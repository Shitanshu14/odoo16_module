from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
import sendgrid
import json


class ContactCustomFields(models.Model):
    _name = 'contact.custom.fields'
    _description = "Fields in Sendgrid"
    _order = "id"

    field_id = fields.Char(required=True,string='Field ID')
    name = fields.Char(required=True, string='Field Name')
    field_type = fields.Selection([ ('Number', 'Number'),('Text', 'Text'), ('Date', 'Date')], required=True, string="Field Type")

    # @api.model
    # def create(self, vals_list):
    #     key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
    #     the_key = {'SENDGRID_API_KEY': key}
    #     sg = sendgrid.SendGridAPIClient(the_key.get('SENDGRID_API_KEY'))
    #
    #     data = {
    #         "name": vals_list.get('field_name'),
    #         "field_type": vals_list.get('field_type')
    #     }
    #
    #     response = sg.client.marketing.field_definitions.post(request_body=data)
    #     print(response.status_code)
    #
    #     field_response = json.loads(response.body)
    #     print(field_response)
    #
    #     vals_list['field_id'] = field_response.get('id')
    #
    #     return super(ContactCustomFields, self).create(vals_list)

