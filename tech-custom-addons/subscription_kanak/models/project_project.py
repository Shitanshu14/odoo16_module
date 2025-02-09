from odoo import fields, models, api

class Project(models.Model):
    _inherit = 'project.project'
    _description = 'Project'
    
    project_service_ids = fields.Many2many('product.product',string="Services",domain="['&', ('detailed_type', '=', 'service'), ('sale_ok', '=', 1)]")
    # project_service_ids = fields.Many2many('product.product',string="Services",domain="['&', ('detailed_type', '=', 'service'), ('sale_ok', '=', 1)]",compute='_compute_service_ids',store=True)
    
    subscription_id = fields.Many2one('subscription.subscription',string='Subscription',domain="[('project_id', '=', False)]")
    
    # subscription_line_ids = fields.Many2many('subscription.line',string='Subscriptions',compute='_compute_subscription_ids')

    def write(self, vals):
        if vals.get('description'):
            self.message_post(body=f"Description: {self.description} <i class='o_TrackingValue_separator fa fa-long-arrow-right mx-1 text-600' style='vertical-align: middle;' title='Changed' role='img' aria-label='Changed'></i> {vals.get('description')}")

        return super(Project, self).write(vals)



    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     raise ValidationError('this works')
    # def _compute_subscription_ids(self):
    #     for record in self:
    #         subscription_lines = self.env['subscription.line'].search(
    #             [('project_id', '=', self.id)])
    #         subscription_line_ids = []
    #         for subscription_line in subscription_lines:
    #             service_id = subscription_line.id
    #             subscription_line_ids.append((service_id))
    #     record.subscription_line_ids = [(6, 0, subscription_line_ids)]

    # @api.depends('subscription_id')
    # def _compute_service_ids(self):
    #     for record in self:
    #         subscription_lines = self.env['subscription.line'].search(
    #             [('project_id', '=', record.id)])
    #         # print("subscription_lines------------------",subscription_lines.name)
    #         service_ids = []
    #         for subscription_line in subscription_lines:
    #             service_id = subscription_line.product_id.id
    #             service_ids.append((service_id))
    #         record.project_service_ids = [(6, 0, service_ids)]

    # # subscription_line_ids = fields.Many2one('subscription.line',string='Subscription Line')

    # @api.onchange('subscription_id')
    # def _compute_project_services(self):
    #     related_subscription = self.env['subscription.subscription'].search([('id', '=', self.subscription_id.id)])
    #     self.write({'description':related_subscription.id})

    #     if(related_subscription):
    #         service_ids = []
    #         for subscription_line_ids in related_subscription.subscription_line_ids:
    #             service_id = subscription_line_ids.product_id
    #             service_ids.append((service_id))
    #         product_ids = [record.id for record in service_ids if record.id]
    #         self.write({'project_service_ids':product_ids})
        #       service_id = subscription_line_ids.product_id
        #       service_ids.append((service_id))
        #     self.write({
        #     'project_service_ids': service_ids
        # })
              
              
    # @api.onchange('team_member_ids')
    # def _onchange_team_members(self):
    #     related_project_team  = self.env['project.team.technians'].search([('id', '=', self.project_team_id.id)])
    #     team_members = []
    #     for member_id in self.team_member_ids.ids:
    #         team_members.append((member_id))
    #     related_project_team.write({
    #         'team_member_ids': team_members
    #     })
    # @api.depends('')
    # def _compute_services(self):
    #     main_model_record = self.env['subscription.subscription'].browse(main_model_id)
