from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product'
    
    
    projects_count = fields.Integer(compute='compute_projects_count')
    
    def compute_projects_count(self):
        for record in self:
            variant_ids = record.attribute_line_ids.mapped('value_ids').ids
            # record.projects_count = self.env['project.project'].search_count([("project_service_ids", "in",variant_ids)])
            record.projects_count = len(variant_ids)
            
            
class search(models.Model):
    _inherit = 'product.template'            
    def get_service_projects(self):
        for record in self:
            variant_ids = record.attribute_line_ids.mapped('value_ids').ids
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            "domain": [("project_services_ids", "in", variant_ids)],
            # 'domain':[('project_services_ids','contains',2)],
            'context': "{'create': False}"
        }