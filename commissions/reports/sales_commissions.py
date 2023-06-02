# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionSalesCommissionReport(models.Model):
    _name = "commissions.sales.report"
    _description = "Reporte de comisiones de ventas"
    _auto = False
    _table_query = """
        WITH order_totals AS (
                SELECT
                    branch_id,
                    DATE(date_order) AS "date",
                    team_id,
                    SUM(amount_total) AS total
                FROM sale_order
                WHERE state = 'done'
                GROUP BY
                    branch_id,
                    DATE(date_order),
                    team_id
            ),
            sol1 AS (
                SELECT
                    so.branch_id AS branch_id,
                    COALESCE(cfg.categ_id, pt.categ_id) AS categ_id,
                    so.team_id AS team_id,
                    DATE(so.date_order) AS "date",
                    sol.product_id AS product_id,
                    pp.commission_group_id AS commission_group_id,
                    MIN(ot.total) AS amount_sale,
                    SUM(
                        CASE
                            WHEN aml.product_uom_id != aml_pt.uom_id THEN aml.quantity * (
                                CASE
                                    WHEN aml_uu.uom_type = 'reference' THEN 1.0
                                    WHEN aml_uu.uom_type = 'bigger' THEN CASE
                                        WHEN aml_uu.factor != 0.0
                                        AND aml_uu.factor IS NOT NULL THEN 1.0 / aml_uu.factor
                                        ELSE 0.0
                                    END
                                    ELSE aml_uu.factor
                                END
                            ) / (
                                CASE
                                    WHEN aml_puu.uom_type = 'reference' THEN 1.0
                                    WHEN aml_puu.uom_type = 'bigger' THEN CASE
                                        WHEN aml_puu.factor != 0.0
                                        AND aml_puu.factor IS NOT NULL THEN 1.0 / aml_puu.factor
                                        ELSE 0.0
                                    END
                                    ELSE aml_puu.factor
                                END
                            )
                            ELSE aml.quantity
                        END
                    ) FILTER(
                        WHERE
                            aml.product_id = sol.product_id
                    ) AS total_sold
                FROM
                    sale_order_line sol
                    INNER JOIN sale_order so ON (sol.order_id = so.id)
                    INNER JOIN product_product pp ON (sol.product_id = pp.id)
                    INNER JOIN product_template pt ON (pp.product_tmpl_id = pt.id)
                    INNER JOIN sale_order_line_invoice_rel solir ON (solir.order_line_id = sol.id)
                    INNER JOIN account_move_line aml ON (aml.id = solir.invoice_line_id)
                    INNER JOIN account_move am ON (am.id = aml.move_id)
                    INNER JOIN product_product aml_pp ON (aml_pp.id = aml.product_id)
                    INNER JOIN product_template aml_pt ON (
                        aml_pt.id = aml_pp.product_tmpl_id
                    )
                    LEFT OUTER JOIN uom_uom aml_uu ON (aml_uu.id = aml.product_uom_id)
                    LEFT OUTER JOIN uom_uom aml_puu ON (aml_puu.id = aml_pt.uom_id)
                    LEFT OUTER JOIN commission_for_group cfg ON (
                        cfg.group_id = pp.commission_group_id
                    )
                    LEFT OUTER JOIN order_totals ot ON (
                        ot.branch_id = so.branch_id
                        AND ot."date" = DATE(so.date_order)
                        AND ot.team_id = so.team_id
                    )
                WHERE
                    so.state = 'done'
                    AND sol.order_id IS NOT NULL
                    AND am.state = 'posted'
                    AND am.move_type = 'out_invoice'
                    AND aml.product_id IS NOT NULL
                    AND aml.quantity > 0.0
                    AND (
                        EXISTS(
                            SELECT 1
                            FROM
                                commission_for_sale cfs
                            WHERE
                                cfs.product_id = sol.product_id
                        )
                        OR EXISTS(
                            SELECT 1
                            FROM
                                commission_for_group cfg
                            WHERE
                                cfg.group_id = pp.commission_group_id
                        )
                    )
                GROUP BY
                    so.branch_id,
                    DATE(so.date_order),
                    so.team_id,
                    pp.commission_group_id,
                    cfg.categ_id,
                    pt.categ_id,
                    sol.product_id
                ORDER BY
                    so.branch_id,
                    DATE(so.date_order),
                    so.team_id,
                    pp.commission_group_id,
                    cfg.categ_id,
                    pt.categ_id,
                    sol.product_id
            )
        SELECT
            ROW_NUMBER() OVER () AS id,
            sol1.*,
            CASE
                WHEN sol1.commission_group_id IS NULL THEN AVG( (
                        SELECT
                            CASE cfs.forma_de_calculo
                                WHEN 'fijo' THEN cfs.basic_bonus
                                WHEN 'regla_de_tres' THEN sol1.total_sold * cfs.basic_bonus / cfs.base_min_qty
                            END
                        FROM
                            commission_for_sale cfs
                        WHERE
                            cfs.product_id = sol1.product_id
                            AND sol1.total_sold >= cfs.base_min_qty
                        ORDER BY
                            cfs.base_min_qty DESC
                        LIMIT
                            1
                    )
                ) FILTER(
                    WHERE
                        sol1.commission_group_id IS NULL
                ) OVER (
                    PARTITION BY sol1.branch_id,
                    DATE_TRUNC('month', sol1."date"),
                    sol1.team_id,
                    sol1.product_id
                )
                ELSE AVG( (
                        SELECT
                            CASE cfg.forma_de_calculo
                                WHEN 'fijo' THEN cfg.basic_bonus
                                WHEN 'regla_de_tres' THEN sol1.total_sold * cfg.basic_bonus / cfg.base_min_qty
                            END
                        FROM
                            commission_for_group cfg
                        WHERE
                            cfg.group_id = sol1.commission_group_id
                            AND sol1.total_sold >= cfg.base_min_qty
                        ORDER BY
                            cfg.base_min_qty DESC
                        LIMIT
                            1
                    )
                ) FILTER(
                    WHERE
                        sol1.commission_group_id IS NOT NULL
                ) OVER (
                    PARTITION BY sol1.branch_id,
                    DATE_TRUNC('month', sol1."date"),
                    sol1.team_id,
                    sol1.commission_group_id
                )
            END AS total_amount_commissions
        FROM sol1
        WHERE sol1.total_sold > 0.0
    """

    branch_id = fields.Many2one(
        "res.branch",
        string="Sucursal",
        readonly=True
    )
    categ_id = fields.Many2one(
        "product.category",
        string="Categoría",
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
    amount_sale = fields.Float(
        string="Monto de venta",
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
