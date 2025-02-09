# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Preview Attachments',
    'version': '16.0.1.0.0',
    'category': 'Tools',
    'author': 'Win DX JSC',
    'company': 'Win DX JSC',
    'maintainer': 'Win DX JSC',
    'price': 77.99,
    'currency': 'USD',
    'sequence': 110,
    'summary': 'Preview Attachments (Docx, Xlsx, Pptx, PDF, Image, Video)',
    'description': """
        User can preview attachments files: Docx, Xlsx, Pptx, PDF, Image, Video...
    """,
    'website': 'https://windx.com.vn',
    'support': 'windxcontact@gmail.com',
    'depends': ['web', 'mail'],
    'data': [
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'windx_attachments_preview/static/src/attachment/*',
            'windx_attachments_preview/static/src/many2many_binary/*',
            'windx_attachments_preview/static/src/attachment_viewer/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
}
