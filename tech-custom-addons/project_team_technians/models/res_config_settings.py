from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    archive_stage_ids = fields.Many2many(
        'project.project.stage',
        'res_config_archive_stage_rel',
        'res_config_settings_id',
        'archive_stage_id',
        string="Project Stages to Archive Project Team"
    )
    active_stage_ids = fields.Many2many(
        'project.project.stage',
        'res_config_active_stage_rel',
        'res_config_settings_id',
        'active_stage_id',
        string="Project Stages to Activate Project Team"
    )

    @api.onchange('archive_stage_ids', 'active_stage_ids')
    def _onchange_stage_ids(self):
        archive_stage_ids_domain = [('id', 'not in', self.archive_stage_ids.ids)] if self.archive_stage_ids else []
        active_stage_ids_domain = [('id', 'not in', self.active_stage_ids.ids)] if self.active_stage_ids else []

        return {
            'domain': {
                'archive_stage_ids': active_stage_ids_domain,
                'active_stage_ids': archive_stage_ids_domain,
            }
        }

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_env = self.env['ir.config_parameter'].sudo()

        stage_ids = param_env.get_param('project_team.archive_stage_ids', default='')
        second_stage_ids = param_env.get_param('project_team.active_stage_ids', default='')

        res.update(
            archive_stage_ids=[(6, 0, [int(stage_id) for stage_id in stage_ids.split(',') if stage_id])],
            active_stage_ids=[(6, 0, [int(second_stage_id) for second_stage_id in second_stage_ids.split(',') if second_stage_id])]
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param_env = self.env['ir.config_parameter'].sudo()

        archive_stage_ids = ','.join(map(str, self.archive_stage_ids.ids))
        active_stage_ids = ','.join(map(str, self.active_stage_ids.ids))

        param_env.set_param('project_team.archive_stage_ids', archive_stage_ids)
        param_env.set_param('project_team.active_stage_ids', active_stage_ids)