# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_product_subscription_available = fields.Boolean(compute="compute_is_product_subscription_available", string='Is Product Subscription Available ?')
    is_subscription = fields.Boolean(string='Subscription Line?')
    subscription_id = fields.Many2one('subscription.subscription', string='Subscription', copy=False)
    purchase_option = fields.Selection([('subscription', 'Subscription'), ('one_time_purchase', 'One Time Purchase')], 'Purchase Option', default='one_time_purchase', required=True)
    subscription_line_id = fields.Many2one('subscription.line', string='Subscription Line')
    subscription_interval = fields.Many2one('subscription.intervals', string='Subscription Intervals')

    def _prepare_subscription_line_values(self, subscription):
        self.ensure_one()
        recurring_rule_type = self.subscription_interval.recurring_rule_type
        recurring_interval = self.subscription_interval.recurring_interval
        new_date = datetime.date.today() + self.env['subscription.subscription'].get_relative_delta(recurring_rule_type, recurring_interval)
        return {
            'partner_id': self.order_id.partner_id.id,
            'product_id': self.product_id.id,
            'name': self.name,
            'quantity': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'price_unit': self.price_unit,
            'discount': self.discount,
            'date_start': fields.Date.context_today(self),
            'duration_cycle': 'unlimited',
            'subscription_interval': self.subscription_interval.id,
            'recurring_next_date': new_date or fields.Date.context_today(self),
            'subscription_id': subscription.id,
            'sale_order_line_ids': [(4, self.id)],
            'tax_id': [(6, 0, self.tax_id.ids)],
            'state': 'draft'
        }

    def create_subscription_line(self, subscription):
        subscription_line_model = self.env['subscription.line']
        subscription_line = self.env['subscription.line']
        for rec in self:
            subscription_line_values = rec._prepare_subscription_line_values(subscription)
            new_subscription_line = subscription_line_model.create(subscription_line_values)
            subscription_line |= new_subscription_line
        return subscription_line

    @api.constrains('subscription_id')
    def _check_subscription_sale_partner(self):
        for rec in self:
            if rec.subscription_id:
                if rec.order_id.partner_id != rec.subscription_id.partner_id:
                    raise ValidationError(_("Sale order and subscription should be linked to the same partner"))

    @api.depends('product_id')
    def compute_is_product_subscription_available(self):
        for rec in self:
            self.is_product_subscription_available = False
            if rec.product_id:
                if self.product_id.is_subscription:
                    self.is_product_subscription_available = True
                else:
                    self.is_subscription = False
                    self.purchase_option = 'one_time_purchase'

    @api.onchange('is_product_subscription_available')
    def onchange_is_product_subscription_available(self):
        if not self.is_product_subscription_available:
            self.is_subscription = False
            self.purchase_option = 'one_time_purchase'

    @api.onchange('purchase_option')
    def purchase_option_change(self):
        if self.purchase_option:
            if self.purchase_option == 'subscription':
                self.is_subscription = True
            else:
                self.is_subscription = False

    @api.onchange('product_id', 'purchase_option')
    def onchange_subscription_interval(self):
        return {'domain': {
            'subscription_interval': [('id', 'in', self.product_id.mapped('subscription_intervals').ids)]
        }}
