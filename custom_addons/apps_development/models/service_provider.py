from odoo import models, fields, api


class ResCountryDistrict(models.Model):
    _name = 'res.country.district'
    _description = 'Country District'

    name = fields.Char(string='District Name', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)


class ServiceProvider(models.Model):
    _name = 'apps_development.service.provider'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Provider'

    name = fields.Char(string='Service Provider Name', required=True)
    contact_name = fields.Char(string='Contact Name')
    phone_number = fields.Char(string='Phone Number')
    email = fields.Char(string='Email Address')
    address = fields.Text(string='Address')

    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        domain="[('country_id', '=', country_id)]"
    )
    district_id = fields.Many2one(
        'res.country.district',
        string='District',
        domain="[('country_id', '=', country_id), ('state_id', '=', state_id)]"
    )
    pincode = fields.Char(string='Pincode')

    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.state_id = False
        self.district_id = False

    @api.onchange('state_id')
    def _onchange_state_id(self):
        self.district_id = False
