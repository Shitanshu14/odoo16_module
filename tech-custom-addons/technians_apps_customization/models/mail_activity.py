from odoo import fields, models, api

class MailActivity(models.Model):
    _inherit = 'mail.activity'
    _description = 'Activity'
    
    
    tech_activity_deadline = fields.Datetime('Deadline')
    
    @api.onchange('tech_activity_deadline')
    def _onchange_datetime_field(self):
        if self.tech_activity_deadline:
            self.date_deadline = fields.Date.context_today(self, timestamp=self.tech_activity_deadline)
        else:
            self.date_deadline = fields.Date.context_today(self)