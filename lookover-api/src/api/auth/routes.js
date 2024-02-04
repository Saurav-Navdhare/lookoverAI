const express = require('express')
const router = express.Router();
const controllers = require('./controllers');
const middleware = require('./middlewares');
const verify_session = require('../../middlewares/verify_session');

// Check Routes
router.get('/',(req,res) => {
    return res.send({
        message: "AUTH API is working fine."
    })
});


// Role Check Routes

router.get('/user/roles',verify_session(["org:info"]),controllers.userRoleCheck);

// Org Routes
router.post('/org/create', middleware.orgValidator, controllers.createOrg);
router.post('/org/consume',middleware.consumeValidator, controllers.consumeOrg);

// User Routes
router.post('/user/signinup', middleware.signInUpValidator, controllers.signInUp_create);
router.post('/user/signinup/consume', middleware.consumeValidator, controllers.signInUp_consume);
router.get('/user/signinup/get_idtoken',controllers.returnIdToken);
router.get('/user/refresh/idtoken',controllers.returnIdTokenUsingRefreshToken);

module.exports = router;

