const firebase = require('firebase-admin');
const prisma = require('../../init/prisma');
const { v4: uuidv4 } = require('uuid');
const fetch = require("node-fetch");

// Will Create a Connection Entry in DB.
module.exports.createConnection = async(req,res) => {
    try {
        const { name, plugin } = req.body;
        const { org_id } = req.session.user;

        const connection = await prisma.connections.create({
            data:{
                name,
                plugin,
                organization:{
                    connect:{
                        id: org_id
                    }
                }
            }
        });

        return res.send(connection);

    } catch (error) {
        return res.status(500).send({message:error.message});
    }
}

// Will Update the Connection by Adding the Creds.
// The Creds will be tested async-ly inside backend, to check its authenticity.
module.exports.updateConnectionByAddingCreds = async(req,res) => {
    try {
        const { connection_id } = req.body;
        const { org_id } = req.session.user;
        
        // Fetch Connection First
        const connection = await prisma.connections.findUnique({
            where:{
                id: connection_id,
                AND:{
                    org_id
                }
            }
        });
        if(!connection) throw new Error("Connection ID is Invalid or Deleted.");

        // If Connection Found is for AWS --> Update the Creds there.
        if(connection.plugin === "aws"){
            const { access_key_id, secret_access_key, region } = req.body;
            const updatedConnection = await prisma.connections.update({
                where:{
                    id: connection_id,
                    AND:{
                        org_id
                    }
                },
                data:{
                    data:{
                        access_key_id,
                        secret_access_key,
                        region
                    }
                },
                select:{
                    created_at: true,
                    updated_at: true,
                    id: true,
                    name: true,
                    plugin: true
                }
            });

            return res.send({...updatedConnection});
        }

        // If Not AWS, send Error Message
        else{
            throw new Error("Plugin not Supported. Please Contact Help & Support.")
        }        

    } catch (error) {
        console.log(error);
        return res.status(500).send({message:error.message});
    }
}

module.exports.updateConnection = async(req,res) => {
    try {
        const { connection_id, name, plugin } = req.body;
        const { org_id } = req.session.user;

        const connection = await prisma.connections.update({
            where:{
                id: connection_id,
                AND:{
                    org_id
                }
            },
            data:{
                name,
                plugin,
            },
            select:{
                created_at: true,
                updated_at: true,
                id: true,
                name: true,
                plugin: true,
                org_id: true
            }
        });

        return res.send(connection);
    }
    catch (error) {
        return res.status(500).send({message:error.message});
    }
}


module.exports.getListOfConnections = async(req,res) => {
    try {
        const { org_id } = req.session.user;
        const connections = await prisma.connections.findMany({
            where:{
                org_id
            },
            select:{
                name: true,
                id: true,
                org_id: true,
                created_at: true,
                updated_at: true,
                plugin: true
            }   
        });

        return res.send(connections)

    } catch (error) {
        return res.status(500).send({message: error.message});
    }
}

module.exports.getOneConnection = async(req,res) => {
    try {
        const { org_id } = req.session.user;
        const { connection_id } = req.body;
        const connection = await prisma.connections.findFirst({
            where:{
                id: connection_id,
                AND:{
                    org_id
                }
            },
            select:{
                name: true,
                created_at: true,
                id: true,
                org_id: true,
                updated_at: true,
                plugin: true
            }
        });

        return res.send(connection);

    } catch (error) {
        return res.status(500).send({
            message: error.message
        })
    }
}

module.exports.deleteConnection = async(req,res) => {
    try {
        const { connection_id } = req.body;
        const { org_id } = req.session.user;

        const connection = await prisma.connections.delete({
            where:{
                id: connection_id,
                AND:{
                    org_id
                }
            }
        });

        return res.send({message:"Connection Deleted."});

    } catch (error) {
        return res.status(500).send({message:error.message});
    }
}