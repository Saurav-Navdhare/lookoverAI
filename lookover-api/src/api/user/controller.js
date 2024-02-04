const firebase = require('firebase-admin');
const prisma = require('../../init/prisma');
const { v4: uuidv4 } = require('uuid');
const fetch = require("node-fetch");


// Add User in Organization
module.exports.addUserInOrganization_Create = async(req,res) => {
    try {
        const { email, role_id, name } = req.body;
        const { org_id } = req.session.user;

        // Check if User Already Exists in the Organization
        const user = await prisma.user.findUnique({
            where:{
                email_org_id:{
                    email,
                    org_id
                }
            }
        });

        if(user) throw new Error("User Already Exists in the Organization.");

        // Create User in Base Verification Table
        const base_verification = await prisma.base_verification.create({
            data:{
                mode: "email",
                type: "org-user-add-verification",
                expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3), // 3 Days
                value: Math.floor(100000 + Math.random() * 900000).toString(),
                data: {user_name: name, user_email: email, role_id, org_id},
                key: uuidv4().replace(/-/g, "")
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
        return res.status(500).send({message:error.message});
    }
} 

// Verify User in Organization
module.exports.addUserInOrganization_Verify = async(req,res) => {
    let tenant,userInOrg,firebaseUser;
    try {
        const { device_id, code, context_id } = req.body;
        
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

        if(if_verification.type !== "org-user-add-verification") throw new Error("Invalid Verification Type.");

        // Check if User Already Exists in the Organization
        const checkUser = await prisma.user.findUnique({
            where:{
                email_org_id:{
                    email: if_verification.data.user_email,
                    org_id: if_verification.data.org_id
                }
            }
        });

        if(checkUser) throw new Error("User Already Exists in the Organization.");

        // Get ORG Details
        const organization = await prisma.organization.findUnique({
            where:{
                id: if_verification.data.org_id
            }
        });

        if(!organization) throw new Error("Organization Not Found.");

        // Get Firebase Tenant Auth

        tenant = await firebase.auth().tenantManager().authForTenant(organization.firebase_tenant_id);

        // Create User in Firebase
        firebaseUser = await tenant.createUser({
            email: if_verification.data.user_email,
            emailVerified: true,
            displayName: if_verification.data.user_name
        });

        // Create User in Prisma
        userInOrg = await prisma.user.create({
            data:{
                id: firebaseUser.uid,
                email: firebaseUser.email,
                name: firebaseUser.displayName,
                org_id: organization.id,
                user_roles:{
                    create:{
                        roles:{
                            connect:{
                                id: if_verification.data.role_id
                            }
                        }
                    }
                }
            }
        });

        const loginToken = await tenant.createCustomToken(firebaseUser.uid,{
            roles: [if_verification.data.role_id],
            org_id: organization.id,
        })

        return res.status(200).send({
            message: 'User Added Successfully.',
            loginToken: loginToken
        })


    } catch (error) {

        if(userInOrg){
            await prisma.user.delete({
                where:{
                    id: userInOrg.id
                }
            });

            console.log("[SYSTEM]: Roll Back User Creation in Prisma.")
        }

        if(firebaseUser){
            await tenant.deleteUser(firebaseUser.uid);
            console.log("[SYSTEM]: Roll Back User Creation in Firebase.")
        }

        return res.status(500).send({message:error.message});
    }
}

// User Info in Organization
module.exports.userInfo = async(req,res) => {
    try {
        const { user_id, org_id } = req.session.user;
        const user = await prisma.user.findUnique({
            where:{
                id: user_id,
                AND:{
                    org_id
                }
            },
            include:{
                user_roles: true
            }
        });
        return res.send(user);
    } catch (error) {
        return res.status(500).send({message: error.message});
    }
}

// Update Email
module.exports.userUpdateEmail = async(req,res) => {
    let tenant,firebaseUser,current_email,updateUser;
    let base_verification;
    const { stage } = req.body;
    try {
        const { user_id, org_id } = req.session.user;
        if(stage==="generate"){
            const current_email = (await prisma.user.findUnique({
                where:{
                    id: user_id,
                    AND:{
                        org_id
                    }
                },
                select:{
                    email: true
                }
            })).email;
            base_verification = await prisma.base_verification.create({
                data:{
                    mode: "email",
                    type: "org-user-update-email",
                    expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3), // 3 Days
                    value: Math.floor(100000 + Math.random() * 900000).toString(),
                    data: {user_email: email, org_id,current_email},
                    key: uuidv4().replace(/-/g, "")
                }
            });
            
            return res.send({
                type: "org-user-update-email",
                expiresAt: base_verification.expiresAt,
                context_id: base_verification.id,
                code: base_verification.value,
                message: 'Check Inbox for Verification Code.'
            })
        }
        else if(stage==="consume"){
            const { context_id, code } = req.body; 
            base_verification = await prisma.base_verification.findUnique({
                where:{
                    id: context_id,
                    AND:{
                        type: "org-user-update-email",
                        AND:{
                            value: code
                        }
                    }
                }
            });

            if (!if_verification) {
                return res.status(400).send({
                    message: 'Invalid Verification Code'
                });
            } 
    
            // Check Expiry
            if (if_verification.expiresAt < new Date()) {
                return res.status(400).send({
                    message: 'Verification Code Expired'
                });
            }

            current_email = base_verification.data.current_email;
        
            const organization = await prisma.organization.findUnique({
                where:{
                    id: base_verification.data.org_id
                }
            });

            tenant = await firebase.auth().tenantManager().authForTenant(organization.firebase_tenant_id);

            updateUser = await prisma.user.update({
                where:{
                    email_org_id:{
                        email: base_verification.data.user_email,
                        org_id: organization.id
                    }
                }
            });

            firebaseUser = await tenant.updateUser(updateUser.id,{
                email: base_verification.data.user_email
            })

            return res.send({
                message: "Email Updated Successfully."
            })
        }
        else{
            throw new Error("Invalid Stage.");
        }

    } catch (error) {
        if(stage==="consume"){
            if(firebaseUser){
                await tenant.updateUser(firebaseUser.uid,{
                    email: current_email
                });
                console.log("[SYSTEM]: Roll Back Email Update in Firebase.")
            }

            if(updateUser){
                await prisma.user.update({
                    where:{
                        id: updateUser.id
                    },
                    data:{
                        email: current_email
                    }
                });
                console.log("[SYSTEM]: Roll Back Email Update in Prisma.")
            }
        }
        return res.status(500).send({message: error.message});
    }
}

