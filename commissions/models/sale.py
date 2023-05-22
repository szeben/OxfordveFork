
# -*- coding: utf-8 -*-

from calendar import monthrange
from datetime import date

from odoo import _, api, exceptions, fields, models


def get_first_and_last_day_of_month(date: date):
    return date.replace(day=1), date.replace(day=monthrange(date.year, date.month)[1])


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_id = fields.Many2one('commission.for.sale', string="Comisión")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    commission_id = fields.Many2one(
        'commission.for.sale',
        string="Comisión"
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
        readonly=True,
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
        readonly=True,
        store=True
    )
    total_vendidos = fields.Float(
        compute="_compute_total_vendidos",
        string="Total vendidos",
        store=True
    )
    total_amount_sales = fields.Monetary(
        compute="_compute_total_vendidos",
        string="Monto de las ventas",
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
        # "commission_id",
        # "product_id.commission_ids",
        # "state",
        # "invoice_status",
        "order_id",
        "order_id.invoice_ids",
        "order_id.state",
        "order_id.date_order",
        "order_id.branch_id",
        "order_id.invoice_ids",
        "order_id.invoice_ids.state",
        "order_id.invoice_ids.move_type",
        "order_id.invoice_ids.invoice_line_ids",
        "order_id.invoice_ids.invoice_line_ids.product_id",
        "order_id.invoice_ids.invoice_line_ids.product_id.uom_id",
        "order_id.invoice_ids.invoice_line_ids.branch_id",
        "order_id.invoice_ids.invoice_line_ids.product_uom_id",
        # "order_id.invoice_ids.invoice_line_ids.product_uom_id.uom_type",
        # "order_id.invoice_ids.invoice_line_ids.product_uom_id.factor_inv",
        # "order_id.invoice_ids.invoice_line_ids.product_uom_id.factor",
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

            line.total_vendidos = 0
            line.total_amount_sales = 0

            for invoice in line.order_id.invoice_ids:
                if not (invoice.state == 'posted' and invoice.move_type == 'out_invoice'):
                    continue

                quantity = 0

                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.product_id.id != line.product_id.id:
                        continue

                    if line.order_id.date_order and not line.date:
                        line.date = line.order_id.date_order

                    if line.order_id.branch_id and not invoice_line.branch_id:
                        invoice_line.branch_id = line.order_id.branch_id

                    if (
                        invoice_line.product_uom_id == invoice_line.product_id.uom_id
                        and invoice_line.quantity
                    ):
                        quantity = invoice_line.quantity
                    elif invoice_line.product_uom_id.uom_type == 'bigger':
                        quantity = invoice_line.quantity * (
                            invoice_line.product_uom_id.factor_inv / invoice_line.product_id.uom_id.factor_inv
                        )
                    elif invoice_line.product_uom_id.uom_type in {'smaller', 'reference'}:
                        quantity = invoice_line.quantity * invoice_line.product_id.uom_id.factor

                    line.quantity = quantity
                    line.total_vendidos = line.total_vendidos + line.quantity
                    line.total_amount_sales = line.total_amount_sales + line.amount_sale

    @api.depends(
        "total_vendidos",
        'state',
        "date",
        "team_id",
        "invoice_lines",
        "invoice_status",
        "product_id",
        "commission_id",
        "product_id.commission_ids",
        "product_id.commission_id",
        "product_id.commission_ids.commission_type",
        "product_id.commission_ids.cant_minima_base",
        "product_id.commission_ids.cant_min_base_otra_com",
    )
    def _compute_commissions(self):
        for line in self:
            if not (
                line.invoice_lines
                and line.product_id.commission_ids
                and line.total_vendidos != 0
                and line.date
                and line.team_id
            ):
                continue

            line.total_amount_commissions = 0

            first_day, last_day = get_first_and_last_day_of_month(line.date)
            lines = self.env['sale.order.line'].search([
                ('date', '>=', first_day),
                ('date', '<=', last_day),
                ('product_id', '=', line.product_id.id),
                ('team_id', '=', line.team_id.id),
                ('total_vendidos', '>', 0),
                ('product_id.commission_ids', '!=', False)
            ])

            if not lines:
                continue

            total_vendidos_mes = sum(lines.mapped("total_vendidos"))
            line_id = line.id
            len_lines = len(lines)

            print("python", total_vendidos_mes, len_lines)
            print("SQL", self.read_group(domain=[('date', '>=', first_day),
                ('date', '<=', last_day),
                ('product_id', '=', line.product_id.id),
                ('team_id', '=', line.team_id.id),
                ('total_vendidos', '>', 0),
                ('product_id.commission_ids', '!=', False)], fields=["total_vendidos:sum"], groupby=[]))



            for lin in lines:
                cumplen_fija_ids = []
                cumplen_bas_ids = []
                max_fija_c = False
                max_bas_c = False
                comission_max = False
                line.total_amount_commissions = 0

                for commission in line.product_id.commission_ids:
                    if commission.commission_type == 'fija':
                        if total_vendidos_mes >= commission.cant_minima_base:
                            cumplen_fija_ids.append(commission)
                    else:
                        if total_vendidos_mes >= commission.cant_min_base_otra_com:
                            cumplen_bas_ids.append(commission)

                if cumplen_fija_ids:
                    max_fija_c = max(cumplen_fija_ids, key=lambda x: x.cant_minima_base)

                if cumplen_bas_ids:
                    max_bas_c = max(cumplen_bas_ids, key=lambda x: x.cant_min_base_otra_com)

                if cumplen_fija_ids and cumplen_bas_ids:
                    if max_fija_c.cant_minima_base >= max_bas_c.cant_min_base_otra_com:
                        comission_max = max_fija_c
                    else:
                        comission_max = max_bas_c

                elif cumplen_fija_ids:
                    comission_max = max_fija_c

                elif cumplen_bas_ids:
                    comission_max = max_bas_c

                line.total_amount_commissions = 0

                if comission_max and (line.id == line_id):
                    len_lines = len(lines)

                    if comission_max.commission_type == 'fija':
                        if comission_max.forma_de_calculo == 'fijo':
                            line.total_amount_commissions = comission_max.bono_base / len_lines
                        else:
                            line.total_amount_commissions = (
                                total_vendidos_mes * comission_max.bono_base / comission_max.cant_minima_base
                            ) / len_lines
                    elif comission_max.commission_type == 'basada_en_otra_comision':
                        if comission_max.forma_de_calculo == 'fijo':
                            line.total_amount_commissions = comission_max.bono_base_otra_com / len_lines
                        else:
                            line.total_amount_commissions = (
                                total_vendidos_mes * comission_max.bono_base_otra_com / comission_max.cant_min_base_otra_com
                            ) / len_lines
                else:
                    line.total_amount_commissions = 0
