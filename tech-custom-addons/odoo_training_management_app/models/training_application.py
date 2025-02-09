# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date,datetime,timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import base64

class TrainingApplication(models.Model):
    _name = "emp.training.application"
    _description = 'Training Application'
    _rec_name = 'number'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    


    def action_send_card(self):
        template_id = self.env.ref('odoo_training_management_app.tech_application_email_template').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)

        training_report = self.env.ref('odoo_training_management_app.report_training_application')
        data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf(training_report, [self.id], data=None)[0])
        ir_values = {
            'name': 'Training ' + self.display_name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'emp.training.application',
        }
        training_report_attachment_id = self.env[
            'ir.attachment'].sudo().create(
            ir_values)
           
        ctx = {
                    'default_model': 'emp.training.application',
                    'default_res_id': self.id,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'custom_layout': "mail.mail_notification_paynow",
                    'force_email': False,
                    'default_attachment_ids': [(4, training_report_attachment_id.id)]                
            }
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
           
        }




        # send_email = template.send_mail(self.id,force_send = True)
        # if(send_email):

        #     title = _("Mail Sent")
        #     message = _("Mail Sent Successfully!")
        # else:
        #     title = _("Mail not Sent")
        #     message = _("There was an error sending the email")
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': title,
        #         'message': message,
        #         'sticky': False,
        #     }
        # }
    @api.model
    def _default_stage(self):
        stage_id = self.env['emp.training.application.stage'].search([('default_stage','=', True)],limit=1)
        return stage_id



    def _group_expand_stages(self, stages, domain, order):
        return self.env['emp.training.application.stage'].search([])
    application_name = fields.Char(
        string='Application Name',
        required=True
    )
    training_name = fields.Char(
        string='Training Name',
        required=True
    )
    description = fields.Text(
        string='Description'
    )
    create_date = fields.Date(
        string='Create Date',
        required=True,
        default=fields.Date.context_today
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    stage_id = fields.Many2one(
        'emp.training.application.stage',
        string='Stage',
        tracking=True,
        default=_default_stage,
        group_expand='_group_expand_stages',
        index=True
    )
    application_line_ids = fields.One2many(
        'emp.training.application.line',
        'application_id', 
        string='Application Line'
    )






    project_id = fields.Many2one(
        'project.project',
        string='Project',
        default=lambda self: self._default_project(),
        help="Please select a Project From setting Page.",
        store=True
    )
    def _default_project(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('emp.training.application.project_id', default=0))


    number = fields.Char(
        string='Number',
        readonly=True,
        copy=False
    )
    start_date = fields.Date(
        string='Start Date',
        required=True
    )
    end_date = fields.Date(
        string='End Date',
        required=True
    )
    is_approve = fields.Boolean(
        string='Is Approved?',
        related = 'stage_id.is_approve',
        store = True
    )
    is_cancel = fields.Boolean(
        string='Is Canceled?',
        related = 'stage_id.is_cancel',
        store = True
    )
    is_draft = fields.Boolean(
        string='Is Draft?',
        related = 'stage_id.is_draft',
    )
    is_task_created = fields.Boolean(
        string='Is Task Created',
    )
    task_count = fields.Integer(
        compute='_compute_task_counter',
        string="Task Count"
    )

    training_count = fields.Integer(
        compute='_compute_training_counter',

    )

    @api.depends('application_line_ids')
    def _compute_training_counter(self):
        for record in self:
            record.training_count = len(record.application_line_ids)
    # send_button_visible = fields.Boolean(
    #     string='Send Button Visible',compute="_compute_application_stage"
    # )
    
    # @api.depends('stage_id')
    # def _compute_application_stage(self):
    #     for  rec in self:
    #         if(rec.stage_id.is_draft == True):
    #             rec.send_button_visible = False
    #         else:
    #             rec.send_button_visible = True
    
   
    def _compute_task_counter(self):
        for rec in self:
            rec.task_count = self.env['project.task'].search_count([('custom_application_id', 'in', self.ids)])

    @api.model
    def create(self, vals):

        if not vals.get('project_id'):
            default_project_id = self._default_project()
            if default_project_id:
                vals['project_id'] = default_project_id
            else:
                raise UserError(_('Please select a Project before creating a record.'))

        vals['number'] = self.env['ir.sequence'].next_by_code('emp.training.application') 
        stage_id = self.env['emp.training.application.stage'].search([('default_stage','=', True)],limit=1)
        if stage_id:
            vals.update({'stage_id': stage_id.id})
        else:
            raise UserError(_('Please Set Default Stage.'))
        return super(TrainingApplication, self).create(vals)

    def write(self, vals):
        stage_ids = self.env['emp.training.application.stage'].search(['|',('is_approve','=',True),('is_cancel','=',True)]).ids
        if 'stage_id' in vals and vals.get('stage_id') in stage_ids:
            if not self.env.user.has_group('odoo_training_management_app.group_training_user') and not self.env.user.has_group('odoo_training_management_app.group_training_manager'):
                raise UserError(_('You can not Change Stage.'))
        return super(TrainingApplication, self).write(vals)

    # @api.model
    # def action_create_applicant(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'emp.training.application',
    #         'view_mode': 'form',
    #         'target': 'new',
    #     }


    @api.onchange('employee_id')
    def _onchange_applicant_training_name(self):
        training = 'Training'
        if self.employee_id:
            name = f"{self.employee_id.name} {training}"
            self.application_name = name
            self.training_name = name
        else:
            self.application_name = ''
            self.training_name = ''

    # @api.multi
    def create_task(self):
        for rec in self:
            for line in rec.application_line_ids:
                for subject in line.subject_ids:
                    employee_user_id = rec.employee_id.user_id.id if rec.employee_id.user_id else False

                    responsible_id = rec.user_id.id
                    vals = {
                        'custom_application_id': rec.id,
                        # 'name': rec.number + "-" + rec.application_name+"/"+ line.course_id.name ,
                        'name':   line.course_id.name +" | "+ rec.employee_id.name +" | "+ rec.number,
                        'custom_subject_id': subject.id,
                        'custom_application_line_id': line.id,
                        'custom_training_start_date': line.start_date,
                        'custom_training_end_date': line.end_date,
                        'project_id': rec.project_id.id,
                        # 'user_id': self.env.user.id,
                        'user_ids': [(6, 0, list(filter(None, [employee_user_id, responsible_id])))],
                        'custom_training_employee_id': rec.employee_id.id,
                        'date_deadline': line.end_date,
                        'description': line.description,
                        'custom_is_application_task': True
                    }
                    task = self.env['project.task'].create(vals)
        rec.is_task_created = True

    def action_open_application_line(self):
        self.ensure_one()
        application_line = self.env['emp.training.application.line'].search([('application_id', '=', self.id)], limit=1)
        if application_line:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Application Line',
                'view_mode': 'form',
                'res_model': 'emp.training.application.line',
                'res_id': application_line.id,  # Ensure you pass the correct ID
                'target': 'new',  # Open in a new window
            }
        else:
            raise UserError('No application line found.')

    # @api.multi
    def view_task_application(self):
        action = self.env.ref('odoo_training_management_app.action_view_application_task').sudo().read()[0]
        action['domain'] = [('custom_application_id','in', self.ids)]
        action['context'] = {'default_application_id': self.id}
        return action

    def views_training_Count(self):
        action = self.env.ref('odoo_training_management_app.action_training_application_line').sudo().read()[0]
        action['domain'] = [('application_id','in', self.ids)]
        return action

    # @api.multi
    def unlink(self):
        raise UserError(_('You can not delete application now.'))
        return super(TrainingApplication, self).unlink()

class TrainingApplicationLine(models.Model):
    _name = "emp.training.application.line"
    _description = 'Training Application Line'
    _rec_name = 'number'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.model
    def _default_stage(self):
        stage_id = self.env['emp.training.application.line.stage'].search([('default_stage','=', True)],limit=1)
        return stage_id

    def _group_expand_stages(self, stages, domain, order):
        return self.env['emp.training.application.line.stage'].search([])



    

    start_date = fields.Date(
        string='Start Date',
        required=True
    )
    end_date = fields.Date(
        string='End Date',
        required=True
    )
    app_stage_line_ids = fields.Many2one(
        'emp.training.application.line.stage', 
        string='Employee Training Stages',
        tracking=True,
        default=_default_stage,
        group_expand='_group_expand_stages',
        index=True
    )
    application_id = fields.Many2one(
        'emp.training.application', 
        string='Application'
    )

    task_count = fields.Integer(related='application_id.task_count')
    stage_id = fields.Many2one('emp.training.application.stage')

    def view_task(self):
            action = self.env.ref('odoo_training_management_app.action_view_application_task').sudo().read()[0]
            action['domain'] = [('custom_application_id', 'in', self.ids)]
            action['context'] = {'default_custom_application_id': self.id}
            return action

    def write(self, vals):
        result = super(TrainingApplicationLine, self).write(vals)
        for record in self:
            application_lines = record.application_id.application_line_ids.mapped('app_stage_line_ids')
            all_lines_folded = all(line.fold for line in application_lines)
            if all_lines_folded:
                complete_stage = self.env['emp.training.application.stage'].search([('name', '=', 'Completed')], limit=1)
                if complete_stage:
                    record.application_id.stage_id = complete_stage
            else:
                record.stage_id.is_approve = False
        return result

    course_id = fields.Many2one(
        'slide.channel', 
        string='Course' , 
        required=True
    )
    # subject_ids = fields.Many2many(
    #     'training.subject',
    #     string='Subject',
    #     required=True
    # )
    subject_ids = fields.Many2many(
        'slide.slide',
        string='Subject',
        required=True
    )
    training_center_id = fields.Many2one(
        'emp.training.center',
        string='Training Center', 
    )
    class_room_id = fields.Many2one(
        'emp.training.class.room',
        string='Class Room',
    )
    description = fields.Text(
        string='Description'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='application_id.employee_id',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        related='application_id.user_id',
    )
    number = fields.Char(
        string='Number',
        related='application_id.number',
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='application_id.project_id',
        

    )

    applicant_id = fields.Many2one(related='application_id')

    create_date = fields.Date(
        string='Create Date',
        default=fields.Date.context_today,
    )
    
    # @api.onchange('course_id')
    # def onchange_course_id(self):
    #     subject_ids = [('id', 'in', self.course_id.subject_ids.ids)]
    #     return {'domain': {'subject_ids': [('id', 'in', self.course_id.subject_ids.ids)]}}
    @api.onchange('course_id') #odoo13
    
    def onchange_course_id(self):
        subject_ids = [('id', 'in', self.course_id.slide_ids.ids)]
        return {'domain': {'subject_ids': [('id', 'in', self.course_id.slide_ids.ids)]}}


    # @api.multi
    # def _get_report_values(self, line):
    #     return ', '.join([i.name for i in line.subject_ids])
    #odoo13
    def _get_report_values(self, line):
        return ', '.join([i.name for i in line.subject_ids])

    # @api.multi
    # def _get_report_doc_values(self, doc):
    #     return ', '.join([i.name for i in doc.subject_ids])
    #odoo13
    def _get_report_doc_values(self, doc):
        return ', '.join([i.name for i in doc.subject_ids])

    # @api.multi
    def unlink(self):
        raise UserError(_('You can not delete application now.'))
        return super(TrainingApplicationLine, self).unlink()

    def name_get(self):
        result = []
        for rec in self:
            name = rec.number +' - '+ rec.employee_id.name + ' - ' + rec.course_id.name
            result.append((rec.id, name))
        return result
    
    def action_send_training_mail(self):
        template_id = self.env.ref('odoo_training_management_app.tech_training_confirm_email_template').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        training_report_pdf = self.env.ref('odoo_training_management_app.report_training_application_line')
        data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf(training_report_pdf, [self.id], data=None)[0])
        training_report_values = {
            'name': 'Training ' + self.display_name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'emp.training.application.line',
        }
        training_report_attachment_id = self.env[
            'ir.attachment'].sudo().create(
            training_report_values)
        training_context = {
                    'default_model': 'emp.training.application.line',
                    'default_res_id': self.id,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'custom_layout': "mail.mail_notification_paynow",
                    'force_email': False,
                    'default_attachment_ids': [(4, training_report_attachment_id.id)]                
            }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': training_context,
        }
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


# Action to Format Phone number manually
    

                