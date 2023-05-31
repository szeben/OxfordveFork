
# -*- coding: utf-8 -*-

from calendar import monthrange
from datetime import date

from odoo import _, api, exceptions, fields, models


def get_first_and_last_day_of_month(date: date):
    return date.replace(day=1), date.replace(day=monthrange(date.year, date.month)[1])


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    branch_id = fields.Many2one(
        related='order_id.branch_id',
        string="Sucursal",
        store=True,
        domain=[('order_id', '!=', False)]
    )
    categ_id = fields.Many2one(
        related='product_id.categ_id',
        string="Categoría del producto",
        readonly=True,
        store=True
    )
    team_id = fields.Many2one(
        related='order_id.partner_id.team_id',
        string="Equipo de ventas",
        store=True,
        domain=[('order_id', '!=', False)]
    )
    quantity = fields.Float(
        string="Cantidad facturada",
        store=True
    )
    amount_sale = fields.Monetary(
        string="Monto de la venta",
        related='order_id.amount_total',
        store=True
    )
    date = fields.Datetime(
        related='order_id.date_order',
        string="Fecha",
        store=True
    )
    total_vendidos = fields.Float(
        compute="_compute_total_vendidos",
        string="Total vendidos",
        store=True
    )
    total_amount_commissions = fields.Monetary(
        compute="_compute_commissions",
        string="Total de comisión",
        store=True
    )

    @api.depends(
        "product_id",
        "date",
        "invoice_lines",
        "qty_invoiced",
        "amount_sale",
        "order_id",
        "order_id.invoice_ids",
        "order_id.state",
        "order_id.date_order",
        "order_id.branch_id",
        "order_id.invoice_ids",
        "order_id.invoice_ids.state",
        "order_id.invoice_ids.move_type",
        "order_id.invoice_ids.invoice_line_ids",
        "order_id.invoice_ids.invoice_line_ids.quantity_product_uom",
        "order_id.invoice_ids.invoice_line_ids.product_id",
        "order_id.invoice_ids.invoice_line_ids.quantity",
    )
    def _compute_total_vendidos(self):
        for line in self:
            if not (
                line.invoice_lines
                and line.qty_invoiced > 0
                and line.order_id
                and line.order_id.invoice_ids
                and line.order_id.state == 'done'
            ):
                continue

            total_vendidos = 0

            for invoice in line.order_id.invoice_ids:
                if not (invoice.state == 'posted' and invoice.move_type == 'out_invoice'):
                    continue

                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.product_id.id != line.product_id.id:
                        continue

                    total_vendidos += invoice_line.quantity_product_uom

            line.total_vendidos = total_vendidos

    @api.depends(
        "total_vendidos",
        "date",
        "team_id",
        "invoice_lines",
        "product_id",
        "product_id.commission_ids",
        "product_id.commission_ids.commission_type",
        "product_id.commission_ids.cant_minima_base",
        "product_id.commission_ids.cant_min_base_otra_com",
        "product_id.commission_ids",
        "product_id.commission_group_id.commission_ids.commission_type",
        "product_id.commission_group_id.commission_ids.cant_minima_base",
        "product_id.commission_group_id.commission_ids.cant_min_base_otra_com",
    )
    def _compute_commissions(self):
        for line in self:
            line.total_amount_commissions = 0

            if not (
                line.invoice_lines
                and line.product_id.commission_ids
                and line.total_vendidos != 0
                and line.date
                and line.team_id
            ):
                continue

            first_day, last_day = get_first_and_last_day_of_month(line.date)
            totals = self.read_group(
                domain=[
                    ('date', '>=', first_day),
                    ('date', '<=', last_day),
                    ('product_id', '=', line.product_id.id),
                    ('team_id', '=', line.team_id.id),
                    ('total_vendidos', '>', 0),
                    ('product_id.commission_ids', '!=', False)
                ],
                fields=["total_vendidos:sum"],
                groupby=[],
            )[0]

            count = totals.get("__count", 0.0)

            if count == 0:
                continue

            line.total_amount_commissions = line.product_id.compute_commission(
                totals.get("total_vendidos", 0.0),
            ) / count
