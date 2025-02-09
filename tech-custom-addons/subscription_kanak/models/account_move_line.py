# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    subscription_line_ids = fields.Many2many(
        'subscription.line',
        'subscription_line_invoice_rel',
        'invoice_line_id', 'subscription_line_id',
        string='Subscription Lines', readonly=True, copy=False)
