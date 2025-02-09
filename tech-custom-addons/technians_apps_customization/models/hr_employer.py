from odoo import api, exceptions, fields, models

class HREmployer(models.Model):
    _name = 'hr.employer'
    name = fields.Char(string="Employer")