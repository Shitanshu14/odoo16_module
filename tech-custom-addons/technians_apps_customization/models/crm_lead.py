from odoo import fields, models, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
import ast


class CRMLead(models.Model):
    _inherit = 'crm.lead'
    _description = 'CRM Lead'

    campaign_id = fields.Many2one(ondelete='set null',tracking=True)
    medium_id = fields.Many2one(ondelete='set null',tracking=True)
    source_id = fields.Many2one(ondelete='set null',tracking=True)

    lead_no_of_employees = fields.Selection([('1', 'Self-employed'), ('2', '1-10 employees'), ('3', '11-50 employees'),('4','51-200 employees'),('5','201-500 employees'),('6','501-1000 employees'),('7','1001-5000 employees'),('8','5001-10,000 employees'),('9','10,001+ employees'),('10','Unknown')],string="No. of Employees",store=True,readonly=False,tracking=True)
    lead_industry_id = fields.Many2one('res.partner.industry', string = "Industry",tracking=True)
    lead_status_id = fields.Many2one('lead.status', string = "Lead Status[Deprecated]",tracking=True)
    lead_status_ids = fields.Many2many('lead.status', string = "Lead Status",tracking=True)
    lead_jobrole_id = fields.Many2one('job.roles', string = "Job Role",tracking=True)
    lead_sub_status = fields.Char(string="Lead Sub Status[Deprecated]",tracking=True)
    lead_dob = fields.Date(string="Date of Birth",tracking=True)
    lead_addition_source = fields.Char(string="Lead Addition Source[Deprecated]",tracking=True)
    lead_source = fields.Selection([('1', 'Email Marketing'), ('2', 'Website - SSC India'), ('3', 'Website - Technians'),('4','Facebook'),('5','Data CC'),('6','Linkedin'),('7','Cold Call'),('8','Apollo'),('9','Reference'),('10','Social Media'),('11','fundoodata'),('12','JustDial'),('13','Sulekha'),('14','Other'),('15','Zomato'),('16','Upwork'),('17','Google Ads'),('18','Phone Call')],string="Lead Source",store=True,readonly=False,tracking=True)
    lead_assigned_to = fields.Char(string="Lead Assigned to[Deprecated]",tracking=True)
    lead_office_phone = fields.Char(string="Office Phone",tracking=True)
    lead_linkedin_url = fields.Char(string="Linkedin URL",tracking=True)
    lead_ads_group = fields.Char(string="Ads Group",tracking=True)
    lead_utm_device = fields.Char(string="UTM Device",tracking=True)
    lead_utm_device_model = fields.Char(string="UTM Device Model",tracking=True)
    lead_google_gclid = fields.Char(string="Google GCLID",tracking=True)
    lead_first_utm_campaign = fields.Char(string="First UTM Campaign",tracking=True)
    lead_first_utm_medium = fields.Char(string="First UTM Medium",tracking=True)
    lead_first_utm_source = fields.Char(string="First UTM Source",tracking=True)
    lead_first_utm_term = fields.Char(string="First UTM Term",tracking=True)
    lead_first_utm_content = fields.Char(string="First UTM Content",tracking=True)
    lead_utm_term = fields.Char(string="UTM Term",tracking=True)
    lead_utm_placement = fields.Char(string="UTM Placement",tracking=True)
    lead_utm_content = fields.Char(string="UTM Content",tracking=True)
    lead_utm_lp_url = fields.Char(string="UTM LP URL",tracking=True)
    lead_utm_organic_source_url = fields.Char(string="UTM Organic Source URL",tracking=True)
    lead_first_referral_url = fields.Char(string="First Referral URL",tracking=True)
    lead_last_webpage_visited = fields.Char(string="Last Webpage Visited",tracking=True)
    lead_last_referral_url = fields.Char(string="Last Referral URL",tracking=True)
    lead_interaction_source = fields.Char(string="Interaction Source",default="ERP",tracking=True)
    lead_ga_client_id = fields.Char(string="GA Client Id",tracking=True)
    lead_adposition = fields.Char(string="AD Position",tracking=True)

    lead_handl_url = fields.Char(string='Handl URL')
    lead_handl_ref_domain = fields.Char(string='Handlref Domain')
    lead_handl_url_base = fields.Char(string='Handl URL Base')
    lead_organic_source_str = fields.Char(string='Organic Source Str')
    lead_traffic_source = fields.Char(string='Traffic Source')
    lead_utm_matchtype = fields.Char(string='UTM Matchtype')
    lead_visitor_geo_state = fields.Char(string='Visitor Geo State')
    lead_first_traffic_source = fields.Char(string='First Traffic Source')
    # Presales Person field 27th June 2024
    lead_presales_user_id = fields.Many2one('res.users',string="Pre-sales Person",tracking=True)

    def create_job_applicant(self):
        self.ensure_one()
        job_position = 'Created From Lead'
        return {
            'type': 'ir.actions.act_window',
            'name': _('Job Applicant'),
            'view_mode': 'form',
            'res_model': 'applicant.job.wizard',
            'target': 'new',
            'context': {
                'default_name': self.contact_name,
                'default_subject': f"{self.contact_name} [{job_position}]",
                'default_email_from': self.email_from if self.email_from else '',
                'default_phone': self.phone if self.phone else ''
            },

        }

    start_date = fields.Datetime('Start Call Date', help=' Call Reminder Start  Date/Time')
    stop_date = fields.Datetime('Stop Call Date', help='Call Reminder Stop Call Date/time')
    show_date_fields = fields.Boolean(string='Show Date Fields')

    @api.onchange('lead_status_ids')
    def _onchange_tag_ids(self):
        crm_tag_ids = ast.literal_eval(
            self.env['ir.config_parameter'].sudo().get_param('technians_apps_customization.crm_tag_ids', '[]')
        )
        if crm_tag_ids:
            for crm in self:
                matching_categ_ids = set(crm.lead_status_ids.ids) & set(crm_tag_ids)
                crm.show_date_fields = bool(matching_categ_ids)
        else:
            self.show_date_fields = False

    def create_event_for_call_reminder(self):
        for lead in self:
            user_id = lead.user_id.id if lead.user_id else self.env.user.id
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_call').id,
                'res_model_id': self.env.ref('crm.model_crm_lead').id,
                'res_id': lead.id,
                'summary': 'Callback Reminder',
                'date_deadline': fields.Date.today() + timedelta(days=1),
                'user_id': user_id,
            })
            self.env['calendar.event'].sudo().create({
                'name': 'Callback Reminder for Lead ' + lead.name,
                'start': self.start_date,
                'stop': self.stop_date,
                # 'partner_ids': [(4, lead.partner_id.id)],
                'allday': False,
            })

    def write(self, vals):
        res = super(CRMLead, self).write(vals)

        if 'lead_status_ids' in vals:
            crm_tag_ids = ast.literal_eval(
                self.env['ir.config_parameter'].sudo().get_param('technians_apps_customization.crm_tag_ids', '[]')
            )
            if crm_tag_ids:
                for lead in self:
                    if any(tag.id in crm_tag_ids for tag in lead.lead_status_ids):
                        lead.create_event_for_call_reminder()
        return res

    @api.model
    def create(self, vals):
        if 'source_id' not in vals or not vals['source_id']:
            lead_organic_source_str = vals.get('lead_organic_source_str')
            if lead_organic_source_str:
                custom_source = self.env['utm.source'].search([('name', '=', lead_organic_source_str)], limit=1)
                if not custom_source:
                    custom_source = self.env['utm.source'].create({'name': lead_organic_source_str})
                vals['source_id'] = custom_source.id
        result = super(CRMLead, self).create(vals)
        return result
    
    @api.onchange('lead_no_of_employees')
    def employees_map(self):
        """
            Employees map on Customer/Partner,
        """
        for rec in self:
            if rec.lead_no_of_employees:
                rec.partner_id.contact_no_of_employees = rec.lead_no_of_employees
            if rec.lead_industry_id:
                rec.partner_id.contact_industry_id = rec.lead_industry_id.id
            if rec.lead_status_ids:
                rec.partner_id.contact_leadstatus_ids = rec.lead_status_ids.ids
            if rec.lead_sub_status:
                rec.partner_id.contact_sub_status = rec.lead_sub_status
            if rec.lead_dob:
                rec.partner_id.contact_dob = rec.lead_dob
            if rec.lead_source:
                rec.partner_id.contact_source = rec.lead_source
            if rec.lead_jobrole_id:
                rec.partner_id.contact_jobrole_id = rec.lead_jobrole_id.id
            if rec.lead_office_phone:
                rec.partner_id.contact_office_phone = rec.lead_office_phone
            if rec.email_cc:
                rec.partner_id.contact_email_cc = rec.email_cc
            if rec.lead_linkedin_url:
                rec.partner_id.contact_linkedin_url = rec.lead_linkedin_url
            # if rec.lead_jobtitle:
            #     rec.partner_id.contact_no_of_employees = rec.lead_jobtitle
            if rec.lead_ads_group:
                rec.partner_id.contact_ads_group = rec.lead_ads_group
            if rec.lead_utm_placement:
                rec.partner_id.contact_utm_placement = rec.lead_utm_placement
            if rec.lead_utm_device:
                rec.partner_id.contact_utm_device = rec.lead_utm_device
            if rec.lead_utm_device_model:
                rec.partner_id.contact_utm_device_model = rec.lead_utm_device_model 
            if rec.lead_google_gclid:
                rec.partner_id.contact_google_gclid = rec.lead_google_gclid 
            if rec.lead_first_utm_campaign:
                rec.partner_id.contact_first_utm_campaign = rec.lead_first_utm_campaign
            if rec.lead_first_utm_medium:
                rec.partner_id.contact_first_utm_medium = rec.lead_first_utm_medium
            if rec.lead_first_utm_source:
                rec.partner_id.contact_first_utm_source = rec.lead_first_utm_source
            if rec.lead_first_utm_term:
                rec.partner_id.contact_first_utm_term = rec.lead_first_utm_term
            if rec.lead_first_utm_content:
                rec.partner_id.contact_first_utm_content = rec.lead_first_utm_content
            if rec.lead_utm_term:
                rec.partner_id.contact_utm_term = rec.lead_utm_term
            if rec.lead_utm_content:
                rec.partner_id.contact_utm_content = rec.lead_utm_content
            if rec.lead_utm_lp_url:
                rec.partner_id.contact_utm_lp_url = rec.lead_utm_lp_url
            if rec.lead_utm_organic_source_url:
                rec.partner_id.contact_utm_organic_source_url = rec.lead_utm_organic_source_url 
            if rec.lead_first_referral_url:
                rec.partner_id.contact_first_referral_url = rec.lead_first_referral_url 
            if rec.lead_last_webpage_visited:
                rec.partner_id.contact_last_webpage_visited = rec.lead_last_webpage_visited 
            if rec.lead_last_referral_url:
                rec.partner_id.contact_last_referral_url = rec.lead_last_referral_url 
            if rec.lead_interaction_source:
                rec.partner_id.contact_interaction_source = rec.lead_interaction_source 
            if rec.lead_ga_client_id:
                rec.partner_id.contact_ga_client_id = rec.lead_ga_client_id 
            if rec.medium_id:
                rec.partner_id.contact_hc_medium_id = rec.medium_id.id 
            if rec.campaign_id:
                rec.partner_id.contact_hc_campaign_id = rec.campaign_id.id 
            if rec.source_id:
                rec.partner_id.contact_hc_source_id = rec.source_id.id 
            if rec.lead_adposition:
                rec.partner_id.contact_adposition = rec.lead_adposition   
                

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        
        result = super(CRMLead, self)._prepare_customer_values(partner_name=partner_name, is_company=is_company,
                                                               parent_id=parent_id)
        result.update({
            'contact_no_of_employees': self.lead_no_of_employees,
            'contact_industry_id': self.lead_industry_id.id,
            'contact_leadstatus_id': self.lead_status_id.id,
            'contact_leadstatus_ids': self.lead_status_ids.ids,
            'contact_sub_status': self.lead_sub_status,
            'contact_dob': self.lead_dob,
            'contact_source': self.lead_source,
            'contact_jobrole_id': self.lead_jobrole_id.id,
            'contact_office_phone': self.lead_office_phone,
            'contact_email_cc': self.email_cc,
            'contact_linkedin_url': self.lead_linkedin_url,
            'contact_ads_group': self.lead_ads_group,
            'contact_utm_placement': self.lead_utm_placement,
            'contact_utm_device': self.lead_utm_device,
            'contact_utm_device_model': self.lead_utm_device_model,
            'contact_google_gclid': self.lead_google_gclid,
            'contact_first_utm_campaign': self.lead_first_utm_campaign,
            'contact_first_utm_medium': self.lead_first_utm_medium,
            'contact_first_utm_source': self.lead_first_utm_source,
            'contact_first_utm_term': self.lead_first_utm_term,
            'contact_first_utm_content': self.lead_first_utm_content,
            'contact_utm_term': self.lead_utm_term,
            'contact_utm_content': self.lead_utm_content,
            'contact_utm_lp_url': self.lead_utm_lp_url,
            'contact_utm_organic_source_url': self.lead_utm_organic_source_url,
            'contact_first_referral_url': self.lead_first_referral_url,
            'contact_last_webpage_visited': self.lead_last_webpage_visited,
            'contact_last_referral_url': self.lead_last_referral_url,
            'contact_interaction_source': self.lead_interaction_source,
            'contact_ga_client_id': self.lead_ga_client_id,
            'contact_hc_medium_id': self.medium_id.id,
            'contact_hc_campaign_id': self.campaign_id.id,
            'contact_hc_source_id': self.source_id.id,
            'contact_adposition': self.lead_adposition,
            
            'contact_handl_url': self.lead_handl_url,
            'contact_handl_ref_domain': self.lead_handl_ref_domain,
            'contact_handl_url_base': self.lead_handl_url_base,
            'contact_organic_source_str': self.lead_organic_source_str,
            'contact_traffic_source': self.lead_traffic_source,
            'contact_utm_matchtype': self.lead_utm_matchtype,
            'contact_first_traffic_source': self.lead_first_traffic_source,
            })
        return result
   
    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         # Call the parent method to update the partner details
    #         super(CRMLead, self)._onchange_partner_id()

    #         # Update additional fields in the partner (company)
    #         self.partner_id.write({
    #         'contact_ads_group': self.lead_ads_group,
    #         'contact_utm_placement': self.lead_utm_placement,
    #         'contact_utm_device': self.lead_utm_device,
    #         'contact_utm_device_model': self.lead_utm_device_model,
    #         'contact_google_gclid': self.lead_google_gclid,
    #         'contact_first_utm_campaign': self.lead_first_utm_campaign,
    #         'contact_first_utm_medium': self.lead_first_utm_medium,
    #         'contact_first_utm_source': self.lead_first_utm_source,
    #         'contact_first_utm_term': self.lead_first_utm_term,
    #         'contact_first_utm_content': self.lead_first_utm_content,
    #         'contact_utm_term': self.lead_utm_term,
    #         'contact_utm_content': self.lead_utm_content,
    #         'contact_utm_lp_url': self.lead_utm_lp_url,
    #         'contact_utm_organic_source_url': self.lead_utm_organic_source_url,
    #         'contact_first_referral_url': self.lead_first_referral_url,
    #         'contact_last_webpage_visited': self.lead_last_webpage_visited,
    #         'contact_last_referral_url': self.lead_last_referral_url,
    #         'contact_interaction_source': self.lead_interaction_source,
    #         'contact_ga_client_id': self.lead_ga_client_id,
    #         'contact_hc_medium_id': self.medium_id.id,
    #         'contact_hc_campaign_id': self.campaign_id.id,
    #         'contact_hc_source_id': self.source_id.id,
    #         'contact_adposition': self.lead_adposition,
    #             # Add more fields as needed
    #         })
            
            
    def tech_send_lead_birthday_email(self):
        records = self.search([])
        for record in records:
            dob = record.lead_dob
            if dob:
                if self.is_birthday_today(dob):
                    mail_template = self.env.ref('technians_apps_customization.tech_lead_birthday_email_tpl')
                    mail_template.send_mail(record.id, force_send=True)

    @staticmethod
    def is_birthday_today(birthdate):
        today = datetime.date.today()
        return birthdate.month == today.month and birthdate.day == today.day

    def action_open_linkedin(self):
        self.ensure_one()
        if self.lead_linkedin_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.lead_linkedin_url,
                'target': 'new',
            }
    
    def action_send_crm_mail(self):
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        
        email_context = {
                    'default_model': 'crm.lead',
                    'default_res_id': self.id,
                    'default_composition_mode': 'comment',
                    'custom_layout': "mail.mail_notification_paynow",
                    'force_email': False,
                                
            }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': email_context,
        }
class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def send_daily_lead_report(self):
        

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        today = date.today()
        leads = self.env['crm.lead'].search([
            ('create_date', '>=', today.strftime('%Y-%m-%d 00:00:00')),
            ('create_date', '<=', today.strftime('%Y-%m-%d 23:59:59'))
        ])
        if len(leads) == 0:
            return
        source_leads = {}
        int_source_leads = {}
        for lead in leads:
            source_name = lead.source_id.name if lead.source_id else 'Unknown'
            int_source_name = lead.lead_interaction_source if lead.lead_interaction_source else 'Unknown'
            if source_name in source_leads:
                source_leads[source_name] += 1
            else:
                source_leads[source_name] = 1
            
            if int_source_name in int_source_leads:
                int_source_leads[int_source_name] += 1
            else:
                int_source_leads[int_source_name] = 1

        source_leads_html = """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #743F74; color: white;">
                    <th style="padding: 8px; text-align: left;">Source</th>
                    <th style="padding: 8px; text-align: left;">Number of Leads</th>
                </tr>
            """
        for source, count in source_leads.items():
            source_leads_html += f"""
                <tr>
                    <td style="padding: 8px; text-align: left;">{source}</td>
                    <td style="padding: 8px; text-align: left;">{count}</td>
                </tr>
                """
        source_leads_html += "</table>"
        int_source_leads_html = """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #743F74; color: white;">
                    <th style="padding: 8px; text-align: left;">Interaction Source</th>
                    <th style="padding: 8px; text-align: left;">Number of Leads</th>
                </tr>
            """
        for int_source, int_count in int_source_leads.items():
            int_source_leads_html += f"""
                <tr>
                    <td style="padding: 8px; text-align: left;">{int_source}</td>
                    <td style="padding: 8px; text-align: left;">{int_count}</td>
                </tr>
                """
        int_source_leads_html += "</table>"
        sales_admin_group = self.env.ref('sales_team.group_sale_manager')

        users = self.env['res.users'].search([('groups_id', 'in', sales_admin_group.id)])
        # raise ValidationError(users)
        for user in users:
            if not user.email:
                _logger.warning(f"User {user.name} has no email address.")
                continue

            subject = f"Daily Sales Lead Update, {today.strftime('%Y-%m-%d')}"

            body_html = f"""
                    <p>Hi {user.name},</p>
                    <p>Please find below the Lead status report for today:</p>
                    {source_leads_html}
                    {int_source_leads_html}
                """
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_to': user.email,
                'email_from': 'support@technians.com',
                'reply_to': 'support@technians.com',
            }

            self.env['mail.mail'].create(mail_values).send()

    