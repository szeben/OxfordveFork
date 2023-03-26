# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AMRExtension(models.TransientModel):
    
    _inherit = 'account.move.reversal'
        
    dev_mercancia = fields.Boolean(string="Devolución de Mercancía", 
                                   default=True)
    origen_invoice = fields.Char(related="move_ids.invoice_origin")
    
    stock_pick = fields.Many2one(comodel_name="stock.picking", string="Albarán Asociado")
    

    @api.onchange('dev_mercancia')
    def empty_sp(self):
        if not self.dev_mercancia:
            self.stock_pick = ''
    
    def _prepare_default_reversal(self, move):
        res = super(AMRExtension, self)._prepare_default_reversal(move)
        res.update([('dev_mercancia', self.dev_mercancia), ('stock_pick', self.stock_pick.id)])
        return res 
    

        

        
        