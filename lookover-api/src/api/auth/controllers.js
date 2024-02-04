const firebase = require('firebase-admin');
const prisma = require('../../init/prisma');
const { v4: uuidv4 } = require('uuid');
const fetch = require("node-fetch");

module.exports.checkIfEmailExists = async (req, res) => {
    try {
        const { email } = req.body;

        const if_user = await prisma.user.findFirst({
            where: {
                email
            }
        })

        if (if_user) {
            return res.status(200).send({
                is_new: false,
                message: 'User exists.'
            })
        }

        return res.status(200).send({
            is_new: true,
            message: 'User does not exist.'
        })
    } catch (error) {
        throw error;
    }
}

module.exports.createOrg = async (req, res) => {
    try {
        const { user_name, user_email, org_name, org_description, links, profile_type } = req.body;


        const base_verification = await prisma.base_verification.create({
            data: {
                mode: 'email',
                type: 'org-creation-verification',
                expiresAt: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes
                value: Math.floor(100000 + Math.random() * 900000).toString(), // 6 digit code
                data: { user_name, user_email, org_name, org_description, links, profile_type },
                key: uuidv4().replace(/-/g, '')
            }
        })

        return res.status(200).send({
            device_id: base_verification.key,
            mode: 'email',
            code: base_verification.value,
            message: 'Check Inbox for Verification Code.',
            context_id: base_verification.id
        });

    } catch (error) {
        throw error;
    }
}

module.exports.consumeOrg = async (req, res) => {
    let firebase_backup_flag = 0;
    let firebaseTenant = null;
    try {
        const { context_id, device_id, code } = req.body;

        const if_verification = await prisma.base_verification.findUnique({
            where: {
                id: context_id,
                AND: {
                    key: device_id,
                    AND: {
                        value: code
                    }
                }
            }
        });

        if (!if_verification) {
            return res.status(400).send({
                message: 'Invalid Verification Code'
            })
        }

        // // Check Expiry
        // if (if_verification.expiresAt < new Date()) {
        //     return res.status(400).send({
        //         message: 'Verification Code Expired'
        //     })
        // }

        const { user_name, user_email, org_name, org_description, links, profile_type } = if_verification.data;

        // Create Firebase Tenant
        firebaseTenant = await firebase.auth().tenantManager().createTenant({
            displayName: (org_name.replace(/\s+/g, '-').toLowerCase()).substring(0, 20)
        });

        firebase_backup_flag += 1

        const tenantAuth = await firebase.auth().tenantManager().authForTenant(firebaseTenant.tenantId);

        // Create User in Firebase and Tenant
        const firebaseUser = await tenantAuth.createUser({
            displayName: user_name,
            email: user_email,
            emailVerified: true,
        });

        // Create Organziation with User getting Owner Role

        const organization = await prisma.organization.create({
            data: {
                firebase_tenant_id: firebaseTenant.tenantId,
                name: org_name,
                id: Math.floor(100000000000 + Math.random() * 900000000000).toString(),
                description: org_description,
                links: links,
                profile_type: profile_type,
                user: {
                    create: {
                        id: firebaseUser.uid,
                        name: user_name,
                        email: user_email,
                        user_roles: {
                            create: {
                                roles: {
                                    connect: {
                                        id: 'owner'
                                    }
                                }
                            }
                        }
                    }
                },
            },
            include: {
                user: {
                    include: {
                        user_roles: true
                    }
                },
            }
        });

        


        // await tenantAuth.setCustomUserClaims(firebaseUser.uid, {
        //     roles: ['owner'],
        //     org_id: organization.id,
        // });

        const loginToken = await tenantAuth.createCustomToken(firebaseUser.uid,{
            roles: ['owner'],
            org_id: organization.id,
        })

        return res.status(200).send({
            loginToken
        })

    } catch (error) {
        console.log(process.env.NODE_ENV == 'dev' ? error : `[System]: ${error.message}`);
        if (firebaseTenant) {
            console.log("[System]: Deleting Tenant")
            await firebase.auth().tenantManager().deleteTenant(firebaseTenant.tenantId);
            await prisma.organization.delete({
                where: {
                    firebase_tenant_id: firebaseTenant.tenantId
                }
            })
        }
        return res.status(500).send({ message: error.message });
    }
}

module.exports.signInUp_create = async (req, res) => {
    try {
        const { email, org_id } = req.body;

        const org_data = await prisma.organization.findUnique({
            where: {
                id: org_id,
                AND: {
                    user: {
                        some: {
                            email
                        }
                    }
                }
            }
        });

        if (!org_data) {
            return res.status(401).send({
                message: 'Users not found in Organization.'
            })
        }

        const base_verification = await prisma.base_verification.create({
            data: {
                mode: 'email',
                type: 'user-signinup-verifcation',
                expiresAt: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes
                value: Math.floor(100000 + Math.random() * 900000).toString(), // 6 digit code
                data: { email, org_id: org_data.id },
                key: uuidv4().replace(/-/g, '')
            }
        });

        return res.status(200).send({
            device_id: base_verification.key,
            mode: 'email',
            code: base_verification.value,
            message: 'Check Inbox for Verification Code.',
            context_id: base_verification.id
        });
    } catch (error) {
        throw error;
    }
}


module.exports.signInUp_consume = async (req, res) => {
    try {
        const { device_id, context_id, code } = req.body;

        const if_verification = await prisma.base_verification.findUnique({
            where: {
                id: context_id,
                AND: {
                    key: device_id,
                    AND: {
                        value: code
                    }
                }
            }
        });

        if (!if_verification) {
            return res.status(400).send({
                message: 'Invalid Verification Code'
            })
        }

        // Check Expiry
        if (if_verification.expiresAt < new Date()) {
            return res.status(400).send({
                message: 'Verification Code Expired'
            })
        }

        const { email, org_id } = if_verification.data;

        const org_data = await prisma.organization.findUnique({
            where: {
                id: org_id,
                AND: {
                    user: {
                        some: {
                            email
                        }
                    }
                }
            }
        });

        if (!org_data) {
            return res.status(401).send({
                message: 'Users not found in Organization.'
            })
        }

        const tenantAuth = await firebase.auth().tenantManager().authForTenant(org_data.firebase_tenant_id);

        const firebaseUser = await tenantAuth.getUserByEmail(email);

        const getUserRoles = await prisma.user_roles.findMany({
            where:{
                user_id: firebaseUser.uid
            }
        })

        // Create new Array where only roles are present and not the whole object
        let roleX = getUserRoles.map((item) => item.role)

        const loginToken = await tenantAuth.createCustomToken(firebaseUser.uid,{
            roles: roleX,
            org_id: org_data.id,
        })


        return res.status(200).send({
            loginToken
        });


    } catch (error) {
        console.log(error);
        return res.status(500).send({
            message: error.message
        })
    }
}


module.exports.returnIdToken = async (req, res) => {
    try {
        const { login_token } = req.body;

        const id = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=${process.env.FIREBASE_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: login_token,
                returnSecureToken: true
            })
        }).then(data => data.json());

        return res.status(200).send({
            id_token: id.idToken,
            refresh_token: id.refreshToken,
            expires_in: id.expiresIn,
        });

    } catch (error) {
        return res.status(500).send({
            message: error.message
        });
    }
}

module.exports.returnIdTokenUsingRefreshToken = async (req, res) => {
    try {
        const { refresh_token } = req.body;

        const id = await fetch(`https://securetoken.googleapis.com/v1/token?key=${process.env.FIREBASE_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                refresh_token: refresh_token,
                grant_type: "refresh_token"
            })
        }).then(data => data.json());

        return res.status(200).send({
            id_token: id.id_token,
            refresh_token: id.refresh_token,
            expires_in: id.expires_in,
            user_id: id.user_id,
            project_id: id.project_id,
            token_type: id.token_type
        });

    } catch (error) {
        console.log(error);
        return res.status(500).send({
            message: error.message
        });
    }
}

module.exports.userRoleCheck = async(req,res) => {
    try {
        return res.send({message:"We are getting info."})
    } catch (error) {
        return res.status(500).send({
            message: error.message
        });
    }
}