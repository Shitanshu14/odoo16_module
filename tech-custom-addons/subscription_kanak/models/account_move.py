# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_count = fields.Integer(string="Subscription Count", compute='_get_subscription_count')

    @api.depends('invoice_line_ids.subscription_line_ids')
    def _get_subscription_count(self):
        for move in self:
            sale_orders = move.line_ids.sale_line_ids.order_id
            subscriptions = sale_orders.order_line.mapped('subscription_id')
            move.subscription_count = len(subscriptions)

    def action_view_subscriptions(self):
        self.ensure_one()
        sale_orders = self.line_ids.sale_line_ids.order_id
        subscriptions = sale_orders.order_line.mapped('subscription_id')
        action = self.env["ir.actions.actions"]._for_xml_id("subscription_kanak.action_subscription")
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        elif len(subscriptions) == 1:
            form_view = [(self.env.ref('subscription_kanak.subscription_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscriptions.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
