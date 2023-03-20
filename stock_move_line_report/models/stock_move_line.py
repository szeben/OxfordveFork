# -*- coding: utf-8 -*-

from functools import reduce

from odoo import _, api, fields, models
from odoo.osv.expression import (AND, AND_OPERATOR, OR_OPERATOR, is_leaf,
                                 is_operator, normalize_domain, normalize_leaf)


def delete_date_leaf(domain):
    new_domain = []

    for i, elm in enumerate(domain):
        if is_leaf(elm) and i > 0:
            field, operator, _ = normalize_leaf(elm)
            if field == 'date' and operator in {'>', '>='}:
                for j, olm in enumerate(new_domain[::-1]):
                    if is_operator(olm):
                        new_domain.pop(-j-1)
                        if olm in {AND_OPERATOR, OR_OPERATOR}:
                            break
                continue
        new_domain.append(elm)

    return normalize_domain(new_domain)


def compute_existence(previous, record) -> float:
    if (record.product_id.qty_available - record.qty_done) == 0:
        return record.qty_done
    elif record.location_id.usage == 'inventory' and record.location_id.scrap_location == False:
        return record.qty_done + previous
    elif not record.picking_code and record.location_dest_id.scrap_location == False and record.location_dest_id.usage == 'inventory':
        return previous - record.qty_done
    elif record.picking_code == "outgoing":
        return previous - record.qty_done
    elif record.picking_code == "internal":
        if record.location_id.branch_id == record.location_dest_id.branch_id:
            return previous
        elif record.branch_id != record.location_dest_id.branch_id:
            return previous - record.qty_done
        else:
            return record.qty_done + previous
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

    extra_context = {}

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        self.extra_context.update({"domain": args, "order": order})
        return super().search(args, offset=offset, limit=limit, order=order, count=count)

    def _get_previous_value(self):
        order = self.extra_context.get('order', 'date ASC')
        order_field = order.split(",", maxsplit=1)[0].strip().lower()

        if order_field in {"date", "date asc"}:
            min_record = min(self, key=lambda r: r.write_date)
            domain = [
                '&', '&',
                ('id', 'not in', self.ids),
                ('date', '<=', min_record.date),
                ('write_date', '<', min_record.write_date)
            ]
            extra_domain = self.extra_context.get('domain', [])
            if extra_domain:
                domain = AND([domain, delete_date_leaf(extra_domain)])

            return reduce(
                compute_existence,
                super().sudo().search(domain, order=order),
                0.0
            )

    @api.depends('qty_done', 'reference')
    def _compute_in_out(self):
        previous = self._get_previous_value()
        anterior = 0.0 if previous is None else previous

        for record in self:
            entrada = 0.0
            salida = 0.0

            if record.picking_code == 'internal':
                if record.location_id.branch_id == record.location_dest_id.branch_id:
                    entrada = salida = record.qty_done
                elif record.branch_id != record.location_dest_id.branch_id:
                    salida = record.qty_done
                else:
                    entrada = record.qty_done

            else:
                if record.picking_code in {'incoming', 'mrp_operation'} or (
                    record.location_id.usage == 'inventory'
                    and record.location_id.scrap_location == False
                ):
                    entrada = record.qty_done

                if record.picking_code == 'outgoing' or (
                    not record.picking_code
                    and record.location_dest_id.usage == 'inventory'
                    and record.location_dest_id.scrap_location == False
                ):
                    salida = record.qty_done

            record.salida = salida
            record.entrada = entrada

            if previous is None:
                record.saldo_existencia = False
            else:
                record.saldo_existencia = anterior = compute_existence(anterior, record)
