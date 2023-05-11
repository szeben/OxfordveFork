# -*- coding: utf-8 -*-
{
    'name': 'Validación de pago',

    'summary': """
            Incluye un campo de validación en el formulario de pago, para identificar que el mismo ha sido validado.
        """,

    'description': """
        Incluye un campo de validación en el formulario de pago, para identificar que el mismo ha sido validado.
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [        
        'views/payment_validated_views.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
}
