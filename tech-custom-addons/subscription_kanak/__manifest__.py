# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    'name': 'Product Subscription Management',
    'version': '16.0.1.1',
    'category': 'Sales/Sales',
    'license': 'OPL-1',
    'summary': 'This module is allow to create and order Subscription manually in odoo | product subscription | subscription intervals | product subs | Subscription | Product Subscription | product subscription management | subscription lines',
    'description': """
This module will allows to auto create product subscription.

1.1 [IMP] discount functionality implement in subscription module.
1.2 [IMP] discount functionality apply from 1st order or 2nd order.
1.3 [FIX] Qty plus minus discount will remove issue fix. next when again subscription product add to cart discount not apply issue fix.
1.4 [FIX] backend new subscription create at the time product onchange auto update discount and set discount to subscription line.
1.5 [FIX] onchange product update discount on sale order line. show only s2s payment gateway if any subscription products in sale order.
1.6 [FIX] subscription intervals filter based on product selection on sale order line.
1.7 [FIX] Fix the singleton error on deletion of subscription line if any is in state 'in_progress' & 'hold'.
    """,
    'author': "Kanak Infosystems LLP.",
    'website': 'https://www.kanakinfosystems.com',
    'depends': [
        'account',
        'sale_management',
        'sale',
        'stock',
        'portal',
        'base_automation',
        'project'
    ],
    "external_dependencies": {"python": ["dateutil"]},
    'images': ['static/description/banner.gif'],
    'data': [
        'security/ir.model.access.csv',
        'data/subscription_cron_data.xml',
        'data/subscription_data.xml',
        'data/mail_templates_data.xml',
        'data/report_paperformates.xml',
        'report/subscription_product.xml',
        'report/subscription_product_report_template.xml',
        'views/account_move_views.xml',
        'views/subscription.xml',
        'views/subscription_lines.xml',
        'views/subscription_intervals_views.xml',
        'views/product_views.xml',
        'views/sale_order.xml',
        'views/res_partner_view.xml',
        'views/res_config_settings.xml',
        # Added by Technians
        'views/product_product.xml',
        'views/project_project.xml',
        # 'views/product_template.xml'
        
    ],
    'sequence': 1,
    'installable': True,
    'application': True,
    'post_init_hook': '_post_init_hook',
    'price': 125,
    'currency': 'EUR',
}
