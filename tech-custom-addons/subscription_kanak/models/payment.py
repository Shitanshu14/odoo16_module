# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, models


class PaymentToken(models.Model):
    _name = 'payment.token'
    _inherit = 'payment.token'

    def get_linked_records_info(self):
        res = super().get_linked_records_info()
        subscriptions = self.env['subscription.subscription'].search([('payment_token_id', '=', self.id)])
        for sub in subscriptions:
            res.append({
                'description': subscriptions._description,
                'id': sub.id,
                'name': sub.name,
                'url': f'/my/subscription/{sub.id}/{sub.uuid}'
            })
        return res


class PaymentProvider(models.Model):

    _inherit = 'payment.provider'

    @api.model
    def _is_tokenization_required(self, sale_order_id=None, **kwargs):
        if sale_order_id:
            sale_order = self.env['sale.order'].browse(sale_order_id).exists()
            if sale_order.is_subscription or sale_order.order_line.mapped('subscription_id'):
                return True
        return super()._is_tokenization_required(sale_order_id=sale_order_id, **kwargs)
