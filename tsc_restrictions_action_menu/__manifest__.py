# -*- coding: utf-8 -*-
{
    'name': "Restrictions on Action menu",

    'summary': """
        Restricts the display of the Action menu. Restrict special Action menu options""",

    'description': """
        Restricts the display of the Action menu. Restricts the option to archive/unarchive contacts and duplicate sales and purchase orders
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'license': 'Other proprietary',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'sale_management', 'contacts', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/tsc_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "tsc_restrictions_action_menu/static/src/js/tsc_hide_actions.js",
        ]
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
