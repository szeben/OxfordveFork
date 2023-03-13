# -*- coding: utf-8 -*-
{
    'name': "constraints_on_budgets_and_POs",

    'summary': """
        Restringe la visualización y gestión de presupuestos y OC en el módulo de Compras.""",

    'description': """
        Restringe la visualización y gestión de presupuestos y órdenes de compra en
        el módulo de Compras.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Compras',
    'version': '0.1',
    'license': "Other proprietary",

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account'],

    # always loaded
    'data': [
        'security/constraints_on_budgets_and_pos_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "auto_install": False,
    "installable": True,

    "uninstall_hook": 'constraints_on_budget_and_pos_uninstall_hook',
}
