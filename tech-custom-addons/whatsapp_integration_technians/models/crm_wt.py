from odoo import _, models


class WhatsappCrm(models.Model):
    _inherit = 'crm.lead'

    def crm_whatsapp(self):
        user_name = self.partner_id.name if self.partner_id else self.name
        return {
            'type': 'ir.actions.act_window',
            'name': _('Whatsapp Message'),
            'res_model': 'whatsapp.message.wizard',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_user_id': self.partner_id.id if self.partner_id else False,
                'default_user_name': user_name,
                'default_model': 'crm.lead',
                'default_record_id': self.id,
                'default_mobile': self.partner_id.phone or self.partner_id.mobile if self.partner_id else False,
            },
        }

