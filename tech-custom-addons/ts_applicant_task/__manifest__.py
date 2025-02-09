{
    'name': 'Send Tasks to Applicant',
    'version': '1.0',
    'category': 'HR/Recruitment',
    'sequence': 1,
    'website': 'https://www.linkedin.com/in/rahul-yadav-659b972a8/',
    'summary': 'Applicant Tasks',
    'description': 'Tasks for Applicant',
    'author': 'Rahul',
    'depends': ['base','project','hr_recruitment',],

    'data': [
        'security/ir.model.access.csv',
        'views/applicant.xml',
        'views/hr_applicant_task.xml',
        # 'views/res_config_settings.xml',

    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
