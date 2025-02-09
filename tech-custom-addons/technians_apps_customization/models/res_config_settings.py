from odoo import api, fields, models
import ast

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_tag_ids = fields.Many2many('lead.status', string='Tags')


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        crm_tag_ids = self.env['ir.config_parameter'].sudo().get_param('technians_apps_customization.crm_tag_ids', default=[])
        res.update(
            crm_tag_ids=ast.literal_eval(crm_tag_ids) if crm_tag_ids else [],
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('technians_apps_customization.crm_tag_ids', self.crm_tag_ids.ids or [])
