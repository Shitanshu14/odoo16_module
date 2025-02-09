from odoo import api, fields, models, tools


class Job(models.Model):

    _name = "hr.job"
    _description = "Job Position"
    _inherit = ['hr.job']

    # project_id = fields.Many2one(comodel_name='project.project')



    # task_ids = fields.Many2many(comodel_name='project.task', string='Tasks',domain=lambda self: [('project_id', '=', self._get_project_id())])
    applicant_task_ids = fields.Many2many('hr.applicant.task')




class HrApplicantTask(models.Model):

    _name = "hr.applicant.task"
    _description = "Applicant Task"


    # @api.model
    # def _get_project_id(self):
    #     project_id = self.env['ir.config_parameter'].sudo().get_param('ts_applicant_task.project_id', default=False)
    #     return int(project_id) if project_id else False


    # @api.onchange('name')
    # def _onchange_task(self):
    #     task_attachments = self.env['ir.attachment'].search([
    #         ('res_model', '=', 'project.task'),
    #         ('res_id', '=', self.name.id)
    #     ])
    #     if task_attachments:
    #         self.attachment_ids = [(6, 0, task_attachments.ids)]
    #     else:
    #         self.attachment_ids = [(6, 0, [])]

    # name = fields.Many2one(comodel_name='project.task',string='Task',domain=lambda self: [('project_id', '=', self._get_project_id())])
    name = fields.Char(string='Applicant Task')
    job_id = fields.Many2many(comodel_name='hr.job')
    description = fields.Html(string='Description')
    deadline_days = fields.Integer(string='Days to Complete')
    attachment_ids = fields.Many2many(comodel_name='ir.attachment')


    def write(self, vals):
        res = super(HrApplicantTask, self).write(vals)
        if 'job_id' in vals and vals['job_id']:
            for job in self.job_id:
                job.applicant_task_ids = [(4, self.id)]
        return res

    @api.model
    def create(self, vals):
        res = super(HrApplicantTask, self).create(vals)
        if 'job_id' in vals and vals['job_id']:
            for job in res.job_id:
                job.applicant_task_ids = [(4, res.id)]
        return res


