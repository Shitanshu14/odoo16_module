from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import sendgrid
import json


class SendgridStats(models.Model):
    _name = 'sendgrid.stats'
    _description = "Stats fetched from sendgrid"
    _order = "id"


    singlesend_id = fields.Char(
        string="Campaign ID",
        # required=True,
    )
    singlesend_name = fields.Char(
        string="Campaign Name",
        required=True,)
    sent = fields.Integer(
        string="Sent",
        required=True,)
    delivered = fields.Integer(
        string="Delivered",
        required=True,)
    opens = fields.Integer(
        string="Opens",
        required=True,)
    clicks = fields.Integer(
        string="Clicks",
        required=True,)

    # 5812fde5-6082-11ef-a7fb-5a754358f12e

    # def test_method(self):
    #     key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
    #     the_key = {'SENDGRID_API_KEY': key}
    #     sg = sendgrid.SendGridAPIClient(the_key.get('SENDGRID_API_KEY'))
    #     # response = sg.client.marketing.field_definitions.get()
    #
    #     data = {
    #         "name": "custom_field_name2",
    #         "field_type": "Text"
    #     }
    #
    #     response = sg.client.marketing.field_definitions.post(
    #         request_body=data
    #     )
    #
    #     print(response.status_code)
    #     print(response.body) #create custom_field
    #     # print(response.headers)
    #     field_response = json.loads(response.body)
    #     print(field_response)
    #
    #     # all_fields = sg.client.marketing.field_definitions.get()
    #     # print(all_fields.status_code)
    #     # print(all_fields.body)


    def get_values(self, sg, send):
        send_id = send['id']
        detail_response = sg.client.marketing.singlesends._(send_id).get()
        detailed_info = json.loads(detail_response.body)
        # print("----------------------yyyyyyyyyyyyy",detailed_info)
        single_send_info = {
            'singlesend_id': send_id,
            'singlesend_name': detailed_info.get('name'),
            'sent': send['stats']['requests'],
            'delivered': send['stats']['delivered'],
            'clicks': send['stats']['clicks'],
            'opens': send['stats']['opens']
        }
        return single_send_info


    def fetch_sendgrid_stats(self):
        key = self.env['ir.config_parameter'].sudo().get_param('ts_sendgrid_sync.api_key', default='')
        the_key = {'SENDGRID_API_KEY' : key}
        sg = sendgrid.SendGridAPIClient(the_key.get('SENDGRID_API_KEY'))

        params={}
        response = sg.client.marketing.stats.singlesends.get(query_params=params)
        print('sendgrid response code:',response.status_code)

        stats_response = json.loads(response.body)

        for send in stats_response.get('results', []):
            send_id = send['id']
            existing_record = self.env['sendgrid.stats'].search([('singlesend_id', '=', send_id)], limit=1)

            if existing_record:
                existing_record.write(self.get_values(sg, send))
            else:
                self.env['sendgrid.stats'].create(self.get_values(sg, send))

        # params = {}
        # send_id = '5812fde5-6082-11ef-a7fb-5a754358f12e'
        # response = sg.client.marketing.singlesends._(send_id).get()
        #
        # # response = sg.client.marketing.stats.singlesends.get(
        # #     query_params=params
        # # )
        #
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)

        # params = {'start_date': '2024-07-19', 'end_date': '2024-07-19', 'categories': 'marketing test'}

        # response = sg.client.categories.stats.get(
        #     query_params=params
        # )
        #
        # print(response.status_code)
        # print(response.body)
        #
        # response_body = response.body.decode('utf-8')
        # data = json.loads(response_body)
        #
        # if data and 'stats' in data[0] and 'metrics' in data[0]['stats'][0]:
        #     # category_name = data[0]['stats'][0]['name']
        #     metrics = data[0]['stats'][0]['metrics']
        #     print(metrics)
        #     print(metrics['requests'])
        #     print(metrics['requests'])
        #     # stats = self.env['sendgrid.stats'].search([])
        #     # if category_name not in stats:
        #     self.env['sendgrid.stats'].create({
        #         'category': data[0]['stats'][0]['name'],
        #         'sent':metrics['requests'],
        #         'delivered':metrics['delivered'],
        #         'opens':metrics['opens'],
        #         'clicks':metrics['clicks'],
        #     })
        #
        # else:
        #     print("Metrics not found in response")
        #
        # print(response.headers)
