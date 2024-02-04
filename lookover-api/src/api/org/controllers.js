const firebase = require('firebase-admin');
const prisma = require('../../init/prisma');

module.exports.getOrgInfo = async(req,res) => {
    try {
        const { org_id } = req.session.user;
        
        const org = await prisma.organization.findUnique({
            where:{
                id: org_id
            }
        });

        return res.send(org)

    } catch (error) {
        return res.status(500).send({
            message: error.message
        })
    }


}