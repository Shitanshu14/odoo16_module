# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_subscription = fields.Boolean(string='Subscription Order?', compute='_compute_is_subscription')
    subscription_count = fields.Integer(compute='_compute_subscription_count')

    @api.depends('order_line.is_subscription')
    def _compute_is_subscription(self):
        for order in self:
            order.is_subscription = False
            if order.order_line:
                order.is_subscription = any(order.order_line.mapped('is_subscription'))

    @api.depends("order_line")
    def _compute_subscription_count(self):
        for rec in self:
            rec.subscription_count = len(rec.order_line.mapped('subscription_id'))

    def _prepare_subscription_value(self, order_lines):
        self.ensure_one()
        return {
            'code': self.name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'auto_recurring_payment': True,
            'payment_token_id': self._get_token_from_payments(),
            'pricelist_id': self.pricelist_id.id,
        }

    def _get_token_from_payments(self):
        self.ensure_one()
        last_token = self.transaction_ids._get_last().token_id.id
        if last_token:
            return last_token
        return False

    def action_create_subscription(self, order_lines):
        subscriptions = self.env['subscription.subscription']
        for rec in self.filtered('is_subscription'):
            line_to_update_subscription = order_lines.filtered(
                lambda r: r.subscription_id and r.product_id.is_subscription and r
                not in r.subscription_id.subscription_line_ids.mapped('sale_order_line_ids') and r.is_subscription
            )
            subscription_values = rec._prepare_subscription_value(order_lines)
            subscription = self.env['subscription.subscription'].create(subscription_values)
            subscriptions |= subscription
            subscription_order_lines = order_lines.filtered('is_subscription')
            if subscription_order_lines:
                subscription_order_lines.create_subscription_line(subscription)
                subscription_order_lines.write({'subscription_id': subscription.id})
            for line in line_to_update_subscription:
                line.create_subscription_line(line.subscription_id)
        return subscriptions

    def action_confirm(self):
        if not self.env.context.get('subscription_to_sale'):
            subscriptions = self.filtered(lambda order: (order.is_subscription)).action_create_subscription(self.order_line)
            subscriptions.subscription_line_ids.action_start_subscription()
        return super(SaleOrder, self).action_confirm()

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for rec in self:
            rec.order_line.mapped('subscription_id').filtered(lambda r: r.active).mapped('subscription_line_ids').action_close_subscription()
        return res

    def action_open_subscriptions(self):
        self.ensure_one()
        action = self.env.ref("subscription_kanak.action_subscription").read()[0]
        subscription_lines = self.env['subscription.line'].search([('sale_order_line_ids', 'in', self.order_line.ids)])
        subscriptions = subscription_lines.mapped('subscription_id')
        action["domain"] = [("id", "in", subscriptions.ids)]
        if len(subscriptions) == 1:
            action.update({
                "res_id": subscriptions.id,
                "view_mode": "form",
                "views": filter(lambda view: view[1] == 'form', action['views'])
            })
        return action

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        res = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)

        line = self.order_line.filtered(lambda l: l.id == res.get('line_id'))
        if kwargs.get('subscription_interval'):
            vals = {
                'subscription_interval': int(kwargs['subscription_interval']),
                'is_subscription': True
            }
            line.sudo().write(vals)

        # if line and line.is_subscription and line.product_id.apply_from == '1':
        #     line.sudo().write({'discount': line.product_id.discount_percentage})

        return res
