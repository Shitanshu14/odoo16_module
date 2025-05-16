from odoo import api, models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    set_sendgrid = fields.Boolean(string='Set SendGrid API')
    api_key = fields.Char(string='API Key')
    auto_sync = fields.Boolean(string='Sync Contact with Sendgrid on Creation')
    delete_sync = fields.Boolean(string='Sync Contact with Sendgrid on Deletion')
    display_warning = fields.Boolean(string='Display Warning for Contact sync with Sendgrid')

    auto_sync_applicant = fields.Boolean(string='Sync Applicant with Sendgrid on Creation')
    delete_sync_applicant = fields.Boolean(string='Sync Applicant with Sendgrid on Deletion')
    display_warning_applicant = fields.Boolean(string='Display Warning for Applicant sync with Sendgrid')

    auto_sync_crm = fields.Boolean(string='Sync CRM Lead with Sendgrid on Creation')
    delete_sync_crm = fields.Boolean(string='Sync CRM Lead with Sendgrid on Deletion')
    display_warning_crm = fields.Boolean(string='Display Warning for CRM Lead sync with Sendgrid')

    contact_send_limit = fields.Integer(string="Contact Send Limit")

    @api.onchange('set_sendgrid')
    def _onchange_sendgrid(self):
        if self.set_sendgrid == False:
            self.api_key = self.auto_sync = self.delete_sync = self.auto_sync_applicant = self.delete_sync_applicant = self.auto_sync_crm = self.delete_sync_crm = self.display_warning = self.display_warning_applicant = self.display_warning_crm = False



    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            set_sendgrid=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.set_sendgrid', default=False),
            api_key=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.api_key', default=''),
            auto_sync=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.auto_sync', default=False),
            delete_sync=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.delete_sync', default=False),
            display_warning=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.display_warning', default=False),

            auto_sync_applicant=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.auto_sync_applicant', default=False),
            delete_sync_applicant=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.delete_sync_applicant', default=False),
            display_warning_applicant=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.display_warning_applicant', default=False),

            auto_sync_crm=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.auto_sync_crm', default=False),
            delete_sync_crm=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.delete_sync_crm', default=False),
            display_warning_crm=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.display_warning_crm', default=False),

            contact_send_limit=self.env['ir.config_parameter'].get_param('ts_sendgrid_sync.contact_send_limit', default=500),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.set_sendgrid', self.set_sendgrid)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.api_key', self.api_key)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.auto_sync', self.auto_sync)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.delete_sync', self.delete_sync)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.display_warning', self.display_warning)

        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.auto_sync_applicant', self.auto_sync_applicant)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.delete_sync_applicant', self.delete_sync_applicant)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.display_warning_applicant', self.display_warning_applicant)

        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.auto_sync_crm', self.auto_sync_crm)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.delete_sync_crm', self.delete_sync_crm)
        self.env['ir.config_parameter'].set_param('ts_sendgrid_sync.display_warning_crm', self.display_warning_crm)

        self.env['ir.config_parameter'].sudo().set_param('ts_sendgrid_sync.contact_send_limit',self.contact_send_limit if self.contact_send_limit else 500)

    