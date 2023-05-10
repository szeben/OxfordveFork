# -*- coding: utf-8 -*-
{
    'name': 'Formatos para compras',

    'summary': """
            Modifica el formato para las solicitudes de presupuestos de las órdenes de compra.
        """,

    'description': """
        Modifica el formato para las solicitudes de presupuestos de las órdenes de compra.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'contact_type_restrictions'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/stock_move_line_tree.xml',
        'report/report_purchasequotation_with_approvals_template.xml',
        'report/report_purchasequotation_with_approvals_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
}
