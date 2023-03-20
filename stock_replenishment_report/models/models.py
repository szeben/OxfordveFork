# -*- coding: utf-8 -*-

from collections import OrderedDict
from itertools import chain, groupby, islice

from lxml import etree
from odoo import _, api, fields, models, tools
from odoo.osv.expression import OR

DEFAULT_MIN_BY_BRANCH = 2
DEFAULT_MIN_GLOBAL = 6


def get_name(branch_id):
    return branch_id.name.strip().lower()


class ResBranch(models.Model):
    _inherit = 'res.branch'

    is_main = fields.Boolean(
        string="¿Es la rama principal?",
        default=False
    )
    is_mainland = fields.Boolean(
        string="¿Esta en tierra firme?",
        default=True
    )
    warehouse_ids = fields.One2many(
        'stock.warehouse',
        'branch_id',
        string="Almacenes"
    )


class AccountJournal(models.Model):
    _inherit = "account.journal"

    input_type = fields.Selection(
        selection=[
            ('invoice', 'Factura'),
            ('delivery_note', 'Nota de entrega')
        ],
        string="Tipo de entrada",
        help='Campo de uso exclusivo para el informe "Reposición de Inventario"'
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
                        pt.categ_id AS categ_id,
                        rb.id AS branch_id,
                        pt.uom_id AS uom_id,
                        pp.active AS active,
                        CASE
                            WHEN uu.uom_type = 'reference' THEN 1.0
                            WHEN uu.uom_type = 'bigger' THEN CASE
                                WHEN uu.factor != 0.0
                                AND uu.factor IS NOT NULL THEN 1.0 / uu.factor
                                ELSE 0.0
                            END
                            ELSE uu.factor
                        END AS uom_ratio
                    FROM
                        product_product pp
                        CROSS JOIN res_branch rb
                        INNER JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                        INNER JOIN uom_uom uu ON (uu.id = pt.uom_id)
                    WHERE
                        pt.sale_ok = TRUE
                ),
                account_move_line_with_branch AS (
                    SELECT
                        aml.product_id,
                        aml.quantity,
                        am.invoice_date,
                        aj.input_type,
                        aj.branch_id,
                        aml.product_uom_id AS uom_id,
                        CASE
                            WHEN uu.uom_type = 'reference' THEN 1.0
                            WHEN uu.uom_type = 'bigger' THEN CASE
                                WHEN uu.factor != 0.0
                                AND uu.factor IS NOT NULL THEN 1.0 / uu.factor
                                ELSE 0.0
                            END
                            ELSE uu.factor
                        END AS uom_ratio
                    FROM
                        account_move_line aml
                        INNER JOIN uom_uom uu ON (uu.id = aml.product_uom_id)
                        LEFT OUTER JOIN account_move am ON (aml.move_id = am.id)
                        LEFT OUTER JOIN account_journal aj ON (am.journal_id = aj.id)
                    WHERE
                        aml.product_id IS NOT NULL
                        AND am.state = 'posted'
                        AND am.move_type = 'out_invoice'
                        AND aj.input_type IN ('invoice', 'delivery_note')
                )
            SELECT
                ROW_NUMBER() OVER () AS id,
                pb.categ_id,
                pb.product_id,
                COALESCE(aml.branch_id, pb.branch_id) AS branch_id,
                COALESCE(
                    aml.invoice_date,
                    CURRENT_DATE
                ) AS move_date,
                SUM(
                    CASE
                        WHEN aml.input_type = 'invoice' THEN CASE
                            WHEN aml.uom_id != pb.uom_id THEN aml.quantity * aml.uom_ratio / pb.uom_ratio
                            ELSE aml.quantity
                        END
                        ELSE 0.0
                    END
                ) AS qty_invoice,
                SUM(
                    CASE
                        WHEN aml.input_type = 'delivery_note' THEN CASE
                            WHEN aml.uom_id != pb.uom_id THEN aml.quantity * aml.uom_ratio / pb.uom_ratio
                            ELSE aml.quantity
                        END
                        ELSE 0.0
                    END
                ) AS qty_delivery_note,
                COALESCE(
                    SUM(
                        CASE
                            WHEN aml.uom_id != pb.uom_id THEN aml.quantity * aml.uom_ratio / pb.uom_ratio
                            ELSE aml.quantity
                        END
                    ),
                    0.0
                ) AS quantity
            FROM product_with_branch pb
                LEFT JOIN account_move_line_with_branch aml ON (
                    pb.product_id = aml.product_id AND pb.branch_id = aml.branch_id
                )
            WHERE pb.active = TRUE
            GROUP BY
                pb.product_id,
                pb.branch_id,
                aml.branch_id,
                aml.invoice_date,
                pb.categ_id
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
    categ_id = fields.Many2one(
        'product.category',
        'Categoría',
        readonly=True
    )
    branch_id = fields.Many2one(
        'res.branch',
        'Rama',
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
            'readonly': True,
            'required': False,
            'searchable': False,
            'sortable': False,
            'store': False,
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

            if not branch.is_main:
                alerts[f"replenishment_{name}"] = {
                    **default_values,
                    "type": 'boolean',
                    "string": f"Rep. {branch.name}?"
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

        if view_type == 'tree':
            doc = etree.fromstring(res['arch'])

            for name, field in self._dynamic_fields().items():
                doc.append(etree.Element('field', name=name, optional="show"))
                res['fields'][name] = field

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    @api.model
    def search_count(self, args):
        return len(super()._read_group_raw(args, ['product_id'], ['product_id']))

    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        fields = fields and list(set(fields).difference(self._dynamic_fields().keys()))
        return super()._read_group_raw(domain, fields, groupby, offset, limit, orderby, lazy)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        def keyfunc_product(record):
            return record.product_id

        def keyfun_branch(record):
            return record.branch_id

        min_by_branch = self.min_by_branch
        min_global = self.min_global
        branches = self.env['res.branch'].search([])

        data = []

        if domain is None:
            groups = groupby(self, keyfunc_product)
        else:
            groups = groupby(super().search(domain), keyfunc_product)

        if offset:
            if limit:
                groups = islice(groups, offset, offset + limit)
            else:
                groups = islice(groups, offset, None)
        elif limit:
            groups = islice(groups, limit)

        groups = tuple((product_id, tuple(rows)) for product_id, rows in groups)
        product_ids = [product.id for product, _ in groups]

        virtual_availables = {
            branch_id.id: {
                product_id: values['virtual_available']
                for product_id, values in self.env['product.product'].with_context(
                    warehouse=branch_id.warehouse_ids.ids
                ).search([
                    ('id', 'in', product_ids)
                ])._compute_quantities_dict(None, None, None).items()
                if values.get('virtual_available')
            } for branch_id in branches
        }

        for product_id, group_product in groups:
            row = {
                "product_id": (product_id.id, product_id.display_name),
                "categ_id": (product_id.categ_id.id, product_id.categ_id.name),
            }

            stock = 0.0
            stock_main = 0.0
            stock_mainland = 0.0
            total_quantity_mainland = 0.0

            for branch_id, group_branch in groupby(group_product, keyfun_branch):
                branch_name = get_name(branch_id)
                row[f"inv_{branch_name}"] = virtual_available = (
                    virtual_availables[branch_id.id].get(product_id.id, 0.0)
                )

                qty_invoice, qty_delivery_note, quantity = map(
                    sum,
                    zip(*(
                        (record.qty_invoice, record.qty_delivery_note, record.quantity)
                        for record in group_branch
                    ))
                )

                stock = virtual_available / (quantity or 1.0)

                row[f"invoice_{branch_name}"] = qty_invoice
                row[f"refund_{branch_name}"] = qty_delivery_note
                row[f"quantity_{branch_name}"] = quantity
                row[f"stock_{branch_name}"] = stock

                if branch_id.is_mainland:
                    stock_mainland += virtual_available
                    total_quantity_mainland += quantity

                if branch_id.is_main:
                    stock_main += stock

            row["stock_mainland"] = stock_mainland / (total_quantity_mainland or 1.0)

            for branch_id in branches:
                branch_name = get_name(branch_id)
                stock_field = f"stock_{branch_name}"
                replenishment_field = f"replenishment_{branch_name}"

                if not branch_id.is_main:
                    row[replenishment_field] = stock_field in row and row[stock_field] < min_by_branch and stock_main > min_global

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
