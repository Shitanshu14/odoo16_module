import html2text

from odoo import api, fields, models


class WhatsappSendMessage(models.TransientModel):
    _name = 'whatsapp.message.wizard'

    user_name = fields.Text('Username', readonly=True)
    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(required=True)
    mobile_number = fields.Selection(
        selection="_get_mobile_number_selection", string="Select Number"
    )
    message = fields.Text(string="Message", required=True)
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

    @api.model
    def _get_mobile_number_selection(self):
        # Get the active model and active record ID from the context
        model = self._context.get('active_model')
        res_id = self._context.get('active_id')
        phone_numbers = set()

        if model in ['sale.order', 'purchase.order', 'crm.lead', 'hr.applicant', 'hr.employee', 'calls.technians',
                     'project.project', 'res.partner']:
            # Retrieve the partner or lead from the order or lead
            record = self.env[model].browse(res_id)

            if model in ['sale.order', 'purchase.order']:
                partner = record.partner_id
                # Check if the partner has any phone numbers (mobile and phone)
                if partner.mobile:
                    phone_numbers.add((partner.mobile, partner.mobile))
                if partner.phone:
                    phone_numbers.add((partner.phone, partner.phone))

            if model == 'res.partner':
                if record.mobile:
                    phone_numbers.add((record.mobile, record.mobile))
                if record.phone:
                    phone_numbers.add((record.phone, record.phone))
            if model == 'hr.applicant':
                if record.partner_mobile:
                    phone_numbers.add((record.partner_mobile, record.partner_mobile))
                if record.partner_phone:
                    phone_numbers.add((record.partner_phone, record.partner_phone))

            if model == 'project.project':
                if record.partner_id.mobile:
                    phone_numbers.add((record.partner_id.mobile, record.partner_id.mobile))
                if record.partner_id.phone:
                    phone_numbers.add((record.partner_id.phone, record.partner_id.phone))

            if model == 'calls.technians':
                if record.call_from:
                    phone_numbers.add((record.call_from, record.call_from))
                if record.partner_id.mobile:
                    phone_numbers.add((record.partner_id.mobile, record.partner_id.mobile))
                if record.partner_id.phone:
                    phone_numbers.add((record.partner_id.phone, record.partner_id.phone))
                if record.lead_id.phone:
                    phone_numbers.add((record.lead_id.phone, record.lead_id.phone))
                if record.applicant_id.partner_phone:
                    phone_numbers.add((record.applicant_id.partner_phone, record.applicant_id.partner_phone))
                if record.applicant_id.partner_mobile:
                    phone_numbers.add((record.applicant_id.partner_mobile, record.applicant_id.partner_mobile))

            if model == 'hr.employee':
                if record.mobile_phone:
                    phone_numbers.add((record.mobile_phone, record.mobile_phone))
                if record.work_phone:
                    phone_numbers.add((record.work_phone, record.work_phone))

            # Check if the lead has phone numbers
            if model == 'crm.lead':
                if record.phone:
                    phone_numbers.add((record.phone, record.phone))
                if record.mobile:
                    phone_numbers.add((record.mobile, record.mobile))
                if record.partner_id.mobile:
                    phone_numbers.add((record.partner_id.mobile, record.partner_id.mobile))
                if record.partner_id.phone:
                    phone_numbers.add((record.partner_id.phone, record.partner_id.phone))

        # Return the list of phone numbers as options
        return list(phone_numbers)

    @api.onchange('mobile_number')
    def _onchange_mobile_number(self):
        if self.mobile_number:
            self.mobile = self.mobile_number

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.mobile = self.user_id.mobile or self.user_id.phone

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + ' '
            message_string = message_string[:(len(message_string))]
            number = self.mobile
            link = "https://web.whatsapp.com/send?phone=" + number
            send_msg = {
                'type': 'ir.actions.act_url',
                'url': link + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,

            }
            if (self.record_id):
                message = self.env['mail.message'].create({
                    'model': self.model,
                    'res_id': self.record_id,
                    'body': message_string,
                    'subtype_id': self.env.ref('mail.mt_note').id,
                })
            return send_msg
