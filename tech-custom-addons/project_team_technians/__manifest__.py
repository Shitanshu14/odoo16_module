{
    'name': 'Project Team',
    'version': '1.0',
    'summary': 'Adds Project Team field in Project',
    'description': 'Adds Project Team field in Project',
    'author': 'Technians',
    'website': 'https://www.technians.com',
    'depends': ['base','project'],  # List of dependencies if any
    'data': [
        'security/ir.model.access.csv',
        'views/project_team.xml',
        'views/ir_cron.xml',
        'views/res_config_settings.xml',
        # Add XML or CSV files related to the module
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
