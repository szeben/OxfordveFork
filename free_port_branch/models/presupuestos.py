# -*- coding: utf-8 -*-

from odoo import models, api, fields

class PresupuestoExtendido(models.Model):
    
    #_inherit = 'res.branch'
    _inherit = 'sale.order'
    _description = 'Extensión al Presupuesto'
    
    @api.onchange('order_line')
    def _conchange_impuesto(self):
        if self.company_id.puerto_libre:
            for record in self.order_line:
                record.tax_id = [(5, 0, 0)]



