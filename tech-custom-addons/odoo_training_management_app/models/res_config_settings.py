from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    project_id = fields.Many2one("project.project",config_parameter = 'odoo_training_management_app.project_id')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['project_id'] = int(
            self.env['ir.config_parameter'].sudo().get_param('emp.training.application.project_id', default=0))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('emp.training.application.project_id', self.project_id.id)



