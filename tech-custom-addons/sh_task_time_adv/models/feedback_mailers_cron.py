from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _budget_issues_feedback_cron(self):        
        contacts = self.search([])
        for contact in contacts:
            print('----contacts--XXXXX--', contacts)
            if contact:
                template = self.env.ref('sh_task_time_adv.budget_issues_feed_id') #render email template
                print('template--', template)
                template.send_mail(contact.id, force_send=True)
                print('==temp==', template)
        return True
