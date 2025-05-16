from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import python_http_client.exceptions as http_exceptions
import sendgrid
# import json
from datetime import date
import re
from odoo.tools.safe_eval import pytz, _logger


def is_valid_email(email):
    # Regular expression to validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

class ApplicantSendWizard(models.TransientModel):
    _name = 'applicant.send.wizard'
    _description = "Display Mapped Fields and Send CRM Contact"

    link_ids = fields.Many2many(
        comodel_name='applicant.fields.link',
        string="Mapped Fields",
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        res = super(ApplicantSendWizard, self).default_get(fields)
        links = self.env['applicant.fields.link'].search([])
        res['link_ids'] = [(6, 0, links.ids)]
        return res


    def get_key(self):
        key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
        if not key:
            raise UserError("Enter an API Key in Settings!")
        api_key = {'SENDGRID_API_KEY': key}
        return api_key

    def send_contact_now(self):
        applicant_ids = self._context.get('active_ids', [])
        limit = int(self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.contact_send_limit', default=0))
        # if len(applicant_ids) < limit if limit else 100:
        if len(applicant_ids) <  301:
            linked_fields = self.env['applicant.fields.link'].search([])
            if not linked_fields:
                raise ValidationError("Map Odoo and Sendgrid Fields in Configuration first!")
            applicants = self.env['hr.applicant'].browse(applicant_ids)
            for applicant in applicants:
                contact_vals = {"custom_fields": {}}
                contact_vals['custom_fields']['Data_Types'] = 'applicant'
                first_name, last_name = "", ""
                # Separate custom fields
                for linked_field in linked_fields:
                    sendgrid_field_name = linked_field.sendgrid_field.name
                    odoo_field_name = linked_field.odoo_field.name
                    field_value = getattr(applicant, odoo_field_name, None)

                    if field_value:
                        if isinstance(field_value, datetime):
                            field_value = field_value.strftime('%m/%d/%Y')
                        if isinstance(field_value, date):
                            field_value = field_value.strftime('%m/%d/%Y')
                        elif isinstance(field_value, models.BaseModel):
                            if field_value != False:
                                field_value = field_value.name or ''
                    if odoo_field_name in ["applicant_current_city_id", "applicant_preferred_city_id","job_id"] and not field_value:
                        continue
                    if odoo_field_name == "display_name" and field_value:
                            name_parts = field_value.split(" ", 1)
                            first_name = name_parts[0]
                            last_name = name_parts[1] if len(name_parts) > 1 else ""
                    if sendgrid_field_name == "first_name":
                            contact_vals["first_name"] = first_name
                    elif sendgrid_field_name == "last_name":
                            contact_vals["last_name"] = last_name
                    elif sendgrid_field_name == "email":
                        if is_valid_email(field_value):
                            contact_vals["email"] = field_value
                    elif sendgrid_field_name in ["address", "phone_number","city"]:
                        contact_vals[sendgrid_field_name] = field_value if field_value not in [False ,None] else ''

                        
                    else:
                        contact_vals["custom_fields"][sendgrid_field_name] = field_value if field_value not in [False, None] else ""
                if "last_name" not in contact_vals:
                    contact_vals["last_name"] = last_name

                if "email" in contact_vals and is_valid_email(contact_vals["email"]):
                    contacts= [contact_vals]
                    # raise ValidationError(str(contacts))
                self.send_contact(contacts, applicant)
        else:
            raise UserError(f'Cannot send more than {limit} contacts!!!')

    def send_contact(self, contacts, applicant):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))

        data = {"contacts": contacts}
        try:
            response = sg.client.marketing.contacts.put(request_body=data)
            if response.status_code == 202:
                applicant.synced_with_sendgrid = True
                applicant.message_post(body="<strong>Applicant Synced with Sendgrid</strong>")
                # return {
                #     'type': 'ir.actions.client',
                #     'tag': 'display_notification',
                #     'params': {
                #         'type': 'success',
                #         'message': _('Your request has been successfully sent'),
                #         'next': {'type': 'ir.actions.act_window_close'},
                #     }
                # }
            else:
                raise UserError("Contacts cannot be added at the moment")
        except http_exceptions.BadRequestsError as e:
            if e.status_code == 400:
                raise UserError("Please enter a valid email address!")
            else:
                raise UserError(f"An unexpected error occurred: {e}")
        except Exception as e:
            raise UserError(f"An unexpected error occurred: {e}")

    # def send_contact_now(self):
    #     applicant_ids = self._context.get('active_ids', [])
    #     limit = int(self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.contact_send_limit', default=0))
    #     if len(applicant_ids) < limit if limit else 100:
    #         linked_fields = self.env['applicant.fields.link'].search([])
    #         if not linked_fields:
    #             raise ValidationError("Map Odoo and Sendgrid Fields in Configuration first!")
    #
    #         applicants = self.env['hr.applicant'].browse(applicant_ids)
    #
    #         for applicant in applicants:
    #             contact_vals = {}
    #             for linked_field in linked_fields:
    #                 sendgrid_field_name = linked_field.sendgrid_field.name
    #                 odoo_field_name = linked_field.odoo_field.name
    #
    #                 field_value = getattr(applicant, odoo_field_name, None)
    #                 if field_value:
    #                     # Check if field is a date and format it as YYYY/MM/DD
    #                     if isinstance(field_value, date):
    #                         field_value = field_value.strftime('%m/%d/%Y')
    #                     elif isinstance(field_value, models.BaseModel):
    #                         field_value = field_value.name
    #
    #                     contact_vals.update({
    #                         sendgrid_field_name: field_value
    #                     })
    #                 # if field_value:
    #                 #     contact_vals.update({
    #                 #         sendgrid_field_name: field_value
    #                 #     })
    #             if any(contact_vals):
    #                 contact_vals.update({
    #                     'odoo_model': 'applicant'
    #                 })
    #             contacts = [contact_vals]
    #             # print("----------------------------", contacts)
    #             self.send_contact(contacts, applicant)
    #     else:
    #         raise UserError(f'Cannot send more than {limit} contacts!!!')
    #
    #
    # def send_contact(self, contacts, applicant):
    #     api_key = self.get_key()
    #     sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))
    #
    #     data = {
    #         "contacts": contacts
    #     }
    #     try:
    #         response = sg.client.marketing.contacts.put(request_body=data)
    #
    #         print(response.status_code)
    #
    #         if response.status_code == 202:
    #             applicant.synced_with_sendgrid = True
    #             applicant.message_post(body="<strong>Applicant Synced with Sendgrid</strong>")
    #
    #         else:
    #             print("Contacts cannot be added at the moment")
    #     except http_exceptions.BadRequestsError as e:
    #         if e.status_code == 400:
    #             raise UserError("Please enter a valid email address!")
    #         else:
    #             print(f"An unexpected error occurred: {e}")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")


class ApplicantFieldsLink(models.Model):
    _name = 'applicant.fields.link'
    _description = "Mapping Leads fields with Sendgrid Fields"
    _order = "id"

    odoo_field = fields.Many2one(
        comodel_name='ir.model.fields',
        domain="[('model_id.model','=','hr.applicant'),('ttype', 'in', ('date','integer','char','text', 'many2one','datetime'))]",
        ondelete='cascade',
        required=True)

    sendgrid_field = fields.Many2one(
        comodel_name='contact.custom.fields',
        domain="[('name','!=','odoo_model')]",
        string="Sendgrid Field",
        required=True)

    @api.onchange('odoo_field')
    def _onchange_odoo_field(self):
        self.sendgrid_field = False
        if self.odoo_field:
            field_type = self.odoo_field.ttype
            if field_type == 'date':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Date')]}}
            elif field_type == 'integer':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Number')]}}
            elif field_type in ['char', 'text']:
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Text')]}}
            elif field_type == 'many2one':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Text')]}}
            if field_type == 'datetime':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Date')]}}
        else:
            return {'domain': {'sendgrid_field': []}}
