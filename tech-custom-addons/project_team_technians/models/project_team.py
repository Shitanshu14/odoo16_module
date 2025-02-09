from odoo import models, fields, api


class ProjectTeam(models.Model):
    _name = 'project.team.technians'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Team'

    # Define additional fields in Project Model
    name = fields.Char(string='Name', required=True)
    team_member_ids = fields.Many2many('res.users', string='Team Members', domain=[('share', '=', False)],
                                       ondelete="cascade",
                                       help='The Project team is the group of people responsible for executing the tasks and working together towards a common goal by producing deliverables outlined in the project plan and schedule, as directed by the project manager, at whatever level of effort or participation defined for them.')
    account_manager_id = fields.Many2one('res.users', domain=[('share', '=', False)], string='Account Manager',
                                         help='Account managers act as client advocates and work with Project Manager, Project Team, and internal departments to ensure that client needs are understood and satisfied. They may assist with making sales, handling client complaints, collecting and analyzing data, and improving the overall customer experience.')
    project_manager_id = fields.Many2one('res.users', string='Project Manager',
                                         help='A Project Manager is in charge of ensuring their teams complete all projects, tasks, and milestones on time and within budget. They manage individual tasks for their respective teams with keen attention to detail to avoid any unpleasant surprises.')
    active = fields.Boolean(string='Active', default=True)

#shitanshu change here three method
    @api.model
    def create(self, vals):
        """ Override create method to add team members as followers when creating a new record """
        record = super(ProjectTeam, self).create(vals)
        if 'team_member_ids' in vals:
            members = record.team_member_ids
            if members:
                record.message_subscribe(partner_ids=members.mapped('partner_id').ids)
        return record

    def write(self, vals):
        """ Override write method to manage followers when team members are added or removed """
        res = super(ProjectTeam, self).write(vals)
        if 'team_member_ids' in vals:
            for record in self:
                members = record.team_member_ids
                if members:
                    # Add new members as followers
                    record.message_subscribe(partner_ids=members.mapped('partner_id').ids)
        return res

    # description = fields.Text(string='Description')
    # @api.onchange('project_manager_id')
    # def _onchange_project_manager(self):
    #     if(self.project_manager_id):
    #         team_members = self.team_member_ids.ids
    #         team_members.append((self.project_manager_id.id))
    #         self.write({
    #                 'team_member_ids': team_members
    #             })

    @api.onchange('project_manager_id', 'account_manager_id')
    def _onchange_managers(self):
        # Ensure both Project Manager and Account Manager are in the team members
        team_members = set(self.team_member_ids.ids)  # Using a set to avoid duplicates

        if self.project_manager_id:
            team_members.add(self.project_manager_id.id)

        if self.account_manager_id:
            team_members.add(self.account_manager_id.id)

        self.update({'team_member_ids': [(6, 0, list(team_members))]})
