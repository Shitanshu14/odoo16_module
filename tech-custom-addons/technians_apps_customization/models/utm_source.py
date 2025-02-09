# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, models, fields
from odoo.exceptions import UserError
class UtmSource(models.Model):
    _inherit = 'utm.source'
    lead_count = fields.Integer(string="Leads Count" ,compute="_compute_lead_count")
    sale_order_count = fields.Integer(string="SO Count" ,compute="_compute_sale_order_count")
    invoice_count = fields.Integer(string="Invoice Count" ,compute="_compute_invoice_count")
    contact = fields.Integer(string="Contacts Count" , compute="_compute_contact_count")
    applicants= fields.Integer(string="Applicants Count" ,compute="_compute_applicants_count")


    @api.depends('name')
    def _compute_lead_count(self):
        for rec in self:
            rec.lead_count = self.env['crm.lead'].search_count([('source_id','=', rec.id)])
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = self.env['sale.order'].search_count([('source_id','=',record.id)])
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([('source_id','=',rec.id)])

    def _compute_contact_count(self):
        for rec in self:
            rec.contact = self.env['res.partner'].search_count([('contact_hc_source_id', '=', rec.id)])

    def _compute_applicants_count(self):
        for rec in self:
            rec.applicants = self.env['hr.applicant'].search_count([('source_id', '=', rec.id)])



