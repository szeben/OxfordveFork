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
        - Grupo para gestionar proveedores (crear, eliminar, editar y listar).
        - Grupo para visualizar proveedores.
        - Grupo para visualizar proveedores, exeptuando los proveedores nacionales.
        - Grupo para visualizar clientes.
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
