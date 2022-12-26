# -*- coding: utf-8 -*-
{
    'name': "Restricciones por tipo de diario.",

    'summary': """
        Restringe la gestión de los diarios de acuerdo a su clasificación 
        como custodio, inversión o punto de venta.""",

    'description': """
       Incluye una clasificación para los diarios, identificándolos como 
       “Custodio”, “Inversión” o "Punto de venta", a fin de que sólo ciertos usuarios puedan 
       gestionar dichos diarios.

       Agrega 3 grupo de usuario:
       1) Grupo para gestionar diarios de tipo Cutodio.
       2) Grupo para gestionar diarios de tipo Inversión.
       3) Grupo para gestionar diarios de tipo Punto de venta.

    """,

    'author': "Techne Studio IT & Consulting",
    
    'website': "https://technestudioit.com/",
  
    'category': 'Accounting/Journal Type.',

    'version': '1.0',

    'license': "Other proprietary",

    'depends': ['base', 'account'],

    "installable": True,
    
    "data": [            
            'security/restrict_journal_type.xml',
            'security/ir.model.access.csv',
            'views/journal_type.xml',       
            ],
}
