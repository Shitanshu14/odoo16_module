from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ApplicantmailWizard(models.TransientModel):
    _name = 'applicant.job.wizard'
    _description = 'Applicant Job Wizard'

    crm_id = fields.Many2one('crm.lead', string='Job lead')
    name = fields.Char(string='Name')
    subject = fields.Char(string='Subject')
    email_from = fields.Char(string='Email')
    phone = fields.Char(string='Phone')



    def create_applicant(self):
        self.ensure_one()
        applicant_vals = {
            'name': self.subject,
            'partner_name': self.name,
            'email_from': self.email_from,
            'partner_phone': self.phone,
            'medium_id': self.crm_id.medium_id.id if self.crm_id and self.crm_id.medium_id else '',
            'campaign_id': self.crm_id.campaign_id.id if self.crm_id and self.crm_id.campaign_id else '',
            'source_id': self.crm_id.source_id.id if self.crm_id and self.crm_id.source_id else '',
            'applicant_utm_device': self.crm_id.lead_utm_device if self.crm_id.lead_utm_device else '',
            'applicant_ads_group': self.crm_id.lead_ads_group if self.crm_id.lead_ads_group else '',
            'applicant_utm_device_model':self.crm_id.lead_utm_device_model if self.crm_id.lead_utm_device_model else'',
            'applicant_google_gclid':self.crm_id.lead_google_gclid if self.crm_id.lead_google_gclid else'',
            'applicant_first_utm_campaign':self.crm_id.lead_first_utm_campaign if self.crm_id.lead_first_utm_campaign else'',
            'applicant_first_utm_medium':self.crm_id.lead_first_utm_medium if self.crm_id.lead_first_utm_medium else '',
            'applicant_first_utm_source':self.crm_id.lead_first_utm_source if self.crm_id.lead_first_utm_source else'',
            'applicant_first_utm_term':self.crm_id.lead_first_utm_term if self.crm_id.lead_first_utm_term else'',
            'applicant_first_utm_content':self.crm_id.lead_first_utm_content if self.crm_id.lead_first_utm_content else '',
            'applicant_utm_term':self.crm_id.lead_utm_term if self.crm_id.lead_utm_term else '',
            'applicant_utm_placement':self.crm_id.lead_utm_placement if self.crm_id.lead_utm_placement else'',
            'applicant_utm_content':self.crm_id.lead_utm_content if self.crm_id.lead_utm_content else '',
            'applicant_utm_lp_url':self.crm_id.lead_utm_lp_url if self.crm_id.lead_utm_lp_url else'',
            'applicant_utm_organic_source_url':self.crm_id.lead_utm_organic_source_url if self.crm_id.lead_utm_organic_source_url else'',
            'applicant_first_referral_url':self.crm_id.lead_first_referral_url if self.crm_id.lead_first_referral_url else'',
            'applicant_last_webpage_visited':self.crm_id.lead_last_webpage_visited if self.crm_id.lead_last_webpage_visited else '',
            'applicant_last_referral_url':self.crm_id.lead_last_referral_url if self.crm_id.lead_last_referral_url else '',
            'applicant_interaction_source':self.crm_id.lead_interaction_source if self.crm_id.lead_interaction_source else '',
            'applicant_ga_client_id':self.crm_id.lead_ga_client_id if self.crm_id.lead_ga_client_id else'',
            'applicant_adposition':self.crm_id.lead_adposition if self.crm_id.lead_adposition else '',
            'applicant_handl_url':self.crm_id.lead_handl_url if self.crm_id.lead_handl_url else '',
            'applicant_handl_ref_domain':self.crm_id.lead_handl_ref_domain if self.crm_id.lead_handl_ref_domain else'',
            'applicant_handl_url_base':self.crm_id.lead_handl_url_base if self.crm_id.lead_handl_url_base else'',
            'applicant_organic_source_str':self.crm_id.lead_organic_source_str if self.crm_id.lead_organic_source_str else'',
            'applicant_traffic_source':self.crm_id.lead_traffic_source if self.crm_id.lead_traffic_source else'',
            'applicant_utm_matchtype':self.crm_id.lead_utm_matchtype if self.crm_id.lead_utm_matchtype else '',
            'applicant_interaction_source':self.crm_id.lead_interaction_source if self.crm_id.lead_interaction_source else '',
            'applicant_first_traffic_source':self.crm_id.lead_first_traffic_source if self.crm_id.lead_first_traffic_source else'',

        }
        self.env['hr.applicant'].create(applicant_vals)
