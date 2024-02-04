const express = require('express')
const router = express.Router();
const controllers = require('./controller');
const verify_session = require('../../middlewares/verify_session');

// BASE ROUTE /role

// Create a Connection
router.get('/', verify_session(), controllers.getAllRoles);

module.exports = router;