# -*- coding: utf-8 -*-
{
    'name': "Restringir y gestionar contactos.",

    'summary': """
        Restringe la visualizacion y gestión de los contactos de acuerdo a su clasificación como cliente o proveedor.""",

    'description': """
        Restringe la visualizacion y gestión de los contactos de acuerdo a su clasificación como cliente o proveedor.
        Agrega el campo "Es nacional", para indicar si un proveedor es nacional o no.
        Agrega el filtro para el campo "Es nacional".
        Agrega 4 grupos de usuario nuevos, los cuales se listan a continuación:
        - Grupo para restringir la gestión de proveedores (No puede crear, eliminar y editar).
        - Grupo para para restringir la visualización de proveedores.
        - Grupo para para restringir la visualización de proveedores nacionales.
        - Grupo para para restringir la visualización de clientes.
    """,

    'author': "Techne Studio IT & Consulting",
    
    'website': "https://technestudioit.com/",
  
    'category': 'Customizations/Contactos.',

    'version': '1.0',

    'license': "Other proprietary",

    'depends': ['base', 'contacts', 'sale', 'purchase', 'account'],

    "installable": True,
    
    "data": [
            'views/national_field.xml',
            'security/restrict_supplier_customer.xml',
            'security/ir.model.access.csv',
            ],
}
