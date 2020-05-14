/*
 * decaffeinate suggestions:
 * DS101: Remove unnecessary use of Array.from
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
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
const {
  spawn
} = require('child_process');


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

const handler = script => (function(req, res) {
  let test_mode;
  const openhimTransactionID = req.headers['x-openhim-transactionid'];
  const importScript = path.join(config.getConf().scriptsDirectory, script.filename);
  const args = buildArgs(script);
  const argsFromRequest =[];

  let out = "";
  if (req.method == "GET") {
    if (req.query.importId){
      args.push(("--importId"));
      args.push((req.query.importId));
    }
    else {
      args.push(("--country_code"));
      args.push((req.params.domain));
      args.push(("--period"));
      args.push((req.params.period));
      args.push(("--format"));
      args.push((req.params.format));
    }
    argsFromRequest.push(importScript);
    argsFromRequest = push(args);
    const cmd = spawn('/home/openhim-core/.local/share/virtualenvs/ocl_datim-viNFXhy9/bin/python',argsFromRequest);
    logger.info(`[${openhimTransactionID}] Executing ${asyncImportScript} ${args.join(' ')}`);
    const appendToOut = data => out = `${out}${data}`;
    cmd.stdout.on('data', appendToOut);
    cmd.stderr.on('data', appendToOut);

    return cmd.on('close', function(code) {
      logger.info(`[${openhimTransactionID}] Script exited with status ${code}`);

      const outputObject = out;
      return res.send({
        'x-mediator-urn': config.getMediatorConf().urn,
        status: code === 0 ? 'Successful' : 'Failed',
        response: {
          status: code === 0 ? 200 : 500,
          headers: {
            'content-type': 'application/json'
          },
          body: out,
          timestamp: new Date()
        }
      });
  });
  }
  if (req.method == "POST") {
    args.push(("--country_code"));
    args.push((req.params.domain));
    args.push(("--period"));
    args.push((req.params.period));
    args.push(("--country_name"));
    args.push((req.params.country_name));
    if (!req.query.test_mode) {
      test_mode="False";
    } else {
        test_mode = req.query.test_mode;
    }
    const contentType = request.getHeader('Content-Type');
    const imapImport='';
    const importPath='';
    if contentType==="application/json"
      imapImport = JSON.stringify(req.body);
      importPath = '/opt/ocl_datim/data/imapImport.json'
    else if contentType==="text/csv"
      imapImport = req.body;
      importPath = '/opt/ocl_datim/data/imapImport.csv'
    imapImport.mv(importPath, function(err) {
      if (err)
        return res.status(500).send(err);
    });
    const asyncImportScript = path.join(config.getConf().scriptsDirectory, 'import_util.py');
    argsFromRequest = [asyncImportScript, importScript, country_code, period, importPath, country_name, test_mode];
    const cmd = spawn('/home/openhim-core/.local/share/virtualenvs/ocl_datim-viNFXhy9/bin/python',argsFromRequest);
    logger.info(`[${openhimTransactionID}] Executing ${asyncImportScript} ${args.join(' ')}`);
    const appendToOut = data => out = `${out}${data}`;
    cmd.stdout.on('data', appendToOut);
    cmd.stderr.on('data', appendToOut);

    return cmd.on('close', function(code) {
      logger.info(`[${openhimTransactionID}] Script exited with status ${code}`);

      const outputObject = out;
      return res.send({
        'x-mediator-urn': config.getMediatorConf().urn,
        status: outputObject.status_code === 202  ? 'Successful' : 'Failed',
        response: {
          status: outputObject.status_code,
          headers: {
            'content-type': 'text/plain',
            'Access-Control-Allow-Origin' : '*'
          },
          body: outputObject.status_code === 202 ? outputObject.id : outputObject.result,
          timestamp: new Date()
        }
      });
  });
  });
});




// Express

let app = null;
let server = null;


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

  server = app.listen(config.getConf().server.port, config.getConf().server.hostname, () => logger.info(`[${process.env.NODE_ENV}] ${config.getMediatorConf().name} running on port ${server.address().address}:${server.address().port}`));
  return server.timeout = 0;
});

const restartExpress = function() {
  if (server) {
    logger.info("Re-initializing express server ...");
    server.close(); // existing connection will still be processed async
    return startExpress(); // start server with new config
  }
};


const debugLogConfig = function() {
  if (config.getConf().logger.level === 'debug') {
    logger.debug('Full config:');
    return logger.debug(JSON.stringify(config.getConf(), null, '  '));
  }
};


if (process.env.NODE_ENV !== 'test') {
  logger.info('Attempting to register mediator with core ...');
  config.getConf().openhim.api.urn = config.getMediatorConf().urn;

  mediatorUtils.registerMediator(config.getConf().openhim.api, config.getMediatorConf(), function(err) {
    if (err) {
      logger.error(err);
      process.exit(1);
    }

    logger.info('Mediator has been successfully registered');

    const configEmitter = mediatorUtils.activateHeartbeat(config.getConf().openhim.api);

    configEmitter.on('config', function(newConfig) {
      logger.info('Received updated config from core');
      config.updateConf(newConfig);
      debugLogConfig();
      return restartExpress();
    });

    configEmitter.on('error', err => logger.error(err));

    return mediatorUtils.fetchConfig(config.getConf().openhim.api, function(err, newConfig) {
      if (err) { return logger.error(err); }
      logger.info('Received initial config from core');
      config.updateConf(newConfig);
      debugLogConfig();
      return startExpress();
    });
  });
}


exports.app = app;
