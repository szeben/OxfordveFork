# -*- coding: utf-8 -*-

from itertools import chain, groupby, islice
from collections import OrderedDict
from datetime import timedelta

from lxml import etree
from odoo import _, api, fields, models, tools

DEFAULT_MIN_BY_BRANCH = 2
DEFAULT_MIN_GLOBAL = 6


def get_name(branch_id):
    return branch_id.name.strip().lower()


class ResBranch(models.Model):
    _inherit = 'res.branch'

    is_main = fields.Boolean(string="¿Es la rama principal?", default=False)
    is_mainland = fields.Boolean(string="¿Esta en tierra firme?", default=True)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    input_type = fields.Selection(
        selection=[
            ('invoice', 'Factura'),
            ('delivery_note', 'Nota de entrega')
        ],
        string="Tipo de entrada",
    )


class StockReplenishmentReport(models.Model):
    _name = 'stock.replenishment.report'
    _description = 'Stock Replenishment Report'
    _auto = False

    @property
    def _table_query(self):
        select_ = """
            WITH product_with_branch AS (
                    SELECT
                        pp.id AS product_id,
                        rb.id AS branch_id
                    FROM
                        product_product pp
                        CROSS JOIN res_branch rb
                        INNER JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                    WHERE
                        pt.sale_ok = TRUE
                ),
                account_move_line_with_branch AS (
                    SELECT
                        aml.product_id,
                        aml.quantity,
                        am.invoice_date,
                        aj.input_type,
                        aj.branch_id
                    FROM
                        account_move_line aml
                        LEFT OUTER JOIN account_move am ON (aml.move_id = am.id)
                        LEFT OUTER JOIN account_journal aj ON (am.journal_id = aj.id)
                    WHERE
                        aml.product_id IS NOT NULL
                        AND am.state = 'posted'
                        AND am.move_type = 'out_invoice'
                        AND aj.input_type IS NOT NULL
                )
            SELECT
                ROW_NUMBER() OVER () AS id,
                pb.product_id,
                COALESCE(aml.branch_id, pb.branch_id) AS branch_id,
                aml.invoice_date AS move_date, (
                    SELECT sq.id
                    FROM stock_quant sq
                        LEFT JOIN stock_warehouse sw ON (
                            sw.lot_stock_id = sq.location_id
                        )
                    WHERE
                        COALESCE(aml.branch_id, pb.branch_id) = sw.branch_id
                        AND sw.is_main = TRUE
                        AND sq.product_id = pb.product_id
                    ORDER BY
                        sw.write_date DESC
                    LIMIT
                        1
                ) AS quant_id,
                SUM(
                    CASE
                        WHEN aml.input_type = 'invoice' THEN aml.quantity
                        ELSE 0.0
                    END
                ) AS qty_invoice,
                SUM(
                    CASE
                        WHEN aml.input_type = 'delivery_note' THEN aml.quantity
                        ELSE 0.0
                    END
                ) AS qty_delivery_note,
                COALESCE(SUM(aml.quantity), 0.0) AS quantity
            FROM product_with_branch pb
                LEFT JOIN account_move_line_with_branch aml ON (
                    pb.product_id = aml.product_id AND pb.branch_id = aml.branch_id
                )
            GROUP BY
                pb.product_id,
                pb.branch_id,
                aml.branch_id,
                aml.invoice_date
            ORDER BY
                pb.product_id,
                pb.branch_id,
                aml.branch_id,
                aml.invoice_date
        """
        return select_

    product_id = fields.Many2one(
        'product.product',
        'Producto',
        readonly=True
    )
    branch_id = fields.Many2one(
        'res.branch',
        'Rama',
        readonly=True
    )
    quant_id = fields.Many2one(
        'stock.quant',
        'Cantidad',
        readonly=True
    )
    qty_on_hand = fields.Float(
        'Depósito',
        related='quant_id.inventory_quantity_auto_apply',
        readonly=True
    )
    move_date = fields.Date(
        'Fecha de movimiento',
        readonly=True
    )
    qty_invoice = fields.Float(
        'Cantidad por factura',
        readonly=True
    )
    qty_delivery_note = fields.Float(
        'Cantidad por nota de entrega',
        readonly=True
    )
    quantity = fields.Float(
        'Cantidad total',
        readonly=True
    )

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        return self._search_read_report(domain, fields, offset, limit, order, **read_kwargs)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        fields = {'product_id', 'branch_id', 'move_date'}
        for field in filter(lambda name: name not in fields, res):
            res[field]['searchable'] = False
        return res

    def _dynamic_fields(self):
        main_deposit = OrderedDict()
        sales = OrderedDict()
        stock = OrderedDict()
        alerts = OrderedDict()

        default_values = {
            'change_default': False,
            'depends': (),
            'company_dependent': False,
            'manual': False,
            'readonly': False,
            'required': False,
            'searchable': False,
            'sortable': True,
            'store': True,
        }

        for branch in self.env['res.branch'].search([]):
            name = branch.name.strip().lower()
            main_deposit[f"inv_{name}"] = {
                **default_values,
                "type": 'float',
                "group_operator": False,
                "string": f"Inv. {branch.name}"
            }

            sales[f"invoice_{name}"] = {
                **default_values,
                "type": 'float',
                'group_operator': False,
                "string": f"Fact. {branch.name}"
            }
            sales[f"refund_{name}"] = {
                **default_values,
                "type": 'float',
                'group_operator': False,
                "string": f"N.E. {branch.name}"
            }
            sales[f"quantity_{name}"] = {
                **default_values,
                "type": 'float',
                'group_operator': False,
                "string": f"Ventas {branch.name}"
            }
            stock[f"stock_{name}"] = {
                **default_values,
                "type": 'float',
                'group_operator': False,
                "string": f"Stock {branch.name}"
            }

            if branch.is_mainland:
                alerts[f"replenishment_{name}"] = {
                    **default_values,
                    "type": 'boolean',
                    "string": f"Reposición {branch.name}?"
                }

        stock[f"stock_mainland"] = {
            **default_values,
            "type": 'float',
            'group_operator': False,
            "string": f"Stock Tierra Firme"
        }
        alerts["order_is_required"] = {
            **default_values,
            "type": 'boolean',
            "string": "Pedido a Proveedor?"
        }

        return OrderedDict(
            map(
                lambda item: (item[0], {**item[1], "name": item[0]}),
                chain(
                    main_deposit.items(),
                    sales.items(),
                    stock.items(),
                    alerts.items()
                )
            )
        )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id, view_type, toolbar, submenu)

        if view_type in {'search', 'tree'}:
            doc = etree.fromstring(res['arch'])

            if view_type == 'tree':
                for name, field in self._dynamic_fields().items():
                    doc.append(
                        etree.Element('field', name=name, optional="show")
                    )
                    res['fields'][name] = field

            else:
                date_last_15_days = fields.Date.to_string(
                    fields.Date.today() - timedelta(days=15)
                )
                doc.append(
                    etree.Element(
                        'filter',
                        name='last_fortnight_move_date',
                        string="Ultimos 15 días",
                        domain=str([('move_date', '>=', date_last_15_days)])
                    )
                )

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    @api.model
    def search_count(self, args):
        return len(self._read_group_raw(args, ['product_id'], ['product_id']))

    def _search_read_report(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        def keyfunc_product(record):
            return record.product_id

        def keyfun_branch(record):
            return record.branch_id

        min_by_branch = self.min_by_branch
        min_global = self.min_global
        branches = self.env['res.branch'].search([])

        data = []
        groups = groupby(
            self if domain is None else self.search(domain),
            keyfunc_product
        )

        if limit or offset:
            if limit:
                limit = offset + limit
                groups = islice(groups, offset, limit)
            else:
                groups = islice(groups, offset, None)

        for product_id, group_product in groups:
            row = {"product_id": (product_id.id, product_id.display_name)}

            stock_main = 0.0
            stock_mainland = 0.0

            for branch_id, group_branch in groupby(group_product, keyfun_branch):
                first = next(group_branch)

                branch_name = get_name(branch_id)
                row[f"inv_{branch_name}"] = qty_on_hand = first.qty_on_hand

                qty_invoice, qty_delivery_note, quantity = map(
                    sum,
                    zip(*(
                        (record.qty_invoice, record.qty_delivery_note, record.quantity)
                        for record in chain((first,), group_branch)
                    ))
                )
                stock = qty_on_hand/quantity

                row[f"invoice_{branch_name}"] = qty_invoice
                row[f"refund_{branch_name}"] = qty_delivery_note
                row[f"quantity_{branch_name}"] = quantity
                row[f"stock_{branch_name}"] = stock

                if branch_id.is_mainland:
                    stock_mainland += stock

                if branch_id.is_main:
                    stock_main += stock

            row["stock_mainland"] = stock_mainland

            for branch_id in branches:
                branch_name = get_name(branch_id)
                stock_field = f"stock_{branch_name}"
                replenishment_field = f"replenishment_{branch_name}"

                if not branch_id.is_main:
                    if stock_field in row:
                        row[replenishment_field] = (
                            row[stock_field] < min_by_branch and stock_main > min_global
                        )
                    else:
                        row[replenishment_field] = False

                for field in ("inv", "invoice", "refund", "quantity", "stock"):
                    if f"{field}_{branch_name}" not in row:
                        row[f"{field}_{branch_name}"] = 0.0

            row["order_is_required"] = stock < min_global

            if fields:
                row = {key: row[key] for key in fields if key in row}
            data.append(row)

        if order and data and order in data[0]:
            return sorted(data, key=lambda x: x[order])

        return data

    @property
    def min_by_branch(self):
        value = self.env['ir.config_parameter'].sudo().get_param(
            'stock_replenishment_report.min_by_branch',
            DEFAULT_MIN_BY_BRANCH
        )

        try:
            value = int(value)
        except ValueError:
            value = DEFAULT_MIN_BY_BRANCH

        return value

    @property
    def min_global(self):
        value = self.env['ir.config_parameter'].sudo().get_param(
            'stock_replenishment_report.min_global',
            DEFAULT_MIN_GLOBAL
        )

        try:
            value = int(value)
        except ValueError:
            value = DEFAULT_MIN_GLOBAL

        return value

    def _export_rows(self, fields, *, _is_toplevel_call=True):
        lines = []

        for record in self._search_read_report():
            current = [''] * len(fields)
            lines.append(current)

            primary_done = []

            for index, path in enumerate(fields):
                if not path:
                    continue

                name, *path = path

                if name in primary_done or path:
                    continue

                value = record.get(name)

                if isinstance(value, tuple):
                    value = value[-1]
                elif isinstance(value, bool):
                    value = "SI" if value else "NO"

                current[index] = value

        return lines
