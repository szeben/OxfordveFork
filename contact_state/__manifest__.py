# -*- coding: utf-8 -*-
{
    'name': "Gestión de estados para contactos.",

    'summary': """
        Incorpora los estados “Nuevo” y “Validado” a la creación de un contacto.""",

    'description': """
        1) Incorpora los estados de “Nuevo” y “Validado” a la creación de un contacto.
           Los contactos con estado "Nuevo" son almacenados como contactos archivados. 
           Solamente los contactos validados, pueden ser visibles en los demás módulos del sistema.  
        2) Agrega un filtro para usuarios con estado igual a "Nuevo".
        3) Crea un grupo de usuarios para validar contactos llamado "Cambio de estado en contactos".
    """,

    'author': "Techne Studio IT & Consulting",
    
    'website': "https://technestudioit.com/",
  
    'category': 'Customizations/Contactos.',

    'version': '1.0',

    'license': "Other proprietary",

    'depends': ['base', 'contacts'],

    "installable": True,
    
    "data": [
            'views/contact_state.xml',
            'security/group_contact_state.xml',
            ],
}
