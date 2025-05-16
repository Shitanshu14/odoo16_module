from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import python_http_client.exceptions as http_exceptions
import sendgrid
from datetime import date, datetime
# import json
import re

def is_valid_email(email):
    # Regular expression to validate email format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


class ContactsSendWizard(models.TransientModel):
    _name = 'contacts.send.wizard'
    _description = "Display Mapped Fields and Send Contact"

    link_ids = fields.Many2many(
        comodel_name='contacts.fields.link',
        string="Mapped Fields",
        readonly=True
    )

    @api.model
    def default_get(self, fields):
        res = super(ContactsSendWizard, self).default_get(fields)
        links = self.env['contacts.fields.link'].search([])
        res['link_ids'] = [(6, 0, links.ids)]
        return res


    def get_key(self):
        key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
        if not key:
            raise UserError("Enter an API Key in Settings!")
        api_key = {'SENDGRID_API_KEY': key}
        return api_key
    

    def send_contact_now(self):
        partner_ids = self._context.get('active_ids', [])
        limit = int(self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.contact_send_limit', default=0))
        if len(partner_ids) < limit if limit else 100:
            linked_fields = self.env['contacts.fields.link'].search([])
            if not linked_fields:
                raise ValidationError("Map Odoo and Sendgrid Fields in Configuration first!")
            partners = self.env['res.partner'].browse(partner_ids)
            for partner in partners:
                contact_vals = {"custom_fields": {}}
                contact_vals["odoo_contact_id"] = partner.id
                first_name, last_name = "", ""

                for linked_field in linked_fields:
                    sendgrid_field_name = linked_field.sendgrid_field.name
                    odoo_field_name = linked_field.odoo_field.name
                    field_value = getattr(partner, odoo_field_name, None)
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
                        if is_valid_email(field_value):
                            contact_vals["email"] = field_value
                    elif sendgrid_field_name in ["address", "phone_number"]:
                        contact_vals[sendgrid_field_name] = field_value
                    else:
                        contact_vals["custom_fields"][sendgrid_field_name] = field_value if field_value not in [False,
                                                                                                                None] else ""

                if "last_name" not in contact_vals:
                        contact_vals["last_name"] = last_name

                if "email" in contact_vals and is_valid_email(contact_vals["email"]):
                        contacts = [contact_vals]
                        self.send_contact(contacts, partner)

        else:
            raise UserError(f'Cannot send more than {limit} contacts!!!')

    # def send_contact_now(self):
    #     partner_ids = self._context.get('active_ids', [])
    #     limit = int(self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.contact_send_limit', default=0))
    #     if len(partner_ids) < limit if limit else 100:
    #         linked_fields = self.env['contacts.fields.link'].search([])
    #         if not linked_fields:
    #             raise ValidationError("Map Odoo and Sendgrid Fields in Configuration first!")

    #         partners = self.env['res.partner'].browse(partner_ids)

    #         for partner in partners:
    #             contact_vals = {'odoo_contact_id':partner.id}
    #             for linked_field in linked_fields:
    #                 sendgrid_field_name = linked_field.sendgrid_field.name
    #                 odoo_field_name = linked_field.odoo_field.name

    #                 field_value = getattr(partner, odoo_field_name, None)
    #                 if field_value:
    #                     contact_vals.update({
    #                         sendgrid_field_name: field_value
    #                     })
    #             if any(contact_vals):
    #                 contact_vals.update({
    #                     'odoo_model': 'contact'
    #                 })
    #             contacts = [contact_vals]
    #             self.send_contact(contacts,partner)
    #     else:
    #         raise UserError(f'Cannot send more than {limit} contacts!!!')


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



class ContactsFieldsLink(models.Model):
    _name = 'contacts.fields.link'
    _description = "Linking Contact fields with Sendgrid Fields"
    _order = "id"

    odoo_field = fields.Many2one(
        comodel_name='ir.model.fields',
        domain="[('model_id.model','=','res.partner'),('ttype', 'in', ('date','integer','char','text','many2one','datetime'))]",
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
            elif field_type in 'many2one':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Text')]}}
            elif field_type in 'datetime':
                return {'domain': {'sendgrid_field': [('field_type', '=', 'Date')]}}
        else:
            return {'domain': {'sendgrid_field': []}}
