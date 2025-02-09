# -*- coding: utf-8 -*-
# License: Odoo Proprietary License v1.0

{
    'name': 'Odoo 16 Financial Reports - PDF, Excel',
    'version': '1.0.0',
    'category': 'Invoicing Management',
    'summary': 'All in One Accounting Reports For Odoo & '
               'Export the Report in PDF or Excel',
    'sequence': '10',
    'author': 'Odoo Mates',
    'license': 'OPL-1',
    'live_test_url': 'https://www.youtube.com/watch?v=83p4NMMIBg0',
    'price': 10,
    'currency': 'USD',
    'maintainer': 'Odoo Mates',
    'support': 'odoomates@gmail.com',
    'website': '',
    'depends': [
        'accounting_pdf_reports',
        'accounting_excel_reports',
        'om_account_book_excel'
    ],
    'data': [
        # 'views/menu.xml',
        'views/daily_reports.xml',
        'views/settings.xml',
        'views/account_common_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.png']
}
