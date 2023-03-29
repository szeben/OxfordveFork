# -*- coding: utf-8 -*-
{
    'name': "Validación cantidades pedidas en presupuestos.",

    'summary': """
        Verifica que las cantidades pedidas en una orden de venta no sean mayores a las cantidades disponibles.""",

    'description': """
        Verifica que las cantidades pedidas de mercancía por línea de pedido 
        no sean mayores que las cantidades disponibles en almacén, en caso contrario 
        no permite continuar con la transacción.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '15.0.0.1',
    'license': "Other proprietary",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "auto_install": False,
    "installable": True,

}
