from odoo import models, fields, api

class OrderSection(models.Model):
    _name = 'apps_development.order.section'
    _inherit = ['mail.thread']
    _description = 'Order Section'

    name = fields.Char(string='Name', required=True)
    order_id = fields.Char(string='Order ID', required=True, copy=False, readonly=True, default='New')
    phone_number = fields.Char(string='Phone Number')
    service_provider_id = fields.Many2one(
        'apps_development.service.provider',
        string='Service Provider'
    )
    time_schedule = fields.Datetime(string='Time Schedule')
    partner_id = fields.Many2one('res.partner', string='Partner')
    service_type = fields.Selection([
        ('wash', 'Wash'),
        ('service', 'Service'),
        ('part_change', 'Part Change'),
    ], string='Service Type')
    feedback = fields.Text("Feedback")

    @api.model
    def create(self, vals):
        if vals.get('order_id', 'New') == 'New':
            vals['order_id'] = self.env['ir.sequence'].next_by_code('apps_development.order.section') or 'New'
        return super(OrderSection, self).create(vals)
