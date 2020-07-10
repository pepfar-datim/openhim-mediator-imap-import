require('./init');
const fileUpload = require('express-fileupload');

const logger = require('winston');
const config = require('./config');

const express = require('express');
const bodyParser = require('body-parser');
const mediatorUtils = require('openhim-mediator-utils');
const cors = require('cors');
const util = require('./util');
const fs = require('fs');
const path = require('path');
const spawn = require('child_process').spawn;


const buildArgs = function(script) {
  const args = [];

  if (script.arguments) {
    for (let cArg in script.arguments) {
      args.push(cArg);
      if (script.arguments[cArg]) {
        args.push(script.arguments[cArg]);
      }
    }
  }

  return args;
};

const setupEnv = function(script) {
  let env;
  if (script.env) {
    let k;
    env = {};
    for (k in process.env) {
      env[k] = process.env[k];
    }
    for (k in script.env) {
      env[k] = script.env[k];
    }
    return env;
  } else {
    return process.env;
  }
};

const handler = script => function (req, res) {
  let test_mode, format,period,country_code,importId, status;
  const openhimTransactionID = req.headers['x-openhim-transactionid'];
  const scriptCmd = path.join(config.getConf().scriptsDirectory, script.filename)
  const args = buildArgs(script);
  const argsFromRequest =[];


  let out = "";

  if (req.params.period){
    period=req.params.period;
  }
  else if (req.query.period){
    period=req.query.period;
  }
  if (period){
    args.push(("--period"));
    args.push((period));
  }

  if (req.params.country_code){
    country_code=req.params.country_code;
  }
  else if (req.query.country_code){
    country_code=req.query.country_code;
  }
  if (country_code){
    args.push(("--country_code"));
    args.push((country_code));
  }
  if (req.params.importId){
    importId=req.params.importId;
  }
  else if (req.query.importId){
    importId=req.query.importId;
  }
  if (importId){
    args.push(("--bulkImportId"));
    args.push((importId));
  }
  if (!req.query.test_mode) {
    test_mode="False";
  } else {
      test_mode = req.query.test_mode;
  }
  if (req.method == "GET") {
    let contenttype;
    if (req.query.format){
      format = req.query.format.toLowerCase();
    }
    else {
      format="csv";
    }
    if (format === 'json') {
      contenttype = 'application/json';
    }
    else if (format === 'html') {
      contenttype = 'text/html';
    }
    else if (format === 'xml') {
      contenttype = 'application/xml';
    }
    else {
      format = "csv";
      contenttype = 'application/csv';
    }
    args.push(("--format"));
    args.push((format));

    args.unshift(scriptCmd);
    const cmd = spawn('/home/openhim-core/.local/share/virtualenvs/ocl_datim-viNFXhy9/bin/python',args);
    logger.info(`[${openhimTransactionID}] Executing ${scriptCmd} ${args.join(' ')}`);
    const appendToOut = data => out = `${out}${data}`;
    cmd.stdout.on('data', appendToOut);
    cmd.stderr.on('data', appendToOut);

    return cmd.on('close', function(code) {
      logger.info(`[${openhimTransactionID}] Script exited with status ${code}`);
      const outputObject = out;
      if (format) {
        res.set('Content-Type', contenttype);
        if (format === 'csv') {
          res.set('Content-Disposition', 'inline; filename="'+req.params.country_code+'.csv"');
        }
      }
      if (importId){
        console.log(out);
        out=out.replace(/'/g, '"')
        console.log(out);
        var output_check=JSON.parse(out);
        console.log(output_check.status_code);
    }
      return res.status(output_check.status_code).send({
        response: {
          status: code === 0 ? 200 : 500,
          headers: {
            'Access-Control-Allow-Origin' : '*'
          },
          body: out,
        }
      });
  })
}

  if (req.method == "POST") {
    let contentType = req.get('Content-Type');
    console.log('request body');
    console.log(req.body);
    let imapImport='';
    let importPath='';
    if (contentType==="text/csv" || contentType==="text/plain"){
      imapImport = req.body;
      importPath = '/opt/ocl_datim/data/imapImport.csv'
    }
    else if (contentType==="application/json"){
      imapImport = JSON.stringify(req.body);
      importPath = '/opt/ocl_datim/data/imapImport.json'
      console.log('saving json');
    }
    fs.writeFile(importPath, imapImport, (err) => {
      if (err) throw err;
      console.log('imap Request body saved');
  });
  args.push(importPath);
  args.unshift(scriptCmd);
  const cmd = spawn('/home/openhim-core/.local/share/virtualenvs/ocl_datim-viNFXhy9/bin/python',args);
  logger.info(`[${openhimTransactionID}] Executing ${scriptCmd} ${args.join(' ')}`);
    const appendToOut = data => out = `${out}${data}`;
    cmd.stdout.on('data', appendToOut);
    cmd.stderr.on('data', appendToOut);

    return cmd.on('close', function(code) {
      logger.info(`[${openhimTransactionID}] Script exited with status ${code}`);
      res.set('Content-Type', 'application/json+openhim')
      return res.send({
        'x-mediator-urn': config.getMediatorConf().urn,
        status: code === 0 ? 'Successful' : 'Failed',
        response: {
          status: code === 0 ? 202 : 500,
          headers: {
            'content-type': 'application/json',
            'Access-Control-Allow-Origin' : '*'
          },
          body: out,
          timestamp: new Date()
        }
      })
    })
  }
}


let app = null
let server = null

const getAvailableScripts = callback => fs.readdir(config.getConf().scriptsDirectory, callback);

const isScriptNameValid = name => !((name.length === 0) || (name[0] === '.') || (name.indexOf('/') > -1) || (name.indexOf('\\') > -1));

const startExpress = () => getAvailableScripts(function(err, scriptNames) {
  if (err) {
    logger.error(err);
    process.exit(1);
  }

  logger.info(`Available scripts: ${(scriptNames.filter(d => !d.startsWith('.'))).join(', ')}`);

  app = express();

  app.use(cors());

  app.use(bodyParser.text());
  app.use(bodyParser.json());
  app.use(fileUpload());

  if (config.getConf().scripts) {
    for (let script of Array.from(config.getConf().scripts)) {
      (function(script) {
        if (isScriptNameValid(script.filename) && Array.from(scriptNames).includes(script.filename)) {
          if(script.method==="GET"){
            app.get(script.endpoint, handler(script))
          }
          if(script.method==="POST"){
            app.post(script.endpoint, handler(script))
          }
          return logger.info(`Initialized endpoint '${script.endpoint}' for script '${script.filename}'`);
        } else {
          logger.warn(`Invalid script name specified '${script.filename}'`);
          return logger.warn(`Check that this script is located in the scripts directory '${config.getConf().scriptsDirectory}'`);
        }
      })(script);
    }
  }

  server = app.listen(config.getConf().server.port, config.getConf().server.hostname,
    () => logger.info(`[${process.env.NODE_ENV}] ${config.getMediatorConf().name} running on port ${server.address().address}:${server.address().port}`))
  server.timeout = 0
  return server
})

const restartExpress = function () {
  if (server) {
    logger.info('Re-initializing express server ...')
    server.close() // existing connection will still be processed async
    return startExpress() // start server with new config
  }
}

const debugLogConfig = function () {
  if (config.getConf().logger.level === 'debug') {
    logger.debug('Full config:')
    return logger.debug(JSON.stringify(config.getConf(), null, '  '))
  }
};


if (process.env.NODE_ENV !== 'test') {
  logger.info('Attempting to register mediator with core ...')
  config.getConf().openhim.api.urn = config.getMediatorConf().urn

  mediatorUtils.registerMediator(config.getConf().openhim.api, config.getMediatorConf(), function (err) {
    if (err) {
      logger.error(err)
      process.exit(1)
    }

    logger.info('Mediator has been successfully registered')

    const configEmitter = mediatorUtils.activateHeartbeat(config.getConf().openhim.api)

    configEmitter.on('config', function (newConfig) {
      logger.info('Received updated config from core')
      config.updateConf(newConfig)
      debugLogConfig()
      return restartExpress()
    })

    configEmitter.on('error', err => logger.error(err))

    return mediatorUtils.fetchConfig(config.getConf().openhim.api, function (err, newConfig) {
      if (err) { return logger.error(err) }
      logger.info('Received initial config from core')
      config.updateConf(newConfig)
      debugLogConfig()
      return startExpress()
    })
  })
}

exports.app = app;
