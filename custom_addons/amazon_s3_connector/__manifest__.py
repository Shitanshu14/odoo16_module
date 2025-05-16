{
    'name': "Odoo Amazon S3 Connector",
    'version': "16.0.1.0.0'",
    'category': "Document Management",
    'summary': """ Connect with Amazon S3 Files from Odoo""",
    'description': """This module was developed to upload to Amazon S3 Cloud 
                      Storage as well as access files from Amazon S3 Cloud 
                      Storage in Odoo.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'images': ['static/description/banner.png'],
    'depends': ['base_setup'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/attchment_delete.xml'
    ],

    'license': 'AGPL-3',
    'external_dependencies': {'python': ['boto3']},
    'application': True,
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook'
}
