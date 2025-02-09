from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    project_id = fields.Many2one('project.project', string='Project')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        project_id = self.env['ir.config_parameter'].sudo().get_param('ts_applicant_task.project_id', default=False)
        res.update(
            project_id=int(project_id) if project_id else False
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ts_applicant_task.project_id', self.project_id.id or False)
