# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"

    @api.onchange('target_move', 'display_account', 'sortby', 'initial_balance',
                  'partner_ids', 'date_from',
                  'period_length', 'journal_ids', 'account_ids')
    def onchange_clear(self):
        self.report_details = ''

    def _view_report(self, data):
        records, data = self._get_report_data(data)
        report_ref = 'accounting_pdf_reports.action_report_general_ledger'
        report_details = self.env.ref('accounting_pdf_reports.action_report_general_ledger'). \
            with_context(active_model='account.aged.trial.balance',active_ids=self.id)._render_qweb_html(report_ref, records, data=data)[0]
        self.report_details = report_details
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('accounting_pdf_reports.account_report_general_ledger_view').id,
            'res_model': self._name,
            'target': 'new',
            'res_id': self.id
        }

