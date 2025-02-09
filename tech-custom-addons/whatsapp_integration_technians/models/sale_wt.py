from odoo import _, models, fields, api

class WhatsappSale(models.Model):
    _inherit = 'sale.order'

    def sale_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_template_id': self.env.ref('whatsapp_integration_technians.sales_whatsapp_template').id,'default_model':'sale.order','default_record_id':self.id,'default_user_name': self.name,'default_mobile':self.partner_id.mobile or self.partner_id.phone},
                }

 




