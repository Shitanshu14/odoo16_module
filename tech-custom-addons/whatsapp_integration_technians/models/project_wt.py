from odoo import _, models


class WhatsappProject(models.Model):
    _inherit = 'project.project'
    
    def project_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_mobile': self.partner_id.mobile or self.partner_id.phone,'default_model':'project.project','default_record_id':self.id,'default_user_name': self.name},
                } 