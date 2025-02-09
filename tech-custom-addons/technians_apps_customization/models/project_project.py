from odoo import fields, models, api
import datetime
from odoo.exceptions import ValidationError
class Project(models.Model):
    _inherit = 'project.project'
    _description = 'Project'
    
    # project_services_ids = fields.Many2many('product.template',string="Services",domain="['&', ('detailed_type', '=', 'service'), ('sale_ok', '=', 1)]",group_by='product_template_attribute_value_ids')
    # project_service_ids = fields.Many2many('product.product',string="Services",domain="['&', ('detailed_type', '=', 'service'), ('sale_ok', '=', 1)]")
    
    
    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        current_time = datetime.date.today()
        if self.partner_id:
            # raise ValidationError("Project Created")
            active_project_count = self.search_count([('partner_id', '=', self.partner_id.id), ('date', '!=', False),
            ('stage_id.fold', '=', False),
            ('date', '>', current_time.strftime('%m-%d-%Y'))])
            self.partner_id.update({'active_projects': active_project_count})

            inactive_project_count = self.search_count([('partner_id', '=', self.partner_id.id), ('date', '!=', False),
            ('stage_id.fold', '=', True), ('date', '<', current_time)])
            self.partner_id.update({'inactive_projects': inactive_project_count})
            return res

    def write(self, vals):
        res = super(Project, self).write(vals)
        current_time = datetime.date.today()
        if self.partner_id:
            active_project_count = self.search_count([('partner_id', '=', self.partner_id.id), ('date', '!=', False),
            ('stage_id.fold', '=', False), ('date', '>', current_time.strftime('%m-%d-%Y'))])
            self.partner_id.update({'active_projects': active_project_count})

            inactive_project_count = self.search_count([('partner_id', '=', self.partner_id.id), ('date', '!=', False),
            ('stage_id.fold', '=', True), ('date', '<', current_time)])
            self.partner_id.update({'inactive_projects': inactive_project_count})

            return res
