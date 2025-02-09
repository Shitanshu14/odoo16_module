from odoo import api, fields, models, tools, SUPERUSER_ID
class RecruitmentSource(models.Model):
    _inherit = "hr.applicant.category"

    application_count = fields.Integer( string= "Applicants Count" , compute="_compute_count_appicant")

    @api.depends('name')
    def _compute_count_appicant(self):
        for record in self:
            record.application_count = self.env['hr.applicant'].search_count([('categ_ids','=',record.id)])