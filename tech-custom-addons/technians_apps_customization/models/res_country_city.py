from odoo import api, exceptions, fields, models

class CountryCity(models.Model):
    _name = 'res.country.city'
    name = fields.Char(string="City")
    city_state_id = fields.Many2one('res.country.state', string = "State")
    city_country_id = fields.Many2one('res.country', string = "Country")