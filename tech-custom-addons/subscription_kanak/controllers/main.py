# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import http
from odoo.http import request


class sale_subscription(http.Controller):

    payment_succes_msg = 'message=Thank you, your payment has been validated.&message_class=alert-success'
    payment_fail_msg = 'message=There was an error with your payment, please try with another payment method or contact us.&message_class=alert-danger'

    # 3DS controllers
    # transaction began as s2s but we receive a form reply
    @http.route(['/my/subscription/<sub_uuid>/payment/<int:tx_id>/accept/',
                 '/my/subscription/<sub_uuid>/payment/<int:tx_id>/decline/',
                 '/my/subscription/<sub_uuid>/payment/<int:tx_id>/exception/'], type='http', auth="public", website=True)
    def payment_accept(self, sub_uuid, tx_id, **kw):
        Subscription = request.env['contract.contract']
        tx_res = request.env['payment.transaction']

        subscription = Subscription.sudo().search([('uuid', '=', sub_uuid)])
        tx = tx_res.sudo().browse(tx_id)

        tx.form_feedback(kw, tx.acquirer_id.provider)

        get_param = self.payment_succes_msg if tx.renewal_allowed else self.payment_fail_msg

        return request.redirect('/my/subscription/%s/%s?%s' % (subscription.id, sub_uuid, get_param))
