# -*- coding: utf-8 -*-

from functools import reduce

from odoo import _, api, fields, models


def compute_existence(previous, record):
    if (record.product_id.qty_available - record.qty_done) == 0:
        return record.qty_done
    elif record.location_id.usage == 'inventory' and record.location_id.scrap_location == False:
        return record.qty_done + previous
    elif not record.picking_code and record.location_dest_id.scrap_location == False and record.location_dest_id.usage == 'inventory':
        return previous - record.qty_done
    elif record.picking_code == "internal":
        return previous
    elif record.picking_code == "outgoing":
        return previous - record.qty_done
    else:
        return record.qty_done + previous


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    number = fields.Char(
        string='Numero',
        related='picking_id.origin'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente o Proveedor',
        related='picking_id.partner_id'
    )
    entrada = fields.Float(
        string='Entrada',
        compute='_compute_in_out'
    )
    salida = fields.Float(
        string='Salida',
        compute='_compute_in_out'
    )
    saldo_existencia = fields.Float(
        string='Saldo en existencia',
        compute='_compute_in_out'
    )

    @api.depends('qty_done', 'reference')
    def _compute_in_out(self):
        anterior = 0.0

        if self:
            anterior = reduce(
                compute_existence,
                self.search([
                    ('id', 'not in', self.ids),
                    ('date', '<=', self[0].date),
                ], order='date'),
                anterior
            )

        for record in self:
            entrada = 0.0
            salida = 0.0

            if (
                record.location_id.usage == 'inventory' and
                record.location_id.scrap_location == False
            ) or record.picking_code in {'incoming', 'internal', 'mrp_operation'}:
                entrada = record.qty_done

            if (
                not record.picking_code and record.location_dest_id.usage == 'inventory' and
                record.location_dest_id.scrap_location == False
            ) or record.picking_code in {'outgoing', 'internal'}:
                salida = record.qty_done

            record.salida = salida
            record.entrada = entrada
            record.saldo_existencia = anterior = compute_existence(
                anterior, record)
