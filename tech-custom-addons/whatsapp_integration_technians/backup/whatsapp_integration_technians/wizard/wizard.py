from odoo import api, fields, models
import html2text

class WhatsappSendMessage(models.TransientModel):
    _name = 'whatsapp.message.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    record_id = fields.Integer('Record id')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True, )

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']
        returned_fields = fields + ['partner_ids']
        values = dict.fromkeys(res_ids, False)
        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(
            template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if
                                 template_values[res_id].get(field))
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + ' '
            message_string = message_string[:(len(message_string) )]
            number = self.user_id.mobile
            link = "https://web.whatsapp.com/send?phone=" + number
            send_msg = {
                'type': 'ir.actions.act_url',
                'url': link + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
                
            }
            message = self.env['mail.message'].create({
                'model': self.model,
                'res_id': self.record_id,
                'body': message_string, 
                'subtype_id': self.env.ref('mail.mt_note').id,
            })

            return send_msg