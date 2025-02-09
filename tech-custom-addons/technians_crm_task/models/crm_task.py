# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, fields, models, _
import logging
from odoo.osv import  osv
from odoo import SUPERUSER_ID


project_name = "Prospect's Work @ Technians"
class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    tech_task_count = fields.Integer(string="Tasks Count")
    def task_count(self):
        task_obj = self.env['project.task']
        self.task_number = task_obj.search_count([('lead_id', 'in', [a.id for a in self])])
        self.tech_task_count = self.task_number
    task_number = fields.Integer(compute='task_count', string='Tasks', stored=True)

    def write(self, vals):
        if vals.get('stage_id'):
            tasks = self.env['project.task'].search([('lead_id','=',self.id)])
            for task in tasks:
                task.write({'lead_status': vals.get('stage_id')})
            # self.remove_this()
        return super(crm_lead, self).write(vals)

    # def remove_this(self):
    #     tasks = self.env['project.task'].search([('lead_id','!=',False)])
    #     for task in tasks:
    #         task.write({'lead_status': task.lead_id.stage_id.id})

class crm_task_wizard(models.TransientModel):
    _name = 'crm.task.wizard'
    _description = "CRM Task Wizard"
    
    
    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        lead_name = crm_brw.name or ''
        contact_name = crm_brw.partner_id.display_name or ''
        company_name = crm_brw.partner_name or ''
        task_title = lead_name + ' ' + contact_name + ' ' + company_name
        return task_title
    
    def _default_project(self):
        #  return self.env['project.project'].search([('name', '=', "Prospect's Work @ Technians")], limit=1).id
         return self.env['project.project'].search([('id', '=', 17)], limit=1).id
   
    def _set_deadline(self):
        Next_Date = datetime.today() + timedelta(days=3)
        return Next_Date.strftime ('%Y-%m-%d')
    project_id = fields.Many2one('project.project','Project',default=_default_project)
    dead_line = fields.Date('Deadline',default=_set_deadline)
    name = fields.Char('Task Name',default = get_name)
    user_ids = fields.Many2many('res.users','Assignees',default=lambda self: self.env.uid,
        index=True)
    user_ids = fields.Many2many('res.users', relation='project_task_assignee_rel', column1='task_id', column2='user_id',
        string='Assignees', default=lambda self: self.env.user)
    description = fields.Html(string='Description')
    project_name = "Prospect's Work @ Technians"
    task_stage_id = fields.Many2one('project.task.type',string='Task Type', domain=[('project_ids', 'in', 17)])
    def create_task(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['crm.lead'].browse(active_id)
        
        user = []
        for users in self.user_ids:
            user.append(users.id)
        vals = {'name': self.name,
                'project_id':self.project_id.id or False,
                'user_ids': user or False,
                'date_deadline':  self.dead_line or False,
                'partner_id': crm_brw.partner_id.id or False,
                'lead_id': crm_brw.id or False,
                'description': self.description,
                'stage_id' :self.task_stage_id.id or False,
                'lead_status' :crm_brw.stage_id.id or False
                }
        self.env['project.task'].create(vals)
        
class project_Task(models.Model):
    _inherit='project.task'
    
    lead_id =  fields.Many2one('crm.lead', 'Opportunity')

    lead_status = fields.Many2one('crm.stage')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
