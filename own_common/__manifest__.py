{
    'name': 'Own_X',
    'version': '17.0.1.0.6',
    'summary': 'Summery',
    'description': 'Common Customization',
    'category': 'Category',
    'author': 'Oleksii Panpukha',
    'website': 'Website',
    'depends': ['account', 'crm_enterprise'],
    'data': [
        'views/crm_lead.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'own_common/static/src/js/rounded_monetary_widget.js',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
