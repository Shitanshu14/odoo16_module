from odoo import fields, models, api
import datetime
from datetime import date
from odoo.exceptions import ValidationError
class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'
    
    
    
    def tech_employee_send_birthday_email(self):
        records = self.search([])
        for record in records:
            dob = record.birthday
            if dob:
                if self.is_birthday_today(dob):
                    mail_template = self.env.ref('technians_apps_customization.tech_employee_birthday_email_tpl')
                    mail_template.send_mail(record.id, force_send=True)

    def tech_employee_arch_send_birthday_email(self):
        records  = self.search([('active', '=', False)])
        for record in records:
            dob = record.birthday
            personal_email  = record.email_personal
            if dob and personal_email:
                if self.is_birthday_today(dob):
                    mail_template = self.env.ref('technians_apps_customization.tech_employee_arch_birthday_email_tpl')
                    mail_template.send_mail(record.id, force_send=True)

    


    @staticmethod
    def is_birthday_today(birthdate):
        today = datetime.date.today()
        return birthdate.month == today.month and birthdate.day == today.day
    
    is_birthday_month = fields.Boolean('Birthday This Month',store=True)
    is_anniversary_month = fields.Boolean('Anniversaries This Month',store=True)
    email_personal = fields.Char(string="Personal Email",tracking=True)
    # @api.depends('birthday')
    # def _is_birthday_month(self):
    #     current_month = fields.Date.today().month
    #     # raise ValidationError(current_month)
    #     for record in self:
    #         if record.birthday and record.birthday.month == current_month:
    #             record.is_birthday_month = True
    #         else:
    #             record.is_birthday_month = False

    # @api.depends('birthday')
    # def _is_anniversary_month(self):
    #     current_month = fields.Date.today().month
    #     # raise ValidationError(current_month)
    #     for record in self:
    #         record.is_anniversary_month = True
    #         # if record.joining_date:
    #         # else:
    #         #     record.is_anniversary_month = False


    def tech_monthly_anniversary_update(self):
        records = self.search([])
        current_month = fields.Date.today().month
        for record in records:
            dob = record.birthday
            joining_date = record.first_contract_date
            if dob and dob.month == current_month:
                # set bithday month true
                record.is_birthday_month = True
            else:
                # set birthday month false
                record.is_birthday_month = False
            if joining_date and joining_date.month == current_month:
                # set anniversary month true
                record.is_anniversary_month = True
            else:
                # set anniversary month false
                record.is_anniversary_month = False

    