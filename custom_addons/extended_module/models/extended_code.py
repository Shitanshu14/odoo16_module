from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    know_your_employee_survey_id = fields.Many2one(
        'survey.survey', string="Know Your Employee Form"
    )
    background_verification_survey_id = fields.Many2one(
        'survey.survey', string="Background Verification Form"
    )
    policies_procedures_survey_id = fields.Many2one(
        'survey.survey', string="Policies and Procedures Form"
    )


    def action_send_onboarding_forms_email(self):
        for applicant in self:
            if not applicant.email_from:
                raise UserError(_("Applicant's email is not specified."))

            email_to = applicant.email_from
            email_from = self.env.user.email or 'noreply@yourcompany.com'
            subject = "Welcome to Technians – Complete Your Joining Formalities"

            def generate_survey_link(survey):
                if not survey:
                    return None
                user_input = self.env['survey.user_input'].create({
                    'survey_id': survey.id,
                    'partner_id': applicant.partner_id.id,
                    'email': applicant.email_from,
                    'applicant_id': [(6, 0, [applicant.id])],
                })
                return user_input.get_start_url()

            kyc_url = generate_survey_link(applicant.know_your_employee_survey_id)
            bgv_url = generate_survey_link(applicant.background_verification_survey_id)
            policies_url = generate_survey_link(applicant.policies_procedures_survey_id)

            body_html = f"""
                   <div style="font-family: Arial, sans-serif; font-size: 14px;">
                       <p>Dear {applicant.partner_name or applicant.name},</p>
                       <p>Welcome to <b>Technians Softech Pvt Ltd!</b></p>
                       <p>We are delighted to have you on board. As we embark on this exciting journey together, we want to ensure a smooth onboarding process for you.</p>
                       <p>To initiate the joining formalities, we kindly request you to fill out the following forms:</p>
                       <ul>
               """
            if kyc_url:
                body_html += f"""
                       <li>
                           <b><a href="{kyc_url}" target="_blank">Know Your Employee Form</a></b>:
                           This form provides us with essential information about you.
                       </li>
                   """
            if bgv_url:
                body_html += f"""
                       <li>
                           <b><a href="{bgv_url}" target="_blank">Background Verification Form</a></b>:
                           Please complete this form to facilitate the verification process.
                       </li>
                   """
            if policies_url:
                body_html += f"""
                       <li>
                           <b><a href="{policies_url}" target="_blank">Policies and Procedures Form</a></b>:
                           Familiarize yourself with our company policies.
                       </li>
                   """

            body_html += """
                       </ul>
                       <p>Your prompt attention to these forms will contribute to a seamless onboarding experience.</p>
                       <p>If you have any questions or require assistance, feel free to reach out to <b>Daksh Tageja</b> at <a href="mailto:daksh.tageja@technians.com">daksh.tageja@technians.com</a>.</p>
                       <p>We look forward to having you as part of the <b>Technians Softech Pvt Ltd</b> family!</p>
                       <p>Best regards,<br/>Human Resource,<br/>Technians</p>
                   </div>
               """

            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': email_from,
                'email_to': email_to,
            }
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            applicant.message_post(body=body_html, subject=subject, message_type='email')
