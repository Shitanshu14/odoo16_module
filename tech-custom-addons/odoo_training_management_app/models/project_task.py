# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class Task(models.Model):
    _inherit = "project.task"

    custom_application_id = fields.Many2one(
        'emp.training.application',
        string='Application',
        copy=False
    )
    # subject_id = fields.Many2one(
    #     'training.subject',
    #     string='Subject',
    #     copy=False
    # )
    custom_subject_id = fields.Many2one(
        'slide.slide',
        string='Subject',
        copy=False
    )
    custom_application_line_id = fields.Many2one(
        'emp.training.application.line',
        string='Application Line',
        copy=False
    )
    custom_training_start_date = fields.Date(
        string='Training Start Date',
        copy=False
    )
    custom_training_end_date = fields.Date(
        string='Training End Date',
        copy=False
    )
    custom_training_employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        copy=False
    )
    custom_is_application_task = fields.Boolean(
        string='Is Application Task?',
    )

    def action_time_duration(self):
        task_search = self.env['project.task'].search([('id', '=', self.id)], limit=1)
        if not task_search:
            raise UserError("Task not found.")
        completion_time = task_search.custom_subject_id.completion_time if task_search.custom_subject_id else 0

        if completion_time:
            completion_time_hours = completion_time
        else:
            completion_time_hours = 15 / 60.0
        self.env['account.analytic.line'].create({
            'task_id': task_search.id,
            'name': task_search.name,
            'account_id': task_search.project_id.analytic_account_id.id,
            'employee_id': task_search.custom_training_employee_id.id,
            'unit_amount': completion_time_hours,
            'date': fields.Date.today(),
            'project_id': task_search.project_id.id,
        })



class Project(models.Model):
    _inherit = "project.project"

    custom_application_count = fields.Integer(
        compute='_compute_application_counter',
        string="Application Count"
    )

    # @api.multi
    def action_application(self):
        action = self.env.ref('odoo_training_management_app.action_training_application').sudo().read()[0]
        action['domain'] = [('project_id','in', self.ids)]
        return action

    def _compute_application_counter(self):
        for  rec in self:
            rec.custom_application_count = self.env['emp.training.application'].search_count([('project_id', 'in', self.ids)])
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: