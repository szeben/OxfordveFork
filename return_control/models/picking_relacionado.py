# -*- coding: utf-8 -*-

from odoo import models, api, fields

class StockPickingRelacionado(models.Model):
    
    _inherit = 'stock.picking'
    nota_cred = fields.Char(string="Nota de Crédito", readonly=True)
    uso_locacion = fields.Selection(related="location_id.usage")
    es_devolucion = fields.Boolean(string="¿Es una devolución?", compute='compute_devolucion', store=True)
    
    @api.depends('picking_type_code', 'uso_locacion')
    def compute_devolucion(self):
        for pick in self:
            conditions = pick.picking_type_code == 'incoming' and pick.uso_locacion == 'customer'
            pick.es_devolucion = conditions

           
  
               

    
    

  
    