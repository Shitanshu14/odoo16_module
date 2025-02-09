from odoo import fields, models, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Product'
    
    
    projects_count = fields.Integer(compute='compute_projects_count')
    
    def compute_projects_count(self):
        for record in self:
            record.projects_count = self.env['project.project'].search_count([("project_service_ids", "in", self.id)])
            
class search(models.Model):
    _inherit = 'product.product'            
    def get_service_projects(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            "domain": [("project_service_ids", "in", self.id)],
            # 'domain':[('project_services_ids','contains',2)],
            'context': "{'create': False}"
        }