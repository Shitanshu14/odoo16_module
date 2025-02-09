from odoo import models, fields, api
from odoo.exceptions import except_orm, ValidationError
from datetime import datetime
class DeadLineReminder(models.Model):
    _inherit = "res.users"    
    
    @api.model
    def cron_project_not_updated(self):

        count_projects_missing_am = self.env['project.project'].search_count([('account_manager_id', '=', False), ('stage_id.fold' ,'=',False)])
        count_projects_missing_pm = self.env['project.project'].search_count([('user_id', '=', False), ('stage_id.fold' ,'=',False)])
        count_projects_missing_partner = self.env['project.project'].search_count([('partner_id', '=', False), ('stage_id.fold' ,'=',False)])
        count_projects_missing_deadline = self.env['project.project'].search_count([('date_start', '=', False),('date', '=', False), ('stage_id.fold' ,'=',False)])
        count_projects_missing_team = self.env['project.project'].search_count([('project_team_id', '=', False), ('stage_id.fold' ,'=',False)])
        if count_projects_missing_am == 0 and count_projects_missing_deadline == 0 and count_projects_missing_partner == 0 and count_projects_missing_pm == 0 and count_projects_missing_team == 0 :
            return True
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        action_id_missing_partner = self.env['ir.actions.act_window'].search([('name', '=', 'Projects without Customer')])
        action_id_missing_am = self.env['ir.actions.act_window'].search([('name', '=', 'Projects without Account Manager')])
        action_id_missing_pm = self.env['ir.actions.act_window'].search([('name', '=', 'Projects without Project Manager')])
        action_id_missing_end_date = self.env['ir.actions.act_window'].search([('name', '=', 'Projects without End date')])
        action_id_missing_pt = self.env['ir.actions.act_window'].search([('name', '=', 'Project Team Missing')])
        # action_id_no_account_manager = self.env.ref('action_project_without_account_manager',raise_if_not_found=False)
        # raise ValidationError(action_id_no_account_manager)
        # action_id_no_partner = self.env.ref('action_project_without_project_manager', raise_if_not_found=False)
        # action_id_no_deadline = self.env.ref('action_project_without_end_date', raise_if_not_found=False)
        email_from = '"Odoobot" <support@technians.com>'
        body_html = f"""\
                  <p>Hello,</p>
                  <p>The following projects are not up to date </p>
                  <table style="border-collapse: collapse; width: 100%;" border="1">
                      <tr style="background-color: #743F74; color: white;">
                          <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Category</th>
                          <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Count</th>
                          <th style="border: 1px solid #dddddd; text-align: left; padding: 8px; text-align: center;">Action</th>
                      </tr>
                      <tr>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">Projects without account manager</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">{count_projects_missing_am}</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; text-align: center;">
                              <a href="{base_url}/web#action={action_id_missing_am.id}" style="background-color: #743F74; color: white; padding: 5px 10px; border: none; cursor: pointer; text-decoration: none;">View Projects</a>
                          </td>
                      </tr>
                      <tr>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">Projects without project manager</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">{count_projects_missing_pm}</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; text-align: center;">
                              <a href="{base_url}/web#action={action_id_missing_pm.id}" style="background-color: #743F74; color: white; padding: 5px 10px; border: none; cursor: pointer; text-decoration: none;">View Projects</a>
                          </td>
                      </tr>
                      <tr>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">Projects without partner</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">{count_projects_missing_partner}</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; text-align: center;">
                              <a href="{base_url}/web#action={action_id_missing_partner.id}" style="background-color: #743F74; color: white; padding: 5px 10px; border: none; cursor: pointer; text-decoration: none;">View Projects</a>
                          </td>
                      </tr>
                      
                      <tr>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">Projects without End Date</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">{count_projects_missing_deadline}</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; text-align: center;">
                              <a href="{base_url}/web#action={action_id_missing_end_date.id}" style="background-color: #743F74; color: white; padding: 5px 10px; border: none; cursor: pointer; text-decoration: none;">View Projects</a>
                          </td>
                      </tr>
                      <tr>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">Projects without Team</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">{count_projects_missing_team}</td>
                          <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; text-align: center;">
                              <a href="{base_url}/web#action={action_id_missing_pt.id}" style="background-color: #743F74; color: white; padding: 5px 10px; border: none; cursor: pointer; text-decoration: none;">View Projects</a>
                          </td>
                      </tr>
                  </table>
                  <p>Kindly update the necessary details.</p>
                  """

        users = self.env['res.users'].search([('groups_id', 'in', self.env.ref('project.group_project_manager').id),])
        for user in users:
            subject = f"{user.name}: Projects are not up to date"
        # _logger.info("Number of projects with no account manager: %s", count_projects_no_manager)
        # _logger.info("Number of projects with no partner: %s", count_projects_no_partner)
        # _logger.info("Number of projects with no End Date: %s", count_projects_no_deadline)
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': email_from,
                'email_to': user.login,
                'reply_to': email_from
            }
            self.env['mail.mail'].create(mail_values).send()



            
        
