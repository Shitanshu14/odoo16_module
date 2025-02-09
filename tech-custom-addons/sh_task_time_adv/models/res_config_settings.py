from odoo import fields, models,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_allow_multi_user = fields.Boolean(
        related='company_id.sh_allow_multi_user', string='Allow Multi User To Start Task', readonly=False)
    timer_end_duration = fields.Float(string='Automatic Task Timer End Time')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            timer_end_duration=self.env['ir.config_parameter'].get_param('sh_task_time_adv.timer_end_duration', default=0.0)
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('sh_task_time_adv.timer_end_duration', self.timer_end_duration)