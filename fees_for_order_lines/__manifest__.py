# -*- coding: utf-8 -*-
{
    'name': "fees_for_order_lines",

    'summary': """
        Permite manejar distintas tarifas dentro de un mismo presupuesto de venta.""",

    'description': """
        Incluye una columna de tarifa por línea de pedido, seleccionable por el
    usuario. Restringe la posibilidad de usar tarifas distintas a la predefinida, por usuarios no
    autorizados.
    """,

    'author': "Techne Studio IT &amp; Consulting",
    'website': "https://technestudioit.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Ventas',
    'version': '0.1',
    'license': "Other proprietary",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/fees_for_order_lines_security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "auto_install": False,
    "installable": True,

}
