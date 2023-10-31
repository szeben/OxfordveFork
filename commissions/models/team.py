# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class TeamSaleReport(models.Model):
    _name = "team.sale.report"
    _description = "Reporte de comisiones asignadas"
    _auto = False
    _table_query = """
        WITH sol AS (
                SELECT
                    so.branch_id AS branch_id,
                    so.team_id AS team_id,
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
                    ) FILTER (
                        WHERE
                            sol.product_id = aml.product_id
                    ) AS total_sold,
                    SUM(
                        sol.price_subtotal / so.currency_rate
                    ) AS amount_sale, (
                        SELECT digits
                        FROM
                            decimal_precision
                        WHERE
                            name = 'Product Price'
                        LIMIT 1
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
                    AND so.date_order IS NOT NULL
                GROUP BY
                    so.branch_id,
                    so.team_id,
                    grouping_column,
                    DATE(
                        DATE_TRUNC('month', so.date_order)
                    )
            ),
            ucommissions AS (
                SELECT
                    aml.branch_id,
                    aml.team_id,
                    DATE(DATE_TRUNC('month', aml.date)) AS "date",
                    0.0 AS amount_sale,
                    0.0 AS total_sold,
                    0.0 AS total_amount_commissions,
                    aml.commission_by_collection AS commission_by_collection,
                    aml.debit AS debit
                FROM
                    account_move_line aml
                    LEFT JOIN account_account aa ON (aml.account_id = aa.id)
                WHERE
                    aml.parent_state = 'posted'
                    AND aa.collection_id IS NOT NULL
                    AND aml.debit != 0
                    AND aml.partner_id IS NOT NULL
                    AND aml.date IS NOT NULL
                UNION ALL
                SELECT
                    sol.branch_id,
                    sol.team_id,
                    sol."date",
                    sol.amount_sale,
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
                    ) AS total_amount_commissions,
                    0.0 AS commission_by_collection,
                    0.0 AS debit
                FROM sol
                WHERE
                    sol.total_sold > 0.0
            )
        SELECT
            ROW_NUMBER() OVER () AS id,
            ucommissions.branch_id,
            ucommissions.team_id,
            ucommissions.date,
            SUM(total_sold) AS total_vendidos,
            SUM(amount_sale) AS total_amount_sales,
            SUM(total_amount_commissions) AS total_amount_commissions,
            SUM(commission_by_collection) AS commission_by_collection,
            SUM(debit) AS debit,
            SUM(
                COALESCE(total_amount_commissions, 0) + COALESCE(commission_by_collection, 0)
            ) AS total_commissions
        FROM ucommissions
        WHERE
            ucommissions.date IS NOT NULL
        GROUP BY
            ucommissions.branch_id,
            ucommissions.team_id,
            ucommissions.date
        ORDER BY
            ucommissions.branch_id,
            ucommissions.team_id,
            ucommissions.date
    """

    branch_id = fields.Many2one(
        'res.branch',
        string="Sucursal",
        readonly=True
    )
    team_id = fields.Many2one(
        'crm.team',
        string="Equipo de ventas",
        readonly=True
    )

    date = fields.Date(
        string="Fecha",
        readonly=True
    )

    total_vendidos = fields.Float(
        string="Cantidad de ventas",
        readonly=True
    )
    total_amount_sales = fields.Float(
        string="Monto de las ventas",
        readonly=True
    )
    total_amount_commissions = fields.Float(
        string="Comisión asignada por las ventas",
        readonly=True
    )
    debit = fields.Float(
        string="Monto de la cobranza",
        readonly=True
    )
    commission_by_collection = fields.Float(
        string="Comisión por cobranza",
        readonly=True
    )
    total_commissions = fields.Float(
        string="Total de comisiones asignadas",
        readonly=True
    )
