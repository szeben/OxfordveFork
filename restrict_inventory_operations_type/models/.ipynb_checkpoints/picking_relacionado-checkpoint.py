# -*- coding: utf-8 -*-

from odoo import models, api, fields

class StockPickingRelacionado(models.Model):
    
    _inherit = 'stock.picking'
    
    
    mostrar_validacion = fields.Boolean(default=False, compute='_compute_mostrar_valid')
    

    @api.depends('picking_type_id.code')
    def _compute_mostrar_valid(self):
        
        has_my_group = self.env.user.has_group('restrict_inventory_operations_type.group_validar_transferencias_internas')
        
        if self.show_validate and self.picking_type_id.code != 'internal':
            self.mostrar_validacion = True
        else:
            self.mostrar_validacion = False
        
 
        
        """
        for picking in self:
            if picking.picking_type_id.code == 'internal' or picking.picking_type_id.code == 'Internal Transfer':
                picking.mostrar_validacion = True
            else:
                picking.mostrar_validacion = False
                """
                
                
           
  
               

    
    

  
    