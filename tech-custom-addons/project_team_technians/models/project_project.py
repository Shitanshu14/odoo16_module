from odoo import models, fields, api
from odoo.exceptions import except_orm, ValidationError
from datetime import datetime


class MyProject(models.Model):
    _inherit = 'project.project'
    project_team_id = fields.Many2one('project.team.technians', string='Project Team',
                                      help='The Project team is the group of people responsible for executing the tasks and working together towards a common goal by producing deliverables outlined in the project plan and schedule, as directed by the project manager, at whatever level of effort or participation defined for them.')
    team_member_ids = fields.Many2many('res.users', string='Team Members', domain="[('share', '=', False)]", ondelete="cascade", help='')
    account_manager_id = fields.Many2one('res.users', domain=[('share', '=', False)],string='Account Manager',
                                         help='Account managers act as client advocates and work with Project Manager, Project Team, and internal departments to ensure that client needs are understood and satisfied. They may assist with making sales, handling client complaints, collecting and analyzing data, and improving the overall customer experience.')

    def write(self, vals):
        res = super(MyProject, self).write(vals)

        if 'stage_id' in vals:
            project_stage_id = vals['stage_id']

            settings = self.env['res.config.settings'].sudo().get_values()
            stage_ids = settings.get('archive_stage_ids', [(6, 0, [])])[0][2]
            other_ids = settings.get('active_stage_ids', [(6, 0, [])])[0][2]

            if self.project_team_id:
                if project_stage_id in stage_ids:
                    self.project_team_id.sudo().write({'active': False})
                if project_stage_id in other_ids:
                    self.project_team_id.sudo().write({'active': True})

                    #Change From my shitanshu in this method

        if 'team_member_ids' in vals or 'project_team_id' in vals:
            for record in self:
                team_members = record.project_team_id.team_member_ids.mapped('partner_id').ids
                record.message_subscribe(partner_ids=team_members)
                if 'team_member_ids' in vals:
                    members = record.team_member_ids
                    if members:
                        record.message_subscribe(partner_ids=members.mapped('partner_id').ids)

        if vals.get('account_manager_id'):
            account_manager = self.env['res.users'].browse(vals['account_manager_id'])
            self.message_subscribe(partner_ids=[account_manager.partner_id.id])
            if self.project_team_id and account_manager:
                if account_manager not in self.project_team_id.team_member_ids:
                    self.project_team_id.team_member_ids = [(4, account_manager.id)]


        if vals.get('user_id'):
            self._update_project_manager_in_team()

        if vals.get('team_member_ids'):
            self._update_project_team_in_team()

        return res

    # @api.onchange('project_team_id')
    # def _onchange_partner_id(self):
    #     if self.project_team_id:
    #         changes = {}
    #         if not self.user_id:
    #             changes['user_id'] = self.project_team_id.project_manager_id.id
    #         if not self.account_manager_id:
    #             changes['account_manager_id'] = self.project_team_id.account_manager_id.id
    #         changes['team_member_ids'] = [(6, 0, self.project_team_id.team_member_ids.ids)]
    #         self.write(changes)
    #     else:
    #         self.write({
    #             'team_member_ids': False
    #         })

    # Function to update team members of Project team from Single Project
    # @api.onchange('team_member_ids')
    # def _onchange_team_members(self):
    #     related_project_team = self.env['project.team.technians'].search([('id', '=', self.project_team_id.id)])
    #     team_members = []
    #     for member_id in self.team_member_ids.ids:
    #         team_members.append((member_id))
    #     related_project_team.write({
    #         'team_member_ids': team_members
    #     })

    def _update_project_team_in_team(self):
        for rec in self:
            if rec.project_team_id:
                myteam = rec.team_member_ids.ids
                if rec.user_id and rec.user_id.id not in myteam:
                    myteam.append(rec.user_id.id)
                if rec.account_manager_id and rec.account_manager_id.id not in myteam:
                    myteam.append(rec.account_manager_id.id)
                for member in myteam:
                    if member not in rec.team_member_ids.ids:
                        rec.team_member_ids = [(4, member)]
                    if member not in rec.project_team_id.team_member_ids.ids:
                        rec.project_team_id.team_member_ids = [(4, member)]


    def _update_project_manager_in_team(self):
        for rec in self:
            if rec.project_team_id:
                related_project_team = rec.project_team_id
                related_project_team.project_manager_id = rec.user_id.id
                user_id = rec.user_id.id
                team_members = rec.team_member_ids.ids
                if user_id not in team_members:
                    for team_member in team_members:
                        rec.write({
                            'team_member_ids': [(4, team_member)]
                        })

    # @api.onchange('user_id')
    # def _update_project_manager(self):
    #     for rec in self:
    #         if rec.project_team_id and rec.user_id:
    #             related_project_team = rec.project_team_id
    #             # Update the project manager
    #             related_project_team.project_manager_id = rec.user_id.id
    #
    #             # Update team members
    #             team_members = rec.team_member_ids.ids
    #             if rec.user_id.id not in team_members:
    #                 team_members.append(rec.user_id.id)
    #
    #             # Write changes to team_member_ids in one go
    #             rec.write({
    #                 'team_member_ids': [(6, 0, team_members)]
    #             })

    # @api.onchange('account_manager_id')
    # def _update_account_manager(self):
    #     for rec in self:
    #         if rec.project_team_id and rec.account_manager_id:
    #             related_project_team = rec.project_team_id
    #             # Update the account manager
    #             related_project_team.account_manager_id = rec.account_manager_id.id
                
    #             # Update team members
    #             team_members = rec.team_member_ids.ids
    #             if rec.account_manager_id.id not in team_members:
    #                 team_members.append(rec.account_manager_id.id)
    #                 # Subscribe the account manager to project followers
    #                 if rec.account_manager_id.partner_id:
    #                     rec.message_subscribe(partner_ids=[rec.account_manager_id.partner_id.id])

    #             # Write changes to team_member_ids in one go
    #             rec.write({
    #                 'team_member_ids': [(6, 0, team_members)]
    #             })

    # @api.onchange('user_id', 'account_manager_id')
    # def _update_project_manager(self):
    #     if self.project_team_id:
    #         related_project_team = self.env['project.team.technians'].search([('id', '=', self.project_team_id.id)])
    #         for rec in self:
    #             if (rec.user_id):
    #                 related_project_team.write({
    #                     'project_manager_id': rec.user_id.id
    #                 })
    #                 team_members = rec.team_member_ids.ids
    #                 team_members.append((self.user_id.id))
    #                 rec.write({
    #                     'team_member_ids': team_members
    #                 })
    #             if (rec.account_manager_id):
    #                 related_project_team.write({
    #                     'account_manager_id': rec.account_manager_id.id
    #                 })


    @api.model
    def reminder_cron_project_weekly_updates(self):
        if datetime.now().weekday() == 4:

            internal_group = self.env.ref('base.group_user')
            users = self.env['res.users'].search([('groups_id', 'in', [internal_group.id])])
            # raise ValidationError(users)
            for user in users:
                projects = self.search([('active', '=', True), ('account_manager_id', '=', user.id)])
                if not projects:
                    continue
                projects_data = []
                for project in projects:
                    projects_data.append({
                        'project_name': project.name,
                        'status_update_link': self._get_status_update_link(project),
                    })

                self.send_weekly_status_email(user.email, projects_data, user.name)

    def _get_status_update_link(self, project):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        status_update_link = f"{base_url}/web#action=497&active_id={project.id}&model=project.update&view_type=kanban&cids=1&menu_id=136"
        return status_update_link

    def send_weekly_status_email(self, email, projects_data, manager_name):
        if not email:
            return
        subject = "Weekly Project Status Update"
        body_html = f"""\
            <p>Hello {manager_name},</p>
            <p>Kindly update the weekly progress of your projects:</p>
            <table style="border-collapse: collapse; width: 100%;" border="1">
                <tr style="background-color: #743F74; color: white;">
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Project</th>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 8px;">Link</th>
                </tr>
        """

        for project_data in projects_data:
            body_html += f"""
                <tr>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">{project_data['project_name']}</td>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 8px; color: black;">
                        <a href="{project_data['status_update_link']}" style="background-color: #743F74; color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px;">Update Status</a>
                    </td>
                </tr>
            """

        body_html += """
            </table>
        </body>
        """

        mail_values = {
            'subject': subject,
            'body_html': body_html,
            'email_from': '',
            'email_to': email,
            # 'reply_to': 'Technians Softech Pvt Ltd Technians ERP <catchall@technians.com>',
        }

        try:
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
        except Exception:
            pass
