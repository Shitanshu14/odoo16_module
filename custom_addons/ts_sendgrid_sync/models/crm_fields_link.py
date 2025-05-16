from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import python_http_client.exceptions as http_exceptions
import sendgrid
# import json
from datetime import date, datetime
import re

def is_valid_email(email):
    # Regular expression to validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


class CrmSendWizard(models.TransientModel):
    _name = 'crm.send.wizard'
    _description = "Display Mapped Fields and Send CRM Contact"

    link_ids = fields.Many2many(
        comodel_name='crm.fields.link',
        string="Mapped Fields",
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        res = super(CrmSendWizard, self).default_get(fields)
        links = self.env['crm.fields.link'].search([])
        res['link_ids'] = [(6, 0, links.ids)]
        return res


    def get_key(self):
        key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
        if not key:
            raise UserError("Enter an API Key in Settings!")
        api_key = {'SENDGRID_API_KEY': key}
        return api_key

    def send_contact_now(self):
        lead_ids = self._context.get('active_ids', [])
        limit = int(self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.contact_send_limit', default=0))

        # if len(lead_ids) < (limit if limit else 100):
        if len(lead_ids) < 501:
            linked_fields = self.env['crm.fields.link'].search([])
            if not linked_fields:
                raise ValidationError("Map Odoo and Sendgrid Fields in Configuration first!")

            leads = self.env['crm.lead'].browse(lead_ids)

            for lead in leads:
                if not lead.email_from:
                    continue
                contact_vals = {"custom_fields": {}}
                contact_vals["custom_fields"]["Data_Types"] = lead.type
                first_name, last_name = "", ""
                for linked_field in linked_fields:
                    sendgrid_field_name = linked_field.sendgrid_field.name
                    odoo_field_name = linked_field.odoo_field.name
                    field_value = getattr(lead, odoo_field_name, None)
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
                        contact_vals["custom_fields"][sendgrid_field_name] = field_value if field_value not in [False, None] else ""

                if "last_name" not in contact_vals:
                    contact_vals["last_name"] = last_name

                if "email" in contact_vals and is_valid_email(contact_vals["email"]):
                    contacts = [contact_vals]
                    # raise ValidationError(str(contacts))
                    self.send_contact(contacts, lead)

        else:
            raise UserError(f'Cannot send more than {limit} contacts!!!')

    def send_contact(self, contacts, lead):
        api_key = self.get_key()
        sg = sendgrid.SendGridAPIClient(api_key.get('SENDGRID_API_KEY'))

        data = {
            "contacts": contacts
        }
        try:
            response = sg.client.marketing.contacts.put(request_body=data)
            # raise UserError(str(response))
            if response.status_code == 202:
                lead.synced_with_sendgrid = True
                lead.message_post(body="<strong>Lead Synced with Sendgrid</strong>")

            else:
              raise  UserError("Contacts cannot be added at the moment")
        except http_exceptions.BadRequestsError as e:
            if e.status_code == 400:
                
                raise UserError("Please enter a valid email address!")
            else:
                raise UserError(f"An unexpected error occurred: {e}")
        except Exception as e:
            raise UserError(f"An unexpected error occurred: {e}")



class ContactsFieldsLink(models.Model):
    _name = 'crm.fields.link'
    _description = "Mapping Leads fields with Sendgrid Fields"
    _order = "id"

    odoo_field = fields.Many2one(
        comodel_name='ir.model.fields',
        domain="[('model_id.model','=','crm.lead'),('ttype', 'in', ('date','integer','char','text', 'many2one','datetime'))]",
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
            elif field_type == 'datetime':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Date')]}}
        else:
            return {'domain': {'sendgrid_field': []}}
