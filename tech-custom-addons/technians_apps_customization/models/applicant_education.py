from odoo import api, exceptions, fields, models

class ApplicantEducation(models.Model):
    _name = 'applicant.education'
    name = fields.Char(string="Education")