# -*- coding: utf-8 -*-

from collections import OrderedDict
from itertools import chain
from typing import Union

from lxml import etree
from odoo import _, api, fields, models
from odoo.osv.expression import (AND, AND_OPERATOR, OR_OPERATOR, is_leaf,
                                 is_operator, normalize_leaf)
from odoo.tools.func import lazy

DEFAULT_MIN_BY_BRANCH = 2
DEFAULT_MIN_GLOBAL = 6


def remove_fields_from_domain(domain: list, fields: Union[list, tuple, set]) -> list:
    new_domain = []

    for i, elm in enumerate(domain):
        if is_leaf(elm) and (normalize_leaf(elm)[0] in fields):
            for j, olm in enumerate(new_domain[::-1]):
                if is_operator(olm):
                    new_domain.pop(-j-1)
                    if olm in {AND_OPERATOR, OR_OPERATOR}:
                        break
            continue
        new_domain.append(elm)

    return new_domain


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
        query = """
            SELECT
                ROW_NUMBER() OVER () AS id,
                pp.id AS product_id,
                pt.categ_id AS categ_id,
                CURRENT_DATE AS move_date
            FROM product_product pp
                INNER JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            WHERE pp.active = TRUE AND pt.sale_ok = TRUE
            ORDER BY pp.id
        """
        return query

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
    move_date = fields.Date(
        'Fecha de movimiento',
        readonly=True
    )

    data_domain = {}

    @api.model
    def _where_calc(self, domain):
        self.data_domain.update(domain=domain)
        return super()._where_calc(
            remove_fields_from_domain(domain, ['move_date'])
        )

    def _generate_fields(self):
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

            sales[f"qty_invoice_{name}"] = {
                **default_values,
                "type": 'float',
                'group_operator': False,
                "string": f"Fact. {branch.name}"
            }
            sales[f"qty_delivery_note_{name}"] = {
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

            for name, field in self._generate_fields().items():
                doc.append(etree.Element('field', name=name, optional="show"))
                res['fields'][name] = field

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    def _clean_fields(self, fields: list):
        new_fields = []
        generated_fields = set(self._generate_fields().keys())
        for field in fields:
            if not field in generated_fields:
                new_fields.append(field)
        return new_fields

    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        fields = self._clean_fields(fields)
        return super()._read_group_raw(domain, fields, groupby, offset, limit, orderby, lazy)

    def _compute_columns(self, domain: list, product_ids: list):
        min_by_branch = self.min_by_branch
        min_global = self.min_global

        branches = self.env['res.branch'].search([])
        query = super()._where_calc(AND([domain, [('product_id', 'in', product_ids)]]))
        query._tables[self._table] = """
            SELECT
                pt.categ_id AS categ_id,
                aml.product_id AS product_id,
                am.invoice_date AS move_date,
                am.move_type AS move_type,
                aj.input_type AS input_type,
                aj.branch_id AS branch_id,
                CASE
                    WHEN aml.product_uom_id != pt.uom_id THEN aml.quantity * (
                        CASE
                            WHEN uu.uom_type = 'reference' THEN 1.0
                            WHEN uu.uom_type = 'bigger' THEN CASE
                                WHEN uu.factor != 0.0
                                AND uu.factor IS NOT NULL THEN 1.0 / uu.factor
                                ELSE 0.0
                            END
                            ELSE uu.factor
                        END
                    ) / (
                        CASE
                            WHEN puu.uom_type = 'reference' THEN 1.0
                            WHEN puu.uom_type = 'bigger' THEN CASE
                                WHEN puu.factor != 0.0
                                AND puu.factor IS NOT NULL THEN 1.0 / puu.factor
                                ELSE 0.0
                            END
                            ELSE puu.factor
                        END
                    )
                    ELSE aml.quantity
                END AS quantity
            FROM account_move_line aml
                LEFT OUTER JOIN account_move am ON (aml.move_id = am.id)
                LEFT OUTER JOIN account_journal aj ON (am.journal_id = aj.id)
                INNER JOIN uom_uom uu ON (uu.id = aml.product_uom_id)
                INNER JOIN product_product pp ON (pp.id = aml.product_id)
                INNER JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                INNER JOIN uom_uom puu ON (puu.id = pt.uom_id)
            WHERE
                aml.product_id IS NOT NULL
                AND am.state = 'posted'
                AND am.move_type IN ('out_invoice', 'out_refund')
                AND aj.input_type IN ('invoice', 'delivery_note')
        """

        alias_str = []
        alias_params = []

        for branch in branches:
            name = get_name(branch)
            alias_str.extend([
                (
                    'SUM(CASE WHEN input_type = \'invoice\' AND branch_id = %s AND move_type = \'out_invoice\' THEN quantity ELSE 0.0 END) '
                    '- SUM(CASE WHEN input_type = \'invoice\' AND branch_id = %s AND move_type = \'out_refund\' THEN quantity ELSE 0.0 END) '
                    f'AS "qty_invoice_{name}"'
                ),
                (
                    'SUM(CASE WHEN input_type = \'delivery_note\' AND branch_id = %s AND move_type = \'out_invoice\' THEN quantity ELSE 0.0 END) '
                    '- SUM(CASE WHEN input_type = \'delivery_note\' AND branch_id = %s AND move_type = \'out_refund\' THEN quantity ELSE 0.0 END) '
                    f'AS "qty_delivery_note_{name}"'
                ),
                (
                    'SUM(CASE WHEN branch_id = %s THEN CASE WHEN move_type = \'out_refund\' THEN -quantity ELSE quantity END ELSE 0.0 END) '
                    f'AS "quantity_{name}"'
                ),
            ])
            alias_params.extend([branch.id, branch.id, branch.id, branch.id, branch.id])

        query_str, params = query.subselect("*")
        query_str = f"""
            SELECT product_id, {', '.join(alias_str)}
            FROM ({query_str}) AS tmp
            GROUP BY tmp.product_id ORDER BY tmp.product_id
        """
        params = alias_params + params

        virtual_availables = {
            branch.id: {
                product_id: values['virtual_available']
                for product_id, values in self.env['product.product'].with_context(
                    warehouse=branch.warehouse_ids.ids
                ).search([
                    ('id', 'in', product_ids)
                ])._compute_quantities_dict(None, None, None).items()
                if values.get('virtual_available')
            } for branch in branches
        }

        self.env.cr.execute(query_str, params)
        rows = self.env.cr.dictfetchall()
        product_data = {}

        for row in rows:
            stock = 0.0
            stock_main = 0.0
            stock_mainland = 0.0
            total_quantity_mainland = 0.0
            product_id = row["product_id"]

            for branch_id in branches:
                branch_name = get_name(branch_id)

                row[f"inv_{branch_name}"] = virtual_available = (
                    virtual_availables[branch_id.id].get(product_id) or 0.0
                )

                quantity = row[f"quantity_{branch_name}"]
                stock = (virtual_available / quantity) if quantity else 0.0
                row[f"stock_{branch_name}"] = stock

                if branch_id.is_mainland:
                    stock_mainland += virtual_available
                    total_quantity_mainland += quantity

                if branch_id.is_main:
                    stock_main += stock
                else:
                    row[f"replenishment_{branch_name}"] = stock < min_by_branch and stock_main > min_global

            row["stock_mainland"] = stock_mainland / (total_quantity_mainland or 1.0)
            row["order_is_required"] = stock < min_global

            product_data[product_id] = row

        return product_data

    def _generate_default_data(self):
        values = {}

        for name, descrip in self._generate_fields().items():
            if descrip['type'] == 'boolean':
                values[name] = False
            else:
                values[name] = 0.0

        return values

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        res = super().search_read(domain, self._clean_fields(fields), offset, limit, order, **read_kwargs)

        product_ids = self.mapped('product_id').ids or tuple(row["product_id"][0] for row in res)
        product_data = self._compute_columns(domain, product_ids)
        default_data = lazy(self._generate_default_data)

        return [
            {
                **row,
                **{
                    k: v for k, v in (
                        product_data.get(row["product_id"][0])
                        or default_data
                    ).items() if k in fields
                },
                "product_id": row["product_id"]
            } for row in res
        ]

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
        generated_fields = set(self._generate_fields()).union(['move_date'])
        model_fields = []
        selected_fields = []

        for field in fields:
            if all(name not in generated_fields for name in field):
                model_fields.append(field)
            else:
                selected_fields.extend(field)

        res = super()._export_rows(model_fields, _is_toplevel_call=_is_toplevel_call)
        product_ids = self.mapped("product_id").ids
        product_data = self._compute_columns(self.data_domain.get('domain', []), product_ids)
        default_data = lazy(self._generate_default_data)

        for product_id, row in zip(product_ids, res):
            data = product_data.get(product_id) or default_data
            row.extend([data.get(name) for name in selected_fields])

        return sorted(res, key=lambda row: row[0])
