from odoo import api, exceptions, fields, models

class LeadStatus(models.Model):
    _name = 'lead.status'
    name = fields.Char(string="Status Name")
    leads_count = fields.Integer(string='Leads Count', compute='_compute_lead_count')
    color = fields.Integer('Color')

    @api.depends('name')
    def _compute_lead_count(self):
        for record in self:
            record.leads_count = self.env['crm.lead'].search_count([('lead_status_ids', '=', record.id)])

class Tag(models.Model):
    _inherit= "crm.tag"
    _description = "CRM Tag"

    tag_count = fields.Integer(string='Tag Count', compute='_compute_tag_count')

    @api.depends('name')
    def _compute_tag_count(self):
        for record in self:
            record.tag_count = self.env['crm.lead'].search_count([('tag_ids', '=', record.id)])