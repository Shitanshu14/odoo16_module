from odoo import api, exceptions, fields, models

class LeadStatus(models.Model):
    _name = 'job.roles'
    name = fields.Char(string="Job Role")