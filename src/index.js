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
  const {
    country_code
  } = req.query;
  let out = "";
  const {
    imapImport
  } = req.files;
  imapImport.mv('/opt/ocl_datim/data/imapImport.csv', function(err) {
    if (err)
      return res.status(500).send(err);
  });
  const {
    period
  } = req.query;
  const {
    country_name
  } = req.query;
  if (!req.query.test_mode) {
    test_mode="False";
  } else {
    ({
      test_mode
    } = req.query);
  }
  const importScript = path.join(config.getConf().scriptsDirectory, script.filename);
  const asyncImportScript = path.join(config.getConf().scriptsDirectory, 'import_util.py');
  const args = buildArgs(script);
  const argsFromRequest = [asyncImportScript, importScript, country_code, period, "/opt/ocl_datim/data/imapImport.csv", country_name, test_mode];
  const cmd = spawn('python', argsFromRequest);
  logger.info(`[${openhimTransactionID}] Executing ${asyncImportScript} ${args.join(' ')}`);
  const appendToOut = data => out = `${out}${data}`;
  cmd.stdout.on('data', appendToOut);
  cmd.stderr.on('data', appendToOut);

  return cmd.on('close', function(code) {
    logger.info(`[${openhimTransactionID}] Script exited with status ${code}`);

    res.set('Content-Type', 'application/json+openhim');
    if (!req.query.country_code || !req.query.period) {
      res.set('Content-Type', 'application/json+openhim');
      res.send({
        'x-mediator-urn': config.getMediatorConf().urn,
        status: 'Failed',
        response: {
          status: 400,
          headers: {
            'content-type': 'text/plain',
            'Access-Control-Allow-Origin' : '*'
          },
          body: "Both parameters - country_code and period  are required",
          timestamp: new Date()
        }
      });
    }
    const outputObject = JSON.parse(out);
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
          app.post(script.endpoint, handler(script));
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
