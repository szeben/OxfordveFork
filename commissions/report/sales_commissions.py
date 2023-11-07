# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionSalesReportMixin(models.AbstractModel):
    _name = "commissions.sales.report.mixin"
    _description = "Reporte de comisiones de ventas"

    branch_id = fields.Many2one(
        "res.branch",
        string="Sucursal",
        readonly=True
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Equipo de ventas",
        readonly=True
    )
    date = fields.Date(
        string="Fecha",
        readonly=True
    )

    amount_sale = fields.Float(
        string="Monto de venta",
        readonly=True
    )
    total_sold = fields.Float(
        string="Total vendidos",
        readonly=True
    )
    amount_commissions = fields.Float(
        string="Comisión total",
        readonly=True
    )

    def _get_with_query(self, *args: str):
        return "WITH " + ", ".join(
            f"{key} AS ({self._with_querys[key]})"
            for key in args
        ) + " "

    def _generate_commission_query(
        self,
        commission_table: str,
        data_table: str,
        field_name: str,
        use_id: bool = True
    ):
        ct = commission_table
        dt = data_table
        fn = field_name

        extra_fields = ""

        if use_id:
            extra_fields = f"""
                ROW_NUMBER() OVER () AS "id",
            """

        return f"""
            SELECT {extra_fields} "{dt}".*, (
                    SELECT
                        CASE "{ct}".forma_de_calculo
                            WHEN 'fijo' THEN "{ct}".basic_bonus
                            WHEN 'regla_de_tres' THEN "{dt}".total_sold * "{ct}".basic_bonus / "{ct}".base_min_qty
                        END
                    FROM "{ct}"
                    WHERE
                        "{dt}"."{fn}" = "{ct}"."{fn}"
                        AND ROUND(
                            "{dt}".total_sold,
                            COALESCE(dp.digits, 2)
                        ) >= ROUND(
                            "{ct}".base_min_qty :: NUMERIC,
                            COALESCE(dp.digits, 2)
                        )
                    ORDER BY "{ct}".base_min_qty DESC
                    LIMIT 1
                ) AS amount_commissions
            FROM "{dt}"
                LEFT JOIN (
                    SELECT digits
                    FROM decimal_precision
                    WHERE name = 'Commission'
                    LIMIT 1
                ) dp ON (TRUE)
        """

    _with_querys = {
        "sol": """
            SELECT
                sr.branch_id AS branch_id,
                sr.team_id AS team_id,
                sr.categ_id AS categ_id,
                pp.commission_group_id AS group_id,
                sr.product_id AS product_id,
                DATE(DATE_TRUNC('month', sr."date")) AS "date",
                sr.qty_invoiced AS total_sold,
                sr.untaxed_amount_invoiced AS amount_sale,
                pp.commission_by_category
            FROM sale_report sr
            LEFT JOIN product_product pp ON (pp.id = sr.product_id)
        """,
        "_sol": """
            SELECT
                so.branch_id AS branch_id,
                so.team_id AS team_id,
                sol_pt.categ_id AS categ_id,
                sol_pp.commission_group_id AS group_id,
                sol.product_id AS product_id,
                sol_pp.commission_by_category AS commission_by_category,
                DATE(
                    DATE_TRUNC('month', so.date_order)
                ) AS "date", (
                    CASE am.move_type
                        WHEN 'out_invoice' THEN aml.quantity
                        WHEN 'out_refund' THEN - aml.quantity
                    END / aml_uom.factor * pt_uom.factor
                ) AS total_sold,
                sol.price_subtotal / so.currency_rate AS amount_sale
            FROM
                sale_order_line sol
                INNER JOIN sale_order so ON (so.id = sol.order_id)
                INNER JOIN sale_order_line_invoice_rel solir ON (solir.order_line_id = sol.id)
                INNER JOIN account_move_line aml ON (aml.id = solir.invoice_line_id)
                INNER JOIN account_move am ON (am.id = aml.move_id)
                LEFT JOIN product_product sol_pp ON (sol_pp.id = sol.product_id)
                LEFT JOIN product_template sol_pt ON (
                    sol_pt.id = sol_pp.product_tmpl_id
                )
                LEFT JOIN product_product aml_pp ON (aml_pp.id = aml.product_id)
                LEFT JOIN product_template aml_pt ON (
                    aml_pt.id = aml_pp.product_tmpl_id
                )
                LEFT JOIN uom_uom pt_uom ON (pt_uom.id = aml_pt.uom_id)
                LEFT JOIN uom_uom aml_uom ON (
                    aml_uom.id = aml.product_uom_id
                )
            WHERE
                so.state = 'done'
                AND am.state = 'posted'
                AND am.move_type IN ('out_invoice', 'out_refund')
                AND aml.product_id IS NOT NULL
                AND so.date_order IS NOT NULL
                AND sol.product_id = aml.product_id
        """,
        "summary_group": """
            SELECT
                sol.branch_id,
                sol.team_id,
                sol.group_id,
                sol.product_id,
                sol."date",
                SUM(sol.total_sold) AS total_sold,
                SUM(sol.amount_sale) AS amount_sale
            FROM sol
            WHERE
                sol.group_id IS NOT NULL
            GROUP BY
                sol.branch_id,
                sol.team_id,
                sol.group_id,
                sol.product_id,
                sol."date"
        """,
        "summary_product": """
            SELECT
                sol.branch_id,
                sol.team_id,
                sol.categ_id,
                sol.product_id,
                sol."date",
                SUM(sol.total_sold) AS total_sold,
                SUM(sol.amount_sale) AS amount_sale
            FROM sol
            WHERE
                sol.group_id IS NULL
            GROUP BY
                sol.branch_id,
                sol.team_id,
                sol.categ_id,
                sol.product_id,
                sol."date"
        """,
        "summary_category": """
            SELECT
                sol.branch_id,
                sol.team_id,
                sol.categ_id,
                sol."date",
                SUM(sol.total_sold) AS total_sold,
                SUM(sol.amount_sale) AS amount_sale
            FROM sol
            WHERE
                sol.commission_by_category IS TRUE
            GROUP BY
                sol.branch_id,
                sol.team_id,
                sol.categ_id,
                sol."date"
        """,
    }


class CommissionSalesReport(models.Model):
    _name = "commissions.sales.report"
    _description = "Reporte de comisiones de ventas por producto"
    _inherit = "commissions.sales.report.mixin"
    _auto = False

    @property
    def _table_query(self) -> str:
        return self._get_with_query(
            'sol',
            'summary_product'
        ) + self._generate_commission_query(
            "commission_for_sale",
            "summary_product",
            "product_id"
        )

    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        readonly=True
    )
    categ_id = fields.Many2one(
        "product.category",
        string="Categoría",
        readonly=True
    )


class CommissionSalesGroupReport(models.Model):
    _name = "commissions.sales.group.report"
    _description = "Reporte de comisiones de ventas por grupo"
    _inherit = "commissions.sales.report.mixin"
    _auto = False

    @property
    def _table_query(self):
        return self._get_with_query(
            'sol',
            'summary_group'
        ) + self._generate_commission_query(
            "commission_for_group",
            "summary_group",
            "group_id"
        )

    group_id = fields.Many2one(
        "commission.group",
        string="Grupo de comisiones",
        readonly=True
    )
    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        readonly=True
    )


class CommissionSalesCalegoryReport(models.Model):
    _name = "commissions.sales.category.report"
    _description = "Reporte de comisiones de ventas por categoría"
    _inherit = "commissions.sales.report.mixin"
    _auto = False

    @property
    def _table_query(self):
        return self._get_with_query(
            'sol',
            'summary_category'
        ) + self._generate_commission_query(
            "commission_for_category",
            "summary_category",
            "categ_id"
        )

    categ_id = fields.Many2one(
        "product.category",
        string="Categoría",
        readonly=True
    )
