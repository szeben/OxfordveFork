# -*- coding: utf-8 -*-

from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
from collections import defaultdict

class ProductoRelacionado(models.Model):
    _inherit = "product.product"

    nbr_moves_internal = fields.Integer(compute='_compute_int_moves', compute_sudo=False, help="Número de movimientos internos en los últimos 12 meses")

    def _compute_int_moves(self):
        res = defaultdict(dict)
        internal_moves = self.env['stock.move.line'].read_group([
                ('product_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'internal'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['product_id'])
       
        for move in internal_moves:
            res[move['product_id'][0]]['mov_interno'] = int(move['product_id_count'])

        for product in self:
            product_res = res.get(product.id) or {}
            product.nbr_moves_internal = product_res.get('mov_interno', 0)  
            
    def action_view_transf_internas(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['context'] = """{'search_default_filter_last_12_months': 1, 
                                'search_default_done': 1, 
                                'search_default_groupby_product_id': 1, 
                                'search_default_internal': '1',
                                'create': 0}"""
        action['domain'] = [('date','>=', (fields.Date.context_today(self) - relativedelta(years=1)).strftime('%Y-%m-%d')),
                            ('product_id', '=', self.id), 
                            ('state', '=', 'done'),
                            ('picking_id.picking_type_id.code', '=', 'internal')]
        return action            
            
            
            
class ProductoTemplateRelacionado(models.Model):
    
    _inherit = 'product.template'
    
    nbr_moves_internal = fields.Integer(compute='_compute_int_moves', compute_sudo=False, help="Número de movimientos internos en los últimos 12 meses")
    
    def _compute_int_moves(self):
        res = defaultdict(lambda: {'mov_interno': 0})
        
        internal_moves = self.env['stock.move.line'].read_group([
                ('product_id.product_tmpl_id', 'in', self.ids),
                ('state', '=', 'done'),
                ('picking_code', '=', 'internal'),
                ('date', '>=', fields.Datetime.now() - relativedelta(years=1))
            ], ['product_id'], ['product_id'])

        for move in internal_moves:
            product = self.env['product.product'].browse([move['product_id'][0]])
            product_tmpl_id = product.product_tmpl_id.id
            res[product_tmpl_id]['mov_interno'] += int(move['product_id_count'])

        for template in self:
            template.nbr_moves_internal = int(res[template.id]['mov_interno'])
       

    def action_view_transf_internas(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['context'] = """{'search_default_filter_last_12_months': 1, 
                                'search_default_done': 1, 
                                'search_default_groupby_product_id': 1, 
                                'search_default_internal': '1',
                                'create': 0}"""
        action['domain'] = [('date','>=', (fields.Date.context_today(self) - relativedelta(years=1)).strftime('%Y-%m-%d')),
                            ('product_id.product_tmpl_id', 'in', self.ids), 
                            ('state', '=', 'done'),
                            ('picking_id.picking_type_id.code', '=', 'internal')]
        return action