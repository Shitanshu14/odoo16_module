{
    'name': ' Email Validator',
    'version': '1.0',
    'category': 'CRM',
    "author": "Shitanshu Pandey",
    'summary': 'Validate email domain via DNS MX record',
    'depends': ['crm', 'contacts'],
    'data': [
        'views/crm_lead_email_validation.xml',
        'views/res_config_setting.xml',
        'views/res_partner_email_validator.xml',
        'views/hr_applicant_email_validation.xml',
        'data/cron_email_validation.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # 'email_validators/static/src/js/email_validation_widget.js',
            'email_validators/static/src/js/hr_applicant_email_validation_widget.js',
            'email_validators/static/src/xml/hr_applicant_email_validation_widget.xml',
        ],
    },
    'installable': True,
    'application': False,
}
