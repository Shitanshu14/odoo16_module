from odoo import api, fields, models
import datetime
from odoo.exceptions import ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'

    # projects_count = fields.Integer(string="Project Count", compute='compute_projects_count', store=True)
    # active_project_count = fields.Integer(string='Active Project', compute='compute_active_project_count', store=True)
    # @api.depends('write_date')
    # def compute_projects_count(self):
    #     for record in self:
    #         record.projects_count = self.env['project.project'].search_count([("partner_id", "=", record.id)])
    #         self.write({'write_date': datetime.now()})
    # def compute_active_project_count(self):
    #     for record in self:
    #         current_time = datetime.datetime.now()
    #         # active_project = self.env['project.project'].search_count([("date", ">=", current_time)])
    #         active_project = self.env['project.task'].search_count([("date_deadline", ">=", current_time)])
    #         if active_project:
    #             record.active_project_count = active_project
    #             raise ValidationError("Active Project")

    @api.model
    def _budget_issues_feedback_cron(self):        
        contacts = self.search([])
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.budget_issues_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def communication_feedback_cron(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.communication_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def feedback_in_general_cron(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.feed_in_general') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def overall_performance_feedback_cron(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.overall_performance_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def quantity_and_quality_feedback_cron(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.quantity_and_quality_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def service_provided_feedback(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.service_provided_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def team_cooperation_feedback_cron(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.team_corporation_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True

    @api.model
    def timelines_and_deadline_feedback(self):  
        contacts = self.search([])        
        for contact in contacts:
            # project = self.env['project.project'].search(['&', ('partner_id', '=', contact.id), ('partner_id', '!=', False)])
            # if project:
            # if contact.email == 'manish.kumar@technians.com' or contact.email == 'gaurav@technians.com': 
            if (contact.active_projects > 0):
                template = self.env.ref('technians_apps_customization.timelines_and_deadlines_issues_feed') #render email template
                template.send_mail(contact.id, force_send=True)
        return True
    
class TechProjects(models.Model):
    _inherit = "project.project"

    @api.model
    def create(self, vals):
        res = super(TechProjects, self).create(vals)        

        all_partners = self.env['res.partner'].search([])
        for partners in all_partners:
            if partners:
                project_active = self.search_count([('partner_id', '=', partners.id), ('stage_id.fold', '=', False)])
                project_inactive = self.search_count([('partner_id', '=', partners.id), ('stage_id.fold', '=', True)])
                partners.write({'inactive_projects': project_inactive, 'active_projects': project_active})
                
        return res

    def write(self, vals):
        res = super(TechProjects, self).write(vals)
       
        all_partners = self.env['res.partner'].search([])
        for partners in all_partners:
            if partners:
                project_active = self.search_count([('partner_id', '=', partners.id), ('stage_id.fold', '=', False)])
                project_inactive = self.search_count([('partner_id', '=', partners.id), ('stage_id.fold', '=', True)])
                partners.write({'inactive_projects': project_inactive, 'active_projects': project_active})      

        return res
