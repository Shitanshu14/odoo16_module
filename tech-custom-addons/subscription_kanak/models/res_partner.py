# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_subscription_count = fields.Integer(compute='_compute_subscription_count', string='Sale Subscriptions')
    subscription_ids = fields.One2many('subscription.subscription', 'partner_id', string="Subscriptions")

    def _compute_subscription_count(self):
        subscription_model = self.env['subscription.subscription']
        for partner in self:
            partner.sale_subscription_count = int(subscription_model.search_count([('partner_id', '=', partner.id)]))

    def action_open_subscriptions(self):
        self.ensure_one()
        action = self.env.ref('subscription_kanak.action_subscription')
        result = action.read()[0]
        result['context'] = {
            'search_default_partner_id': self.id,
            'default_partner_id': self.id,
            'default_pricelist_id': self.property_product_pricelist.id
        }
        return result
