{
    'name': 'Apps Development',
    'version': '18.0',
    'category': 'Sales',
    'summary': 'Order Section for Apps Development',
    'description': """
    This module adds an Order Section with a form view to manage orders and related details.
    """,
    'author': 'Shitanshu Pandey',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_section_views.xml',
        'views/service_provider.xml',
        # 'views/order_preview.xml',
    ],
    'installable': True,
    'application': True,
}
