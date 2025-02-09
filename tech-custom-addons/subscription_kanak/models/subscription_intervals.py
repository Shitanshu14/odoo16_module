# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class SubscriptionIntervals(models.Model):
    _name = 'subscription.intervals'
    _description = 'Subscription Intervals'
    _order = "recurring_rule_type,recurring_interval"

    name = fields.Char('Name', required=True)
    recurring_rule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')],
                                           string='Interval', required=True, default='monthly')
    recurring_interval = fields.Integer(string="Interval Count", required=True, default=1, help="Invoice every (Days/Week/Month/Year)")

    _sql_constraints = [
        ('recurring_interval_rule_type_uniq', 'unique (recurring_interval, recurring_rule_type)', 'The combination of "Interval" and "Interval Count" must be unique !'),
        ('check_recurring_interval', 'CHECK(recurring_interval >= 1)', 'The Invoice Every field should be 1 or 1+')
    ]
