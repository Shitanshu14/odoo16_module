# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class TrainingCenter(models.Model):
    _name = "emp.training.center"
    _description = 'Training Center'

    name = fields.Char(
        string='Name',
        required=True
    )
    code = fields.Char(
        string='Code',
        required=True
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Training Center Location'
        ,required=True
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: