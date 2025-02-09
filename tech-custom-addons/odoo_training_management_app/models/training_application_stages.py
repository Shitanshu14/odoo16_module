# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TrainingApplicationStage(models.Model):
    _name = "emp.training.application.stage"
    _description = 'Training Application Stage'

    name = fields.Char(
        string='Name',
        required=True
    )
    is_approve = fields.Boolean(
        string='Is Approved?'
    )
    is_cancel = fields.Boolean(
        string='Is Cancelled?'
    )
    is_draft = fields.Boolean(
        string='Is Draft?'
    )
    default_stage = fields.Boolean(
        string='Default Stage'
    )
    fold = fields.Boolean('Folded by Default')
    sequence = fields.Integer()


class TrainingApplicationLineStage(models.Model):
    _name = "emp.training.application.line.stage"
    _description = 'Training Application Line Stage'

    sequence = fields.Integer()

    name = fields.Char(
        string='Name', 
        required=True
    )
    is_draft = fields.Boolean(
        string='Is Draft?'
    )
    default_stage = fields.Boolean(
        string='Default Stage'
    )
    fold = fields.Boolean('Folded by Default')



    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: