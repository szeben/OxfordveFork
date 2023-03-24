# -*- coding: utf-8 -*-
{
    'name': "Informe reposición de inventario",

    'summary': """
        Nueva vista en los informes en el módulo de inventario,
        llamado Reposición de Inventario""",

    'description': """
        Nueva vista en los informes en el módulo de inventario,
        llamado Reposición de Inventario.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock', 'branch', 'product_available_by_branch_kanban'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'stock_replenishment_report/static/src/js/stock_replenishment_view_list.js',
        ],
    },
}
