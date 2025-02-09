from odoo import _, models


class WhatsappRecruitment(models.Model):
    _inherit = 'hr.applicant'
    
    def recruitment_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_model':'hr.applicant','default_record_id':self.id,'default_user_name': self.partner_name,'default_mobile':self.partner_mobile or self.partner_phone},
                }

class WhatsappEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def employee_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_model':'hr.employee','default_record_id':self.id,'default_user_name': self.name,'default_mobile':self.mobile_phone or self.work_phone},
                }