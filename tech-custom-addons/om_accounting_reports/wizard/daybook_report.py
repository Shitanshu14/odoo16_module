# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountDayBookReport(models.TransientModel):
    _inherit = "account.daybook.report"

    report_details = fields.Html(string="Details", copy=False)

    @api.onchange('date_from', 'date_to', 'target_move', 'journal_ids')
    def onchange_clear(self):
        self.report_details = ''

    def get_html_report(self):
        data = {}
        data['form'] = self.read(['target_move', 'date_from', 'date_to', 'journal_ids', 'account_ids'])[0]
        comparison_context = self._build_comparison_context(data)
        data['form']['comparison_context'] = comparison_context
        report_ref = 'om_account_daily_reports.action_report_day_book'
        report_obj = self.env.ref('om_account_daily_reports.action_report_day_book').with_context(active_model='account.daybook.report', active_ids=self.id)
        report_details = report_obj._render_qweb_html(report_ref, docids=None, data=data)[0]
        self.report_details = report_details
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('om_account_daily_reports.account_report_daybook_view').id,
            'res_model': self._name,
            'target': 'new',
            'res_id': self.id
        }
