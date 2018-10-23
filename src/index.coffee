require './init'
fileUpload = require 'express-fileupload'

logger = require 'winston'
config = require './config'

express = require 'express'
bodyParser = require 'body-parser'
mediatorUtils = require 'openhim-mediator-utils'
cors = require 'cors'
util = require './util'
fs = require 'fs'
path = require 'path'
spawn = require('child_process').spawn



buildArgs = (script) ->
  args = []

  if script.arguments
    for cArg of script.arguments
      args.push cArg
      if script.arguments[cArg]
        args.push script.arguments[cArg]

  return args

setupEnv = (script) ->
  if script.env
    env = {}
    for k of process.env
      env[k] = process.env[k]
    for k of script.env
      env[k] = script.env[k]
    env
  else
    process.env

handler = (script) -> (req, res) ->
  openhimTransactionID = req.headers['x-openhim-transactionid']
  country_code= req.query.country_code
  out = ""
  
  imapImport = req.files.imapImport
  console.log req.files.imapImport
  `imapImport.mv('/opt/openhim-imap-import/imapImport.csv', function(err) {
    if (err)
      return res.status(500).send(err);
  });`
  period= req.query.period
  country_name=req.query.country_name
  unless req.query.test_mode
    test_mode="False"
  else
    test_mode= req.query.test_mode
  importScript = path.join config.getConf().scriptsDirectory, script.filename
  asyncImportScript = path.join config.getConf().scriptsDirectory, 'import_util.py'
  args = buildArgs script
  argsFromRequest = [asyncImportScript, importScript, country_code, period, "/opt/openhim-imap-import/imapImport.csv", country_name, test_mode]
  cmd = spawn 'python', argsFromRequest
  logger.info "[#{openhimTransactionID}] Executing #{asyncImportScript} #{args.join ' '}"
  appendToOut = (data) -> out = "#{out}#{data}"
  cmd.stdout.on 'data', appendToOut
  cmd.stderr.on 'data', appendToOut

  cmd.on 'close', (code) ->
    logger.info "[#{openhimTransactionID}] Script exited with status #{code}"

    res.set 'Content-Type', 'application/json+openhim'
    outputObject = JSON.parse(out)
    res.send {
      'x-mediator-urn': config.getMediatorConf().urn
      status: if code == 0 then 'Successful' else 'Failed'
      response:
        status: if code == 0 then outputObject.status_code else 500
        headers:
          'content-type': 'text/plain'
          'Access-Control-Allow-Origin' : '*'
        body: if code == 0 then outputObject.id else out
        timestamp: new Date()
    }

    


# Express

app = null
server = null


getAvailableScripts = (callback) -> fs.readdir config.getConf().scriptsDirectory, callback

isScriptNameValid = (name) -> not (name.length is 0 or name[0] is '.' or name.indexOf('/') > -1 or name.indexOf('\\') > -1)

startExpress = ->
  getAvailableScripts (err, scriptNames) ->
    if err
      logger.error err
      process.exit 1

    logger.info "Available scripts: #{(scriptNames.filter (d) -> not d.startsWith '.').join ', '}"

    app = express()

    app.use cors()

    app.use bodyParser.json()
    app.use fileUpload()

    if config.getConf().scripts
      for script in config.getConf().scripts
        do (script) ->
          if isScriptNameValid(script.filename) and script.filename in scriptNames
            app.post script.endpoint, handler(script)
            logger.info "Initialized endpoint '#{script.endpoint}' for script '#{script.filename}'"
          else
            logger.warn "Invalid script name specified '#{script.filename}'"
            logger.warn "Check that this script is located in the scripts directory '#{config.getConf().scriptsDirectory}'"

    server = app.listen config.getConf().server.port, config.getConf().server.hostname, ->
      logger.info "[#{process.env.NODE_ENV}] #{config.getMediatorConf().name} running on port #{server.address().address}:#{server.address().port}"
    server.timeout = 0

restartExpress = ->
  if server
    logger.info "Re-initializing express server ..."
    server.close() # existing connection will still be processed async
    startExpress() # start server with new config


debugLogConfig = ->
  if config.getConf().logger.level is 'debug'
    logger.debug 'Full config:'
    logger.debug JSON.stringify config.getConf(), null, '  '


if process.env.NODE_ENV isnt 'test'
  logger.info 'Attempting to register mediator with core ...'
  config.getConf().openhim.api.urn = config.getMediatorConf().urn

  mediatorUtils.registerMediator config.getConf().openhim.api, config.getMediatorConf(), (err) ->
    if err
      logger.error err
      process.exit 1

    logger.info 'Mediator has been successfully registered'

    configEmitter = mediatorUtils.activateHeartbeat config.getConf().openhim.api

    configEmitter.on 'config', (newConfig) ->
      logger.info 'Received updated config from core'
      config.updateConf newConfig
      debugLogConfig()
      restartExpress()

    configEmitter.on 'error', (err) -> logger.error err

    mediatorUtils.fetchConfig config.getConf().openhim.api, (err, newConfig) ->
      return logger.error err if err
      logger.info 'Received initial config from core'
      config.updateConf newConfig
      debugLogConfig()
      startExpress()


exports.app = app
