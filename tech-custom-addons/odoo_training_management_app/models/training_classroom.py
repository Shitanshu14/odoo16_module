# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class TrainingClassRoom(models.Model):
    _name = "emp.training.class.room"
    _description = 'Training Class Room'

    name = fields.Char(
        string='Name',
        required=True
    )
    code = fields.Char(
        string='Code',
        required=True
    )
    training_center_id = fields.Many2one(
        'emp.training.center',
        string='Training Center',
        required=True
    )

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: