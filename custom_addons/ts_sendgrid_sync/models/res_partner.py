
from odoo import fields, models,api
from odoo.exceptions import UserError, ValidationError
import python_http_client.exceptions as http_exceptions
import sendgrid
import json
from datetime import date, datetime
import re

def is_valid_email(email):
    if not isinstance(email, str) or not email.strip():
        return False
    # Regular expression to validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


# import os


class ResPartner(models.Model):
    _inherit = 'res.partner'

    synced_with_sendgrid = fields.Boolean(string='Sendgrid Synced', default=False, readonly=True)
    sendgrid_contact_id = fields.Char(string='Sendgrid Id of contact')
    display_warning = fields.Boolean(string='Display Warning', compute='_compute_display_warning', store=False)

    @api.depends()
    def _compute_display_warning(self):
        config_settings = self.env['res.config.settings'].default_get(['display_warning'])
        display_warning = config_settings.get('display_warning', False)
        for partner in self:
            partner.display_warning = display_warning

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get('email'):
            self.synced_with_sendgrid = False
        return res

    @api.model
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        if 'email' not in vals_list:
            return res
        auto_sync = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.auto_sync', default=False)

        if auto_sync == 'True': # and not synced and email:
            linked_fields = self.env['contacts.fields.link'].search([])
            if linked_fields:
                contact_vals = {"custom_fields": {}}
                first_name, last_name = "", ""
                contact_vals['custom_fields']['Data_Types'] = 'Contact'
                for linked_field in linked_fields:
                    sendgrid_field_name = linked_field.sendgrid_field.name
                    odoo_field_name = linked_field.odoo_field.name
                    field_value = getattr(res, odoo_field_name, None)
                    if field_value:
                        if isinstance(field_value, datetime):
                            field_value = field_value.strftime('%m/%d/%Y')
                        elif isinstance(field_value, date):
                            field_value = field_value.strftime('%m/%d/%Y')
                        elif isinstance(field_value, models.BaseModel):
                            field_value = field_value.name

                        contact_vals[sendgrid_field_name] = field_value

                    if odoo_field_name == "display_name" and field_value:
                        name_parts = field_value.split(" ", 1)
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else ""

                    if sendgrid_field_name == "first_name":
                        contact_vals["first_name"] = first_name
                    elif sendgrid_field_name == "last_name":
                        contact_vals["last_name"] = last_name
                    elif sendgrid_field_name == "email":
                        if isinstance(field_value, str) and is_valid_email(field_value):
                            contact_vals["email"] = field_value
                    elif sendgrid_field_name in ["address", "phone_number"]:
                        contact_vals[sendgrid_field_name] = field_value  if field_value else ''
                    else:
                        contact_vals["custom_fields"][sendgrid_field_name] = field_value if field_value not in [False,
                                                                                                                None] else ""

                if "last_name" not in contact_vals:
                    contact_vals["last_name"] = last_name

                if "email" in contact_vals and is_valid_email(contact_vals["email"]):
                    contacts = [contact_vals]
                    self.send_contact(contacts, res)

        return res
    def get_key(self):
        key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
        if not key:
            raise UserError("Enter an API Key in Settings!")
        api_key = {'SENDGRID_API_KEY': key}
        return api_key

    def add_contact_from_odoo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linked Odoo Fields with Sendgrid Fields',
            'res_model': 'contacts.send.wizard',
            'view_mode': 'form',
            'target': 'new',
        }


    def display_links(self):
        print('sucessssssssssssssssssssssssssssssssss')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Map Odoo Fields with Sendgrid Fields',
            'res_model': 'contacts.fields.link',
            'view_mode': 'form',
            'view_id': self.env.ref('ts_sendgrid_sync.fields_link_wizard_view_form').id,
            'target': 'new',
        }


    def button_to_link(self):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))
        field_response = sg.client.marketing.field_definitions.get()
        # if (field_response.status_code != 202):
        #     raise ValidationError(f"Could not add Contact to Sendgrid at the moment")

        print(field_response.status_code)
        print(field_response.body)
        all_fields = json.loads(field_response.body)
        print(all_fields)

        field_records = []
        sendgrid_custom_field_names = []

        for field in all_fields.get('custom_fields', []):
            sendgrid_custom_field_names.append(field['name'])
            existing_field = self.env['contact.custom.fields'].search([
                ('field_id', '=', field['id']),
                ('name', '=', field['name'])
            ])
            if not existing_field:
                field_records.append({
                    'field_id': field['id'],
                    'name': field['name'],
                    'field_type': field['field_type'],
                })
        if 'odoo_model' not in sendgrid_custom_field_names:
            data = {"name": "odoo_model", "field_type": "Text"}
            create_response = sg.client.marketing.field_definitions.post(request_body=data)
            print('-----------------',create_response.status_code)

        for field in all_fields.get('reserved_fields', []):
            existing_field = self.env['contact.custom.fields'].search([
                ('field_id', '=', field['id']),
                ('name', '=', field['name'])
            ])
            if not existing_field:
                field_records.append({
                    'field_id': field['id'],
                    'name': field['name'],
                    'field_type': field['field_type'],
                })

        if field_records:
            self.env['contact.custom.fields'].create(field_records)


        return {
            'type': 'ir.actions.act_window',
            'name': 'Map Odoo Fields with Sendgrid Fields',
            'res_model': 'contacts.fields.link',
            'view_mode': 'tree',
            'view_id': self.env.ref('ts_sendgrid_sync.fields_link_wizard_view_Tree').id,
            'target': 'current',
        }


    def send_contact(self, contacts, partner):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))

        data = {
            "contacts": contacts
        }
        try:
            response = sg.client.marketing.contacts.put(request_body=data)

            print(response.status_code)

            if response.status_code == 202:
                # print('Gaila Bhau!!')
                partner.synced_with_sendgrid = True
                partner.message_post(body="<strong>Contact Synced with Sendgrid</strong>")

            else:
                print("Contacts cannot be added at the moment")
        except http_exceptions.BadRequestsError as e:
            if e.status_code == 400:
                raise UserError("Please enter a valid email address!")
            else:
                print(f"An unexpected error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def fetch_contacts_id_from_sendgrid(self):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))

        response = sg.client.marketing.contacts.get()
        response_body = response.body.decode('utf-8')
        data = json.loads(response_body)
        sendgrid_contacts = data['result']
        for contact in sendgrid_contacts:
            mycontact = self.env['res.partner'].search([('email','=',contact['email'])], limit=1)
            if mycontact.exists():
                mycontact.sendgrid_contact_id = contact['id']

            crm_contact = self.env['crm.lead'].search([('email_from', '=', contact['email'])], limit=1)
            if crm_contact.exists():
                crm_contact.sendgrid_contact_id = contact['id']

            applicant_contact = self.env['hr.applicant'].search([('email_from', '=', contact['email'])], limit=1)
            if applicant_contact.exists():
                applicant_contact.sendgrid_contact_id = contact['id']


    def unlink(self):
        partners = []
        delete_sync = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.delete_sync', default=False)
        if delete_sync == 'True':
            for rec in self:
                partners.append(rec.id)
            self.delete_contact_in_sendgrid(partners)
        return super(ResPartner, self).unlink()

    def delete_contact_in_sendgrid(self, partners):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))

        records = self.env['res.partner'].browse(partners)
        sendgrid_id_string = ', '.join(record.sendgrid_contact_id for record in records if record.sendgrid_contact_id)

        if sendgrid_id_string:
            params = {'ids': sendgrid_id_string}

            response = sg.client.marketing.contacts.delete(
                query_params=params
            )

            print(response.status_code)
            print(response.body)
            print(response.headers)
