from odoo import fields, models, api
import datetime
class HRApplicant(models.Model):
    _inherit = 'hr.applicant'
    _description = 'Job Applicant'
    
    campaign_id = fields.Many2one(ondelete='set null',tracking=True)
    medium_id = fields.Many2one(ondelete='set null',tracking=True)
    source_id = fields.Many2one(ondelete='set null',tracking=True)

    applicant_notice_period = fields.Integer(string = "Notice Period (Months)",tracking=True)
    applicant_experience = fields.Integer(string = "Total Experience (Months)",tracking=True)
    applicant_current_city_id = fields.Many2one('res.country.city', string = "Current City",tracking=True)
    applicant_preferred_city_id = fields.Many2one('res.country.city', string = "Preferred City",tracking=True)
    applicant_current_employer_id = fields.Many2one('hr.employer', string = "Current Employer",tracking=True)
    applicant_resume = fields.Char(string = "Resume/CV",tracking=True)
    applicant_dob = fields.Date(string="Date of Birth",tracking=True)
    applicant_current_ctc = fields.Float(string="Current CTC",tracking=True)
    applicant_ads_group = fields.Char(string="Ads Group",tracking=True)
    applicant_utm_device = fields.Char(string="UTM Device",tracking=True)
    applicant_utm_device_model = fields.Char(string="UTM Device Model",tracking=True)
    applicant_google_gclid = fields.Char(string="Google GCLID",tracking=True)
    applicant_first_utm_campaign = fields.Char(string="First UTM Campaign",tracking=True)
    applicant_first_utm_medium = fields.Char(string="First UTM Medium",tracking=True)
    applicant_first_utm_source = fields.Char(string="First UTM Source",tracking=True)
    applicant_first_utm_term = fields.Char(string="First UTM Term",tracking=True)
    applicant_first_utm_content = fields.Char(string="First UTM Content",tracking=True)
    applicant_utm_term = fields.Char(string="UTM Term",tracking=True)
    applicant_utm_placement = fields.Char(string="UTM Placement",tracking=True)
    applicant_utm_content = fields.Char(string="UTM Content",tracking=True)
    applicant_utm_lp_url = fields.Char(string="UTM LP URL",tracking=True)
    applicant_utm_organic_source_url = fields.Char(string="UTM Organic Source URL",tracking=True)
    applicant_first_referral_url = fields.Char(string="First Referral URL",tracking=True)
    applicant_last_webpage_visited = fields.Char(string="Last Webpage Visited",tracking=True)
    applicant_last_referral_url = fields.Char(string="Last Referral URL",tracking=True)
    applicant_interaction_source = fields.Char(string="Interaction Source",tracking=True)
    applicant_ga_client_id = fields.Char(string="GA Client Id",tracking=True)
    applicant_adposition = fields.Char(string="AD Position",tracking=True)

    applicant_handl_url = fields.Char(string='Handl URL',tracking=True)
    applicant_handl_ref_domain = fields.Char(string='Handlref Domain',tracking=True)
    applicant_handl_url_base = fields.Char(string='Handl URL Base',tracking=True)
    applicant_organic_source_str = fields.Char(string='Organic Source Str',tracking=True)
    applicant_traffic_source = fields.Char(string='Traffic Source',tracking=True)
    applicant_utm_matchtype = fields.Char(string='UTM Matchtype',tracking=True)
    # applicant_visitor_geo_state = fields.Char(string='Visitor Geo State')
    applicant_first_traffic_source = fields.Char(string='First Traffic Source',tracking=True)
    
    @api.model
    def create(self, vals):
        if 'source_id' not in vals or not vals['source_id']:
            applicant_organic_source_str = vals.get('applicant_organic_source_str')
            if applicant_organic_source_str:
                custom_source = self.env['utm.source'].search([('name', '=', applicant_organic_source_str)], limit=1)
                if not custom_source:
                    custom_source = self.env['utm.source'].create({'name': applicant_organic_source_str})
                vals['source_id'] = custom_source.id
        result = super(HRApplicant, self).create(vals)
        return result
    
    # def create_employee_from_applicant(self):
    #     """ Create an employee from applicant """
    #     self.ensure_one()
    #     self._check_interviewer_access()

    #     contact_name = False
    #     if self.partner_id:
    #         address_id = self.partner_id.address_get(['contact'])['contact']
    #         contact_name = self.partner_id.display_name
    #     else:
    #         if not self.partner_name:
    #             raise UserError(_('You must define a Contact Name for this applicant.'))
    #         new_partner_id = self.env['res.partner'].create({
    #             'is_company': False,
    #             'type': 'private',
    #             'name': self.partner_name,
    #             'email': self.email_from,
    #             'phone': self.partner_phone,
    #             'mobile': self.partner_mobile
    #         })
    #         self.partner_id = new_partner_id
    #         address_id = new_partner_id.address_get(['contact'])['contact']
    #     employee_data = {
    #         'default_name': self.partner_name or contact_name,
    #         'default_job_id': self.job_id.id,
    #         'default_job_title': self.job_id.name,
    #         'default_address_home_id': address_id,
    #         'default_department_id': self.department_id.id,
    #         'default_address_id': self.company_id.partner_id.id,
    #         'default_work_email': self.department_id.company_id.email or self.email_from, # To have a valid email address by default
    #         'default_work_phone': self.department_id.company_id.phone,
    #         'form_view_initial_mode': 'edit',
    #         'default_applicant_id': self.ids,
    #     }
    #     if 'applicant_dob' in self.env['hr.applicant']._fields:
    #         employee_data['default_birthday']=self.applicant_dob
            
    #     dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
    #     dict_act_window['context'] = employee_data
    #     return dict_act_window

    def create_employee_from_applicant(self):
        """ Create an employee from applicant """
        self.ensure_one()
        self._check_interviewer_access()

        contact_name = False
        if self.partner_id:
            address_id = self.partner_id.address_get(['contact'])['contact']
            contact_name = self.partner_id.display_name
        else:
            if not self.partner_name:
                raise UserError(_('You must define a Contact Name for this applicant.'))
            new_partner_id = self.env['res.partner'].create({
                'is_company': False,
                'type': 'private',
                'name': self.partner_name,
                'email': self.email_from,
                'phone': self.partner_phone,
                'mobile': self.partner_mobile
            })
            self.partner_id = new_partner_id
            address_id = new_partner_id.address_get(['contact'])['contact']
        employee_data = {
            'default_name': self.partner_name or contact_name,
            'default_job_id': self.job_id.id,
            'default_job_title': self.job_id.name,
            'default_address_home_id': address_id,
            'default_department_id': self.department_id.id,
            'default_address_id': self.company_id.partner_id.id,
            # 'default_work_email': self.department_id.company_id.email or self.email_from,
            'default_work_email':  self.email_from,
            # To have a valid email address by default
            'default_work_phone': self.department_id.company_id.phone,
            'form_view_initial_mode': 'edit',
            'default_applicant_id': self.ids,
        }
        if 'applicant_dob' in self.env['hr.applicant']._fields:
            employee_data['default_birthday'] = self.applicant_dob

        employee_data.update({
            'default_mobile_phone': self.partner_phone,  # Update for mobile phone
            'default_work_phone': self.partner_mobile,  # Update for work phone
        })

        if self.applicant_current_city_id:
            employee_data['default_work_location_id'] = self.applicant_current_city_id.id

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window
    
       

    def tech_send_birthday_email(self):
        records = self.search([])
        for record in records:
            dob = record.applicant_dob
            if dob:
                if self.is_birthday_today(dob):
                    mail_template = self.env.ref('technians_apps_customization.tech_applicant_birthday_email_tpl')
                    mail_template.send_mail(record.id, force_send=True)

    @staticmethod
    def is_birthday_today(birthdate):
        today = datetime.date.today()
        return birthdate.month == today.month and birthdate.day == today.day 
        
    
   