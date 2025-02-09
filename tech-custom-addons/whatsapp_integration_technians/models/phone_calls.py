from odoo import _, models

class WhatsappPhoneCalls(models.Model):
    _inherit = 'calls.technians'
    
    def calls_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_model':'calls.technians','default_record_id':self.id,'default_user_name': self.name,'default_mobile':self.call_from or self.partner_id.mobile or self.partner_id.phone or self.lead_id.phone or self.applicant_id.partner_phone or self.applicant_id.partner_mobile}
                } 