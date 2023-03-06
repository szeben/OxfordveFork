# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPickingReportField(models.Model):
    _inherit = 'stock.picking'

    total_product_uom_qty = fields.Float(
        string='Demandado',
        compute='_compute_total_product_uom_qty',
        store=True
    )
    total_quantity_done = fields.Float(
        string='Realizado',
        compute='_compute_total_quantity_done',
        store=True
    )

    @api.depends('move_ids_without_package', 'move_ids_without_package.product_uom_qty')
    def _compute_total_product_uom_qty(self):
        for record in self:
            record.total_product_uom_qty = sum(
                record.move_ids_without_package.mapped("product_uom_qty")
            )

    @api.depends('move_ids_without_package', 'move_ids_without_package.quantity_done')
    def _compute_total_quantity_done(self):
        for record in self:
            record.total_quantity_done = sum(
                record.move_ids_without_package.mapped("quantity_done")
            )
