from odoo import models, fields

class HrJob(models.Model):
    _inherit = 'hr.job'

    website_job_id = fields.Char(string='Website Job ID')