# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'   

    
    @api.model
    def create(self, vals_list):
        """
            Agrega validación al Crear una orden de venta (modelo sale.order). 
            Se valida por cada línea de pedido (modelo sale.order.line), 
            que la cantidad pedida (campo product_uom_qty), 
            sea menor o igual a la cantidad disponible (campo free_qty_today)
        """ 
        res = super(SaleOrder, self).create(vals_list)      
        order_line_rec = res.order_line    
        for line in order_line_rec:           
            if  line.product_uom_qty > line.free_qty_today:   
                raise UserError(_('Existe una línea de pedido con una solicitud de mercancía superior a la disponible.'))
        return res
    
    @api.model
    def write(self, vals):
        """
            Agrega validación al Editar una orden de venta (modelo sale.order). 
            Se valida por cada línea de pedido (modelo sale.order.line), 
            que la cantidad pedida (campo product_uom_qty), 
            sea menor o igual a la cantidad disponible (campo free_qty_today)
        """     
        order_line_rec = self.order_line    
        for line in order_line_rec:           
            if  line.product_uom_qty > line.free_qty_today:   
                raise UserError(_('Existe una línea de pedido con una solicitud de mercancía superior a la disponible.'))
        return super(SaleOrder, self).write(vals)