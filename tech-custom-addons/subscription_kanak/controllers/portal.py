# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo.addons.sale.controllers.portal import CustomerPortal


class SalePortalSubscription(CustomerPortal):
    def _order_get_page_view_values(self, order, access_token, **kwargs):
        res = super(SalePortalSubscription, self)._order_get_page_view_values(
            order=order, access_token=access_token, **kwargs)

        order = res.get('sale_order')
        if order:
            subscription_line_exist = order.order_line.filtered(lambda l: l.is_subscription)

            if subscription_line_exist and res.get('acquirers'):
                # show only s2s payment gateway
                res.update({
                    'acquirers': res.get('acquirers').filtered(lambda acq: acq.payment_flow == 's2s')
                })
        return res
