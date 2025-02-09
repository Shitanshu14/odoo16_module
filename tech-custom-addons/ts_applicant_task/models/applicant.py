from odoo import api, fields, models, tools
from datetime import datetime,timedelta
from odoo.exceptions import ValidationError



class Applicant(models.Model):

    _name = "hr.applicant"
    _description = "Applicant"
    _inherit = ['hr.applicant']

    def name_get(self):
        res = []
        for rec in self:
            name = rec.partner_name
            res.append((rec.id, name))
        return res

    def send_task_wizard(self):
        for record in self:
            if record.email_from:
                ctx = {
                    'default_applicant_id': record.id,
                }
                return {
                    'name': "Send Task to Applicant",
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'applicant.task.wizard',
                    'target': 'new',
                    'context': ctx,
                }
            else:
                raise ValidationError(f"{record.partner_name} do not have an Email!!")


class ApplicantTaskWizard(models.Model):

    _name = "applicant.task.wizard"
    _description = "Applicant Task Wizard"

    @api.model
    def _get_task_ids(self):
        self.ensure_one()
        task_ids = self.env['hr.job'].browse(self.applicant_id.job_id).applicant_task_ids
        return task_ids

    name = fields.Many2one(comodel_name='hr.applicant.task',string='Task')
    applicant_id = fields.Many2one(comodel_name='hr.applicant',string='Applicant')
    description = fields.Text(string='Task Description')
    days = fields.Integer(string='Deadline Ends After')
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', store=True, readonly=True)
    attachment_ids = fields.Many2many(comodel_name='ir.attachment')
    email_content = fields.Html(string='Email')
    email_subject = fields.Char(string='Subject')

    @api.depends('days')
    def _compute_deadline(self):
        for record in self:
            if record.days:
                record.deadline = fields.Date.context_today(record) + timedelta(days=record.days)
            else:
                record.deadline = False

    @api.onchange('applicant_id')
    def _onchange_applicant_id(self):
        if self.applicant_id and self.applicant_id.job_id:
            self.name = False
            return {
                'domain': {
                    'name': ['|',
                         ('id', 'in', self.applicant_id.job_id.applicant_task_ids.ids),
                         ('job_id', '=', False)
                        ]
                }
            }

    @api.onchange('name')
    def _onchange_task(self):
        if self.name:
            if self.name.description:
                self.description = tools.html2plaintext(self.name.description)
            else:
                self.description = False

            if self.name.deadline_days:
                self.days = self.name.deadline_days
            else:
                self.days = False

            self.email_subject = f"Congratulations! You're Moving Forward in the {self.applicant_id.job_id.name} Process || Task Assessment Round"

            task_attachments = self.env['hr.applicant.task'].search([('id','=',self.name.id)])
            if task_attachments:
                self.attachment_ids = [(6, 0, task_attachments.attachment_ids.ids)]
            else:
                self.attachment_ids = [(6, 0, [])]


    @api.onchange('name', 'applicant_id', 'description', 'days', 'email_subject')
    def _onchange_content(self):
        if not self.name or not self.applicant_id:
            self.email_content = False
        else:
            task = self.name
            calculated_deadline = fields.Date.context_today(self) + timedelta(days=self.days)
            deadline_str = calculated_deadline.strftime('%-d %B, %Y') if calculated_deadline else ''

            content = f"""
                      <p>Dear {self.applicant_id.partner_name},<br/></p>
                      <p>We're excited to inform you that you've been shortlisted for the next round of our {self.applicant_id.job_id.name} recruitment process!<br/></p>
                      <p>We appreciate the time and effort you’ve already invested in the application process. As the next step, we would like you to complete a task assessment. This will help us evaluate your skills and fit for the position. Below are the details of the task:<br/><br/></p>
                      <p><strong>Task Overview:</strong><br/></p>
                      <p>{task.name}<br/></p>
                      <p>Description:  {self.description if self.description else ''}</p>
                      <p><strong>Deadline:</strong>  {deadline_str}<br/></p>
                      <p>Feel free to <a href="mailto:{self.env.user.login}">Reach out</a> if you have any questions or need further clarification. We look forward to your response!<br/><br/></p>
                      <p>Good Luck!</p>
                      <p>Best regards,<br/></p>
                      <span>{self.env.user.signature}</span>
                      <p><strong>{self.env.company.name}</strong></p>
                      """
            self.email_content = content


    def send_task(self):
        self.ensure_one()
        applicant = self.applicant_id
        if applicant.email_from:
            task = self.name.name
            subject = self.email_subject
            # subject = f"{applicant.partner_name}, you have been assigned to {task.name}."
            body_html = self.email_content
            if not applicant or not task or not body_html:
                raise ValidationError(f"Cannot Send Task with empty Contents!!")
            else:
                mail_values = {
                    'subject': subject,
                    'body_html': body_html,
                    'email_from': 'erp@dev.technians.com',
                    'email_to': applicant.email_from,
                    'model': 'hr.applicant',
                    'res_id': applicant.id,
                    'attachment_ids': [(6, 0, self.attachment_ids.ids)] if self.attachment_ids.ids else [],
                }

                mail = self.env['mail.mail'].create(mail_values)

                try:
                    mail.send(raise_exception=True)

                    applicant.message_post(
                        body=f"Email sent successfully<br/><br/>Subject: {subject}<br/><br/>{body_html}<br/>",
                        message_type="comment"
                    )

                except Exception as e:
                    raise ValidationError(f"Failed to send email: {str(e)}")
