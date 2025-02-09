from odoo import models, fields
from datetime import datetime

class QuickCreateTask(models.Model):
    _name = "quick.task.wizard"
    _description = "Create quick task"

    name = fields.Char(string='Task')
    project_id = fields.Many2one('project.project', string='Project',domain="[('stage_id.fold', '=', False)]")
    deadline_date = fields.Date(string='Deadline')
    user_ids = fields.Many2many('res.users', relation='project_quickly_task_user_rel', column1='quickly_task_id',
                                column2='users_id', string='Assignees', context={'active_test': False}, tracking=True)
    task_stage_id = fields.Many2one('project.task.type', string='Stage')
    description = fields.Html(string="Description", )

    def create_project(self):
        task_vals = {
            'name': self.name,
            'project_id': self.project_id.id,
            'date_deadline': self.deadline_date,
            'stage_id': self.task_stage_id.id,
            'description': self.description,
            'user_ids': [(6, 0, self.user_ids.ids)]

        }
        return self.env['project.task'].create(task_vals)

    def save_and_edit_form(self):
        task = self.create_project()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': task.id,
        }

    def save_and_create_new_task(self):
        new_task = self.create_project()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'quick.task.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
    
    def create_and_start_timer(self):
        task = self.create_project()
        self.env['project.task'].sudo().start_time = datetime.now()

        vals = {'name': '/', 'date': datetime.now()}

        id_of_task = task.id,
        if id_of_task:
            vals.update({'start_date': datetime.now()})
            vals.update({'task_id': id_of_task})

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
        self.env.user.write({'task_id': id_of_task,'start_time': datetime.now()})
        self.env['project.task'].write({'task_running': True, 'task_runner': self.env.user.name})
        self.sudo()._cr.commit()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
