# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import models, fields


class product_template(models.Model):
    _inherit = "product.template"

    is_subscription = fields.Boolean('Can be Subscribed')
    subscription_intervals = fields.Many2many('subscription.intervals', string='Subscription Intervals')
