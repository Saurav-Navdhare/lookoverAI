const firebase = require('firebase-admin');
const prisma = require('../../init/prisma');
const { v4: uuidv4 } = require('uuid');
const fetch = require("node-fetch");


// Get all Available Roles in the System
module.exports.getAllRoles = async(req,res) => {
    try {
        const roles = await prisma.roles.findMany();
        return res.send(roles);
    } catch (error) {
        return res.status(500).send({message:error.message});
    }
} 



