# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_running = fields.Boolean("Task Running")
    task_runner = fields.Char(string="Task Runner")
    start_time = fields.Datetime("Start Time", copy=False)
    end_time = fields.Datetime("End Time", copy=False)
    total_time = fields.Char("Total Time", copy=False)
    # duration = fields.Float('Real Duration', compute='_compute_duration')
    is_user_working = fields.Boolean("Is User working ?", compute='_compute_is_user_working')
    start_task_bool = fields.Boolean("Start Task", compute='_compute_start_task_bool')

    def _compute_start_task_bool(self):
        for rec in self:
            rec.start_task_bool = True
            if self.env.user.task_id.id == rec.id:
                rec.start_task_bool = False

    @api.model
    def get_duration(self, task):
        if task:
            task = self.sudo().browse(int(task))
            if task and self.env.user.start_time:
                diff = fields.Datetime.from_string(
                    fields.Datetime.now()) - fields.Datetime.from_string(self.env.user.start_time)
                if diff:
                    duration = float(diff.days) * 24 + \
                        (float(diff.seconds) / 3600)
                    return diff.total_seconds() * 1000

    def _compute_is_user_working(self):
        for rec in self:
            rec.is_user_working = False
            if rec and rec.timesheet_ids:
                timesheet_line = rec.timesheet_ids.filtered(lambda x: x.task_id.id == rec.id and x.end_date == False and x.start_date != False)
                if timesheet_line:
                    rec.is_user_working = True
                else:
                    rec.is_user_working = False

    # @api.depends('timesheet_ids.unit_amount')
    # def _compute_duration(self):
    #     for rec in self:
    #         rec.duration = 0.0
    #         if rec and rec.timesheet_ids:
    #             timesheet_line = rec.timesheet_ids.filtered(lambda x: x.task_id.id == rec.id and x.end_date == False and x.start_date != False)
    #             if timesheet_line:
    #                 rec.duration = timesheet_line[0].unit_amount

    def action_task_start(self):
        if self.task_running and not self.env.company.sh_allow_multi_user:
            raise UserError(" This task has been already started by another user !")
        if self.env.user.task_id:
            raise UserError("You can not start 2 tasks at same time !")
        self.sudo().start_time = datetime.now()
        # add entry in line

        vals = {'name': '/', 'date': datetime.now()}

        if self:
            vals.update({'start_date': datetime.now()})
            vals.update({'task_id': self.id})

            if self.project_id:
                vals.update({'project_id': self.project_id.id})
                act_id = self.env['project.project'].sudo().browse(
                    self.project_id.id).analytic_account_id

                if act_id:
                    vals.update({'account_id': act_id.id})

        usr_id = self.env.user.id
        if usr_id:
            emp_search = self.env['hr.employee'].search(
                [('user_id', '=', usr_id)], limit=1)

            if emp_search:
                vals.update({'employee_id': emp_search.id})

        self.env['account.analytic.line'].sudo().create(vals)
        self.env.user.write({'task_id': self.id,'start_time': datetime.now()})
        self.write({'task_running': True, 'task_runner': self.env.user.name})
        self.sudo()._cr.commit()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def action_user_task_end(self):
        usr_id = self.env.user
        if usr_id and usr_id.task_id:
            usr_id.task_id.action_task_end()
        return {}

    def action_task_end(self):
        # self.sudo().end_time = datetime.now()
        self.sudo().end_time = self.env.user.end_time
        self.sudo().start_time = self.env.user.start_time
        if self.id != self.env.user.task_id.id:
            raise UserError("You cannot End this task !")

        tot_sec = (self.end_time - self.env.user.start_time).total_seconds()
        tot_hours = round((tot_sec / 3600.0), 2)

        self.sudo().total_time = tot_hours
        self.write({'task_running': False})
        return {
            'name': "End Task",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.task.time.account.line',
            'target': 'new',
        }

    # Prevent Marking tasks done if timer is running on it
    def write(self, vals):
        true_stages_obj = self.env['project.task.type'].search([('fold','=',True)]).ids
        stage_id = vals.get('stage_id')

        if stage_id in true_stages_obj:
            stage_name = self.env['project.task.type'].search([('id','=',stage_id)]).name
            users = self.env['res.users'].search([('task_id.id','=',self.id)])

            if users:
                raise UserError(f"Cannot Mark Task {stage_name} someone is working on it!")

        return super(ProjectTask, self).write(vals)

