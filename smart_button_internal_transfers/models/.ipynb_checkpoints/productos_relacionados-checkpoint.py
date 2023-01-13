# -*- coding: utf-8 -*-

from odoo import models, api, fields

class ProductosRelacionados(models.Model):
    
    _inherit = 'product.template'
    _description = 'Extensión a los esqueletos de Producto'
    
    sale_line = fields.Many2many(comodel_name="stock.move.line", string="Stock ID")
    internal_moves = fields.Integer(related="sale_line.nbr_internal_moves")
    
    def action_view_transf_internas(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_line_action")
        action['context'] = """{'search_default_filter_last_12_months': 1, 
                                'search_default_done': 1, 
                                'search_default_groupby_product_id': 1, 
                                'search_default_internal': '1',
                                'create': 0}"""
        action['domain'] = [('product_id', '=', self.id), 
                            ('picking_id.picking_type_id.code', '=', 'internal'),
                            ('product_id.product_tmpl_id', 'in', self.ids)]
        return action