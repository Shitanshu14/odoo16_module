# Copyright (C) Softhealer Technologies.

from odoo import models, fields,api
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, ValidationError

class TaskTimeAccountLine(models.Model):
    _name = 'sh.task.time.account.line'
    _description = 'Task Time Account Line'

    def _get_default_start_time(self):
        if self.env.user.task_id:            
            return self.env.user.start_time

    def _get_default_end_time(self):
        return datetime.now()

    def _get_default_task(self):
        if self.env.user.task_id:
            return self.env.user.task_id
    

    def _get_default_duration(self):
        active_model = self.env.context.get('active_model')
        if active_model == 'project.task':
            active_id = self.env.context.get('active_id')
            if active_id:
                task_search = self.env['project.task'].search(
                    [('id', '=', active_id)], limit=1)
                # raise ValidationError(self.env.user.end_time)
                diff = fields.Datetime.from_string(self.env.user.end_time) - fields.Datetime.from_string(self.env.user.start_time)
                if diff:
                    duration = float(diff.days) * 24 + \
                        (float(diff.seconds) / 3600)
                    return round(duration, 2)
    

    name = fields.Text("Description", required=True)
    start_date = fields.Datetime("Start Date", default=_get_default_start_time)
    end_date = fields.Datetime("End Date", default=_get_default_end_time)
    # duration = fields.Float(string='Duration (HH:MM)', readline=True)
    call_on = fields.Float(string='Duration (HH:MM)', readline=True)
    task_id = fields.Many2one('project.task', string='Task', default=_get_default_task, readonly=True)
    desc_option_id = fields.Many2one('task.timer.description', string="Description")
    minute_count= fields.Integer(string='Duration in Minutes')
    manual_duration = fields.Boolean(string="Enter Duration Manually")

    @api.onchange('desc_option_id')
    def add_description(self):
        if self.name:
            self.write({'name': f"{self.name} {self.desc_option_id.name}"})
        else:
            self.write({'name': self.desc_option_id.name})

    @api.onchange('start_date', 'end_date', 'minute_count')
    def _onchange_dates_or_minutes(self):
        for record in self:
            if record.end_date and record.minute_count:
                end_date = fields.Datetime.from_string(record.end_date)
                minute_count = record.minute_count

                record.start_date = end_date - timedelta(minutes=minute_count)
                record.call_on = minute_count / 60
            elif record.start_date and record.end_date:
                start_date = fields.Datetime.from_string(record.start_date)
                end_date = fields.Datetime.from_string(record.end_date)

                duration_seconds = (end_date - start_date).total_seconds()
                hours = duration_seconds // 3600
                minutes = (duration_seconds % 3600) // 60

                record.call_on = hours + (minutes / 60)
            else:
                record.call_on = 0.0
        # for record in self:
        #     if record.start_date and record.end_date:
        #         start_date = record.start_date
        #         end_date = record.end_date

        #         duration_seconds = (end_date - start_date).total_seconds()
        #         hours, remainder = divmod(duration_seconds, 3600)
        #         minutes, seconds = divmod(remainder, 60)

        #         record.call_on = hours + (minutes / 60)
        #     else:
        #         record.call_on = False
                
    def end_task(self):
        self.env.user.write({'end_time': self.end_date})
        context = dict(self.env.context or {})
        active_model = context.get('active_model', False)
        active_id = context.get('active_id', False)
        vals = {'name': self.name,
                'unit_amount': self.call_on,
                'amount': self.call_on,
                'date': datetime.now(),
                'start_date': self.start_date
                }

        if active_model == 'project.task':
            if active_id:
                task_search = self.env['project.task'].search([('id', '=', active_id)], limit=1)
                print('Task:-', task_search)
                if task_search:
                    vals.update({'end_date': self.end_date})
                    vals.update({'task_id': task_search.id})
                    if task_search.project_id:
                        vals.update({'project_id': task_search.project_id.id})
                        act_id = self.env['project.project'].sudo().browse(task_search.project_id.id).analytic_account_id
                        if act_id:
                            vals.update({'account_id': act_id.id})
                    task_search.sudo().write({'start_time': None,'task_running': False, 'task_runner':False})
        timesheet_line = self.env['account.analytic.line'].sudo().search([('task_id', '=', task_search.id),
                                                                          ('employee_id.user_id','=', self.env.uid),
                                                                          ('end_date', '=', False)], limit=1)
        if timesheet_line:
            timesheet_line.write(vals)
        self.sudo()._cr.commit()
        self.env.user.write({'task_id': False})

        return {'type': 'ir.actions.client', 'tag': 'reload'}
    
    def action_mark_done_task(self):
        # Check if any user is currently working on this task
        users = self.env['res.users'].search([('task_id.id', '=', self.task_id.id)])

        # End the task timer if someone is working
        if users:
            self.end_task()  # Ensure the end_task method is correctly implemented

        # Retrieve the associated project task
        task = self.env['project.task'].search([('id', '=', self.task_id.id)], limit=1)

        if not task:
            raise UserError("Task not found!")
        # Get the 'Done' stage
        # done_stage = self.env['project.task.type'].search([('name', '=', 'Done')], limit=1)
        done_stage = self.env['project.task.type'].search([('name', '=', 'Done'),('fold', '=', True)], limit=1)
        # Update the stage_id of the project.task
        task.write({'stage_id': done_stage.id})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

