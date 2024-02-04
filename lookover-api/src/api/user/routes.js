const express = require('express')
const router = express.Router();
const controllers = require('./controller');
const verify_session = require('../../middlewares/verify_session');

// BASE ROUTE /org/user


// Get User Info in Organization
router.get('/', verify_session(), controllers.userInfo);

// Create a User in Organization
router.post('/add', verify_session(["org:user:create"]), controllers.addUserInOrganization_Create);

// Verify a User in Organization
router.post('/add/verify', controllers.addUserInOrganization_Verify);


// // Update User Email [ Request ]
// router.put('/user/email', verify_session(["org:user:profile:update"]), controllers.userUpdateEmail);

// // Update User Email [ Request ]
// router.put('/user/email', verify_session(["org:user:profile:"]), controllers.userUpdateEmail);


module.exports = router;