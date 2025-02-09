{
    'name': 'Contract Automation',
    'version': '1.0',
    'category': 'HR',
    'sequence': 1,
    'website': 'www.technians.com',
    'summary': 'Employee Contract Automation',
    'description': 'Automating Contracts for Employee',
    'author': 'technians',
    'depends': ['hr_recruitment','hr_contract','hr_contract_types','hr_payroll_account_community',],

    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_applicant.xml',
        'views/res_config_settings.xml',

    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
