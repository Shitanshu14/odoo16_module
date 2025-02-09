from odoo import api, exceptions, fields, models
import datetime
class ResPartner(models.Model):
    
 _inherit = 'res.partner'
 _description = 'Res Partner'
 
 contact_no_of_employees = fields.Selection([('1', 'Self-employed'), ('2', '1-10 employees'), ('3', '11-50 employees'),('4','51-200 employees'),('5','201-500 employees'),('6','501-1000 employees'),('7','1001-5000 employees'),('8','5001-10,000 employees'),('9','10,001+ employees'),('10','Unknown')],string="No. of Employees",store=True,readonly=False,tracking=True)
 contact_industry_id = fields.Many2one('res.partner.industry', string = "Contact Industry",tracking=True)
 contact_leadstatus_id = fields.Many2one('lead.status', string = "Lead Status[Deprecated]",tracking=True)
 contact_leadstatus_ids = fields.Many2many('lead.status', string = "Lead Status",tracking=True)
 contact_sub_status = fields.Char(string="Lead Sub Status",tracking=True)
 contact_dob = fields.Date(string="Date of Birth",tracking=True)
 contact_email_cc = fields.Char(string="Email CC",tracking=True)
 contact_linkedin_url = fields.Char(string="Linkedin URL",tracking=True)
 contact_addition_source = fields.Char(string="Lead Addition Source",tracking=True)
 contact_source = fields.Selection([('1', 'Email Marketing'), ('2', 'Website - SSC India'), ('3', 'Website - Technians'),('4','Facebook'),('5','Data CC'),('6','Linkedin'),('7','Cold Call'),('8','Apollo'),('9','Reference'),('10','Social Media'),('11','fundoodata'),('12','JustDial'),('13','Sulekha'),('14','Other'),('15','Zomato'),('16','Upwork'),('17','Google Ads'),('18','Phone Call')],string="Lead Source",store=True,readonly=False,tracking=True)
 contact_jobrole_id = fields.Many2one('job.roles', string = "Job Role",tracking=True)
 contact_office_phone = fields.Char(string="Office Phone",tracking=True)
#  contact_jobtitle = fields.Char(string="Role/Job Title")
 contact_ads_group = fields.Char(string="Ads Group",tracking=True)
 contact_utm_device = fields.Char(string="UTM Device",tracking=True)
 contact_utm_device_model = fields.Char(string="UTM Device Model",tracking=True)
 contact_google_gclid = fields.Char(string="Google GCLID",tracking=True)
 contact_first_utm_campaign = fields.Char(string="First UTM Campaign",tracking=True)
 contact_first_utm_medium = fields.Char(string="First UTM Medium",tracking=True)
 contact_first_utm_source = fields.Char(string="First UTM Source",tracking=True)
 contact_first_utm_term = fields.Char(string="First UTM Term",tracking=True)
 contact_first_utm_content = fields.Char(string="First UTM Content",tracking=True)
 contact_utm_term = fields.Char(string="UTM Term",tracking=True)
 contact_utm_placement = fields.Char(string="UTM Placement",tracking=True)
 contact_utm_content = fields.Char(string="UTM Content",tracking=True)
 contact_utm_lp_url = fields.Char(string="UTM LP URL",tracking=True)
 contact_utm_organic_source_url = fields.Char(string="UTM Organic Source URL",tracking=True)
 contact_first_referral_url = fields.Char(string="First Referral URL",tracking=True)
 contact_last_webpage_visited = fields.Char(string="Last Webpage Visited",tracking=True)
 contact_last_referral_url = fields.Char(string="Last Referral URL",tracking=True)
 contact_interaction_source = fields.Char(string="Interaction Source",tracking=True)
 contact_ga_client_id = fields.Char(string="GA Client Id",tracking=True) 
 contact_hc_medium_id = fields.Many2one('utm.medium', string = "UTM Medium",tracking=True)
 contact_hc_campaign_id = fields.Many2one('utm.campaign', string = "UTM Campaign",tracking=True)
 contact_hc_source_id = fields.Many2one('utm.source', string = "UTM Source",tracking=True)
 contact_medium_id = fields.Char(string="Medium",tracking=True) 
 contact_campaign_id = fields.Char(string="Campaign",tracking=True) 
 contact_source_id = fields.Char(string="Source",tracking=True) 
 contact_adposition = fields.Char(string="AD Position",tracking=True)
 
 active_projects = fields.Integer(string="Active Projects",tracking=True)
 inactive_projects = fields.Integer(string="Inactive Projects" ,tracking=True)
 contact_handl_url = fields.Char(string='Handl URL',tracking=True)
 contact_handl_ref_domain = fields.Char(string='Handlref Domain',tracking=True)
 contact_handl_url_base = fields.Char(string='Handl URL Base',tracking=True)
 contact_organic_source_str = fields.Char(string='Organic Source Str',tracking=True)
 contact_traffic_source = fields.Char(string='Traffic Source',tracking=True)
 contact_utm_matchtype = fields.Char(string='UTM Matchtype',tracking=True)
#  contact_visitor_geo_state = fields.Char(string='Visitor Geo State')
 contact_first_traffic_source = fields.Char(string='First Traffic Source',tracking=True)
 
 def _project_count(self):
        current_time = datetime.date.today()
        for rec in self:
            rec.active_projects = self.env['project.project'].search_count([('partner_id', '=', rec.id),
                                                                       ('date', '!=', False),
                                                                       ('stage_id.fold', '=', False),
                                                                       ('date', '>', current_time.strftime('%m-%d-%Y'))
                                                                       ])

 def _project_inactive_count(self):
        current_time = datetime.datetime.now()
        for rec in self:
            rec.inactive_projects = self.env['project.project'].search_count([('partner_id', '=', rec.id), ('date', '!=', False),('date', '<', current_time), ('stage_id.fold', '=', True)])
 @api.onchange('parent_id')
 def _onchange_parent_id(self):
    company_id = self.parent_id.id
    company_data = self.env['res.partner'].browse(company_id)
    if(company_data):
        if not self.contact_ads_group:
            self.contact_ads_group = company_data.contact_ads_group
        if not self.contact_utm_device:
            self.contact_utm_device = company_data.contact_utm_device
        if not self.contact_utm_device_model:
            self.contact_utm_device_model = company_data.contact_utm_device_model
        if not self.contact_google_gclid:
            self.contact_google_gclid = company_data.contact_google_gclid
        if not self.contact_first_utm_campaign:
            self.contact_first_utm_campaign = company_data.contact_first_utm_campaign
        if not self.contact_first_utm_medium:
            self.contact_first_utm_medium = company_data.contact_first_utm_medium
        if not self.contact_first_utm_source:
            self.contact_first_utm_source = company_data.contact_first_utm_source
        if not self.contact_first_utm_term:
            self.contact_first_utm_term = company_data.contact_first_utm_term
        if not self.contact_first_utm_content:
            self.contact_first_utm_content = company_data.contact_first_utm_content
        if not self.contact_utm_placement:
            self.contact_utm_placement = company_data.contact_utm_placement
        if not self.contact_utm_term:
            self.contact_utm_term = company_data.contact_utm_term
        if not self.contact_utm_content:
            self.contact_utm_content = company_data.contact_utm_content
        if not self.contact_utm_lp_url:
            self.contact_utm_lp_url = company_data.contact_utm_lp_url
        if not self.contact_utm_organic_source_url:
            self.contact_utm_organic_source_url = company_data.contact_utm_organic_source_url
        if not self.contact_first_referral_url:
            self.contact_first_referral_url = company_data.contact_first_referral_url
        if not self.contact_last_webpage_visited:
            self.contact_last_webpage_visited = company_data.contact_last_webpage_visited
        if not self.contact_last_referral_url:
            self.contact_last_referral_url = company_data.contact_last_referral_url
        if not self.contact_interaction_source:
            self.contact_interaction_source = company_data.contact_interaction_source
        if not self.contact_ga_client_id:
            self.contact_ga_client_id = company_data.contact_ga_client_id
        if not self.contact_hc_medium_id:
            self.contact_hc_medium_id = company_data.contact_hc_medium_id
        if not self.contact_hc_campaign_id:
            self.contact_hc_campaign_id = company_data.contact_hc_campaign_id
        if not self.contact_hc_source_id:
            self.contact_hc_source_id = company_data.contact_hc_source_id    
        if not self.contact_medium_id:
            self.contact_medium_id = company_data.contact_medium_id
        if not self.contact_campaign_id:
            self.contact_campaign_id = company_data.contact_campaign_id
        if not self.contact_source_id:
            self.contact_source_id = company_data.contact_source_id
        if not self.contact_adposition:
            self.contact_adposition = company_data.contact_adposition
        
 def action_open_linkedin(self):
    self.ensure_one()
    if self.contact_linkedin_url:
        return {
            'type': 'ir.actions.act_url',
            'url': self.contact_linkedin_url,
            'target': 'new',
        }