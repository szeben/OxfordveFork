# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionSalesReport(models.Model):
    _name = "commissions.sales.report"
    _description = "Reporte de comisiones de ventas"
    _auto = False
    _table_query = """
        WITH sol AS (
                SELECT
                    so.branch_id AS branch_id,
                    so.team_id AS team_id,
                    MIN(sol_pt.categ_id) AS categ_id,
                    COALESCE(
                        - sol_pp.commission_group_id,
                        sol.product_id
                    ) AS grouping_column,
                    DATE(
                        DATE_TRUNC('month', so.date_order)
                    ) AS "date",
                    SUM(
                        CASE am.move_type
                            WHEN 'out_invoice' THEN aml.quantity
                            WHEN 'out_refund' THEN - aml.quantity
                        END / aml_uom.factor * pt_uom.factor
                    ) FILTER(
                        WHERE
                            sol.product_id = aml.product_id
                    ) AS total_sold,
                    SUM(
                        sol.price_subtotal / so.currency_rate
                    ) AS amount_sale,
                    COALESCE( (
                            SELECT digits
                            FROM
                                decimal_precision
                            WHERE
                                name = 'Commission'
                            LIMIT
                                1
                        ), 2
                    ) AS dp
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
                GROUP BY
                    so.branch_id,
                    so.team_id,
                    grouping_column,
                    DATE(
                        DATE_TRUNC('month', so.date_order)
                    )
            )
        SELECT
            ROW_NUMBER() OVER () AS id,
            sol.branch_id,
            sol.team_id,
            sol.categ_id,
            sol."date",
            sol.amount_sale,
            CASE
                WHEN sol.grouping_column < 0 THEN NULL
                ELSE sol.grouping_column
            END AS product_id,
            CASE
                WHEN sol.grouping_column < 0 THEN - sol.grouping_column
                ELSE NULL
            END AS commission_group_id,
            sol.total_sold,
            COALESCE(
                CASE
                    WHEN sol.grouping_column > 0 THEN (
                        SELECT
                            CASE cfs.forma_de_calculo
                                WHEN 'fijo' THEN cfs.basic_bonus
                                WHEN 'regla_de_tres' THEN sol.total_sold * cfs.basic_bonus / cfs.base_min_qty
                            END
                        FROM
                            commission_for_sale cfs
                        WHERE
                            cfs.product_id = sol.grouping_column
                            AND ROUND(sol.total_sold, sol.dp) >= ROUND(
                                cfs.base_min_qty :: NUMERIC,
                                sol.dp
                            )
                        ORDER BY
                            cfs.base_min_qty DESC
                        LIMIT
                            1
                    )
                    WHEN sol.grouping_column < 0 THEN (
                        SELECT
                            CASE cfg.forma_de_calculo
                                WHEN 'fijo' THEN cfg.basic_bonus
                                WHEN 'regla_de_tres' THEN sol.total_sold * cfg.basic_bonus / cfg.base_min_qty
                            END
                        FROM
                            commission_for_group cfg
                        WHERE
                            - sol.grouping_column = cfg.group_id
                            AND ROUND(sol.total_sold, sol.dp) >= ROUND(
                                cfg.base_min_qty :: NUMERIC,
                                sol.dp
                            )
                        ORDER BY
                            cfg.base_min_qty DESC
                        LIMIT
                            1
                    )
                END,
                0.0
            ) AS total_amount_commissions
        FROM sol
        WHERE sol.total_sold > 0.0
    """

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
    categ_id = fields.Many2one(
        "product.category",
        string="Categoría",
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
    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        readonly=True
    )
    commission_group_id = fields.Many2one(
        "commission.group",
        string="Grupo de comisiones",
        readonly=True
    )
    total_sold = fields.Float(
        string="Total vendidos",
        readonly=True
    )
    total_amount_commissions = fields.Float(
        string="Comisión total",
        readonly=True
    )
