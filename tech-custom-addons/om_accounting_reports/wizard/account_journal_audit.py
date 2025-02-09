# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountPrintJournal(models.TransientModel):
    _inherit = "account.print.journal"

    @api.onchange('target_move', 'sort_selection', 'date_from',
                  'date_to', 'journal_ids')
    def onchange_clear(self):
        self.report_details = ''

    def _view_report(self, data):
        data = self._get_report_data(data)
        report_ref = 'accounting_pdf_reports.action_report_journal'
        report_details = self.env.ref('accounting_pdf_reports.action_report_journal').\
            _render_qweb_html(report_ref, self, data=data)[0]
        self.report_details = report_details
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('accounting_pdf_reports.account_report_print_journal_view').id,
            'res_model': self._name,
            'target': 'new',
            'res_id': self.id
        }
