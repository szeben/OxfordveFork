# -*- coding: utf-8 -*-
{
    'name': """
        Restricción para confirmar factura rectificativa de cliente
        (Restriction to confirm customer credit note)
    """,

    'summary': """
        Restringe la posibilidad de confirmar notas de créditos de clientes, permitiéndolo solo
        a usuarios autorizados. (Restricts the ability to confirm customer credit notes, allowing only
        authorized users)
    """,

    'description': """
        Restringe la posibilidad de confirmar notas de créditos de clientes, permitiéndolo
        solo a usuarios autorizados. (Restricts the ability to confirm customer credit notes, allowing only
        authorized users)
    """,

    'author': "Techne Studio IT & Consulting",
    'website': "https://technestudioit.com/",

    'license': "Other proprietary",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}
