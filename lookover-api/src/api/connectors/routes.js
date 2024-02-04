const express = require('express')
const router = express.Router();
const controllers = require('./controller');
const verify_session = require('../../middlewares/verify_session');

// BASE ROUTE /org/connectors

// Create a Connection
router.post('/', verify_session(["org:connectors:create"]), controllers.createConnection);

// Update a Connection
router.patch('/', verify_session(["org:connectors:update"]), controllers.updateConnection);

// Update a Connection Creds
router.patch('/creds', verify_session(["org:connectors:update"]), controllers.updateConnectionByAddingCreds);

// Delete a Connection
router.delete('/delete', verify_session(["org:connectors:delete"]), controllers.deleteConnection);

// Get All Connections
router.get('/all', verify_session(["org:connectors:read"]), controllers.getListOfConnections);

// Get a Connection
router.get('/', verify_session(["org:connectors:read"]), controllers.getOneConnection);

module.exports = router;