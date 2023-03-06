# -*- coding: utf-8 -*-
{
    'name': 'Informe de Albarán.',

    'summary': """
            Informe de Albarán.
        """,

    'description': """
        Campo calculado para el informe de Albarán.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
}
