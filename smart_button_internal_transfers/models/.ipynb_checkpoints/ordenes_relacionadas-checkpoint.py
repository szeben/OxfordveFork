# -*- coding: utf-8 -*-

from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
from collections import defaultdict

class OrdenesRelacionadas(models.Model):
    
    _inherit = 'stock.move.line'
    _description = 'Extensión a las líneas de Ventas'
    
    nbr_internal_moves = fields.Integer(compute='_compute_internal_moves', compute_sudo=False)
    
    def _compute_internal_moves(self):
        res = defaultdict(lambda: {'mov_interno': 0})
        mov_interno = 0
        internal_moves = self.env['stock.move.line'].read_group([
                ('product_id.product_tmpl_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'internal'),
                ('date','>=', (fields.Date.context_today(self) - relativedelta(years=1)).strftime('%Y-%m-%d'))
            ], ['product_id'], ['product_id'])
    
        for move in internal_moves:
            product = self.env['product.product'].browse([move['product_id'][0]])
            product_tmpl_id = product.product_tmpl_id.id
            res[product_tmpl_id]['mov_interno'] += int(move['product_id_count'])

        for template in self:
            template.nbr_moves_in = int(res[template.id]['mov_interno'])
    

