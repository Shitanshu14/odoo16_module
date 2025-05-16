from odoo import fields, models,api
from odoo.exceptions import UserError, ValidationError
import python_http_client.exceptions as http_exceptions
import sendgrid
import json
from datetime import date, datetime
import re

def is_valid_email(email):
    # Regular expression to validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    synced_with_sendgrid = fields.Boolean(string='Sendgrid Synced', default=False, readonly=True)
    sendgrid_contact_id = fields.Char(string='Sendgrid Id of contact')
    display_warning_crm = fields.Boolean(string='Display Warning', compute='_compute_display_warning', store=False)

    @api.depends()
    def _compute_display_warning(self):
        config_settings = self.env['res.config.settings'].default_get(['display_warning_crm'])
        display_warning_crm = config_settings.get('display_warning_crm', False)
        for partner in self:
            partner.display_warning_crm = display_warning_crm

    @api.model
    def create(self, vals_list):
        res = super(CrmLead, self).create(vals_list)
        if 'email' not in vals_list:
            return res
        auto_sync_crm = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.auto_sync_crm', default=False)
        if auto_sync_crm == 'True':
            linked_fields = self.env['crm.fields.link'].search([])
            if linked_fields:
                contact_vals = {}
                contact_vals = {"custom_fields": {}}
                first_name, last_name = "", ""
                contact_vals['custom_fields']['Data_Types'] = 'Crm'
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

                        if odoo_field_name == "contact_name" and field_value:
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
                        elif sendgrid_field_name in ["address", "phone_number"]:
                            contact_vals[sendgrid_field_name] = field_value
                        else:
                            contact_vals["custom_fields"][sendgrid_field_name] = field_value if field_value not in [
                                False, None] else ""

                    if "last_name" not in contact_vals:
                        contact_vals["last_name"] = last_name

                    if "email" in contact_vals and is_valid_email(contact_vals["email"]):
                        contacts = [contact_vals]
                self.send_contact(contacts, res)
        return res

    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if vals.get('email_from'):
            self.synced_with_sendgrid = False
        return res

    def get_key(self):
        key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
        if not key:
            raise UserError("Enter an API Key in Settings!")
        api_key = {'SENDGRID_API_KEY': key}
        return api_key


    def unlink(self):
        leads = []
        delete_sync_crm = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.delete_sync_crm',default=False)
        if delete_sync_crm == 'True':
            for rec in self:
                leads.append(rec.id)
            self.delete_contact_in_sendgrid(leads)
        return super(CrmLead, self).unlink()


    def delete_contact_in_sendgrid(self, leads):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))

        records = self.env['crm.lead'].browse(leads)
        sendgrid_id_string = ', '.join(record.sendgrid_contact_id for record in records if record.sendgrid_contact_id)

        if sendgrid_id_string:
            params = {'ids': sendgrid_id_string}

            response = sg.client.marketing.contacts.delete(
                query_params=params
            )

            # print(response.status_code)
            # print(response.body)
            # print(response.headers)

    def button_to_link(self):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))
        field_response = sg.client.marketing.field_definitions.get()
        # if (field_response.status_code != 202):
        #     raise ValidationError(f"Could not add Contact to Sendgrid at the moment")

        # print(field_response.status_code)
        # print(field_response.body)
        all_fields = json.loads(field_response.body)
        # print(all_fields)

        field_records = []

        for field in all_fields.get('custom_fields', []):
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
            'res_model': 'crm.fields.link',
            'view_mode': 'tree',
            'view_id': self.env.ref('ts_sendgrid_sync.crm_fields_link_view_Tree').id,
            'target': 'current',
        }

    def send_contact(self, contacts, lead):
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
                lead.synced_with_sendgrid = True
                lead.message_post(body="<strong>Lead Synced with Sendgrid</strong>")

            else:
                print("Contacts cannot be added at the moment")

        except http_exceptions.BadRequestsError as e:
            if e.status_code == 400:
                raise UserError("Please enter a valid email address!")
            else:
                print(f"An unexpected error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # def get_key(self):
    #     key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
    #     if not key:
    #         raise UserError("Enter an API Key in Settings!")
    #     api_key = {'SENDGRID_API_KEY': key}
    #     return api_key
    #
    # def send_contact(self, contacts):
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
    #             print('Gaila Bhau!!')
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

    def add_contact_from_odoo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Linked Odoo Fields with Sendgrid Fields',
            'res_model': 'crm.send.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
        # for record in self:
        #     ids = self._context.get('active_ids')
        #     if len(ids) < 100:
        #         linked_fields = self.env['crm.fields.link'].search([])
        #         if not linked_fields:
        #             raise ValidationError("Link Odoo and Sendgrid Fields in Configuration first!")
        #         contact_vals = {}
        #         for linked_field in linked_fields:
        #             sendgrid_field_name = linked_field.sendgrid_field.name
        #             odoo_field_name = linked_field.odoo_field.name
        #             field_value = getattr(record, odoo_field_name, None)
        #             if field_value:
        #                 contact_vals.update({
        #                     sendgrid_field_name : field_value
        #                 })
        #
        #         contacts = [contact_vals]
        #         self.send_contact(contacts)
        #     else:
        #         raise UserError('Cannot send more than 1000 contacts!!!')
