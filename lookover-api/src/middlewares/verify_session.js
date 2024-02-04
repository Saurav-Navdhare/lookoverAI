// This function is used as Express middleware to check if the Request has Bearer token inside the Authorization header.
// The Bearer token then will be verified using Firebase Admin SDK.
// If the token is valid, the user will be added to the Request object in session user property.
// If the token is invalid, the user will be added to the Request object in session user property as null.

const firebaseAdmin = require('firebase-admin');
const prisma = require('../init/prisma');

function checkStatus(requiredPermissions, UsersPermission) {
    return requiredPermissions.every(requiredPermission => {
      const hasPermission = UsersPermission.some(permission => {
        if (permission.endsWith(':*')) {
          const prefix = permission.slice(0, -2);
          return requiredPermission.startsWith(prefix);
        } else {
          return permission === requiredPermission;
        }
      });
      return hasPermission;
    });
}

const verifyAccess = async (user,requiredPermissions) => {  
    try {
        const userRoles = user.roles;
        const userPermssison =( await prisma.roles.findFirst({
            where:{
                id: userRoles[0]
            },
            select:{
                permissions: true
            }
        })).permissions;
        return checkStatus(requiredPermissions,userPermssison);
    } catch (error) {
        throw error;
    }

}

const verifySession = (requiredPermissions=[]) => async (req, res, next) => {
    try {
        let force = true;
        // if(requiredPermissions.length > 0){
        //     force = true;
        // }
        if (!req.headers.authorization) {
            req.session.user = null;
            if(!force) return next();
            throw new Error("Token not Found");
        }
        const idToken = req.headers.authorization.split(' ')[1];
        const decodedToken = await firebaseAdmin.auth().verifyIdToken(idToken);
        const checkAccess = await verifyAccess(decodedToken,requiredPermissions);
        if(checkAccess){
            req.session.user = decodedToken;
            return next();
        }else{
            throw new Error("Access Denied!!")
        }
        
    } catch (error) {
        req.session.user = null;
        // if(force) return next();
        console.log(error)
        return res.status(401).send({
            message: error.message
        });
    }
}

module.exports = verifySession;