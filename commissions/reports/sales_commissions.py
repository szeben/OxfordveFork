# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionSalesCommissionReport(models.Model):
    _name = "commissions.sales.report"
    _description = "Reporte de comisiones de ventas"
    _auto = False
    _table_query = """
        SELECT
            ROW_NUMBER() OVER () AS id,
            commissions.*
        FROM ( (
                    SELECT sol2.*, (
                            SELECT
                                CASE cfs.commission_type
                                    WHEN 'fija' THEN CASE cfs.forma_de_calculo
                                        WHEN 'fijo' THEN cfs.bono_base
                                        WHEN 'regla_de_tres' THEN sol2.total_sold * cfs.bono_base / cfs.cant_minima_base
                                    END
                                    WHEN 'basada_en_otra_comision' THEN CASE cfs.forma_de_calculo
                                        WHEN 'fijo' THEN cfs.bono_base_otra_com
                                        WHEN 'regla_de_tres' THEN sol2.total_sold * cfs.bono_base_otra_com / cfs.cant_min_base_otra_com
                                    END
                                END
                            FROM
                                commission_for_sale cfs
                            WHERE
                                cfs.product_id = sol2.product_id
                                AND ( (
                                        cfs.commission_type = 'fija'
                                        AND sol2.total_sold >= cfs.cant_minima_base
                                    )
                                    OR (
                                        cfs.commission_type = 'basada_en_otra_comision'
                                        AND sol2.total_sold >= cfs.cant_min_base_otra_com
                                    )
                                )
                            ORDER BY
                                CASE cfs.commission_type
                                    WHEN 'fija' THEN cfs.cant_minima_base
                                    WHEN 'basada_en_otra_comision' THEN cfs.cant_min_base_otra_com
                                END DESC
                            LIMIT
                                1
                        ) AS total_amount_commissions
                    FROM (
                            SELECT
                                sol1.*,
                                SUM(sol1.quantity) FILTER (
                                    WHERE
                                        sol1.quantity > 0.0
                                ) OVER (
                                    PARTITION BY sol1.branch_id,
                                    sol1.product_id,
                                    sol1.team_id,
                                    DATE_TRUNC('month', sol1."date")
                                ) AS total_sold
                            FROM (
                                    SELECT
                                        so.branch_id AS branch_id,
                                        pt.categ_id AS categ_id,
                                        so.team_id AS team_id,
                                        DATE(so.date_order) AS "date",
                                        sol.product_id AS product_id,
                                        NULL :: INTEGER AS commission_group_id,
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
                                        ) AS quantity,
                                        SUM(so.amount_total) AS amount_sale
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
                                    WHERE
                                        sol.quantity IS NOT NULL
                                        AND so.state = 'done'
                                        AND sol.order_id IS NOT NULL
                                        AND am.state = 'posted'
                                        AND am.move_type = 'out_invoice'
                                        AND aml.product_id IS NOT NULL
                                        AND aml.quantity > 0.0
                                        AND pp.commission_group_id IS NULL
                                        AND EXISTS(
                                            SELECT
                                                *
                                            FROM
                                                commission_for_sale cfs
                                            WHERE
                                                cfs.product_id = sol.product_id
                                        )
                                    GROUP BY
                                        so.branch_id,
                                        DATE(so.date_order),
                                        pt.categ_id,
                                        sol.product_id,
                                        so.team_id
                                    ORDER BY
                                        so.branch_id,
                                        DATE(so.date_order),
                                        pt.categ_id,
                                        sol.product_id,
                                        so.team_id
                                ) sol1
                        ) sol2
                )
                UNION ALL (
                    SELECT sol2.*, (
                            SELECT
                                CASE cfg.commission_type
                                    WHEN 'fija' THEN CASE cfg.forma_de_calculo
                                        WHEN 'fijo' THEN cfg.bono_base
                                        WHEN 'regla_de_tres' THEN sol2.total_sold * cfg.bono_base / cfg.cant_minima_base
                                    END
                                    WHEN 'basada_en_otra_comision' THEN CASE cfg.forma_de_calculo
                                        WHEN 'fijo' THEN cfg.bono_base_otra_com
                                        WHEN 'regla_de_tres' THEN sol2.total_sold * cfg.bono_base_otra_com / cfg.cant_min_base_otra_com
                                    END
                                END
                            FROM
                                commission_for_group cfg
                            WHERE
                                cfg.group_id = sol2.commission_group_id
                                AND ( (
                                        cfg.commission_type = 'fija'
                                        AND sol2.total_sold >= cfg.cant_minima_base
                                    )
                                    OR (
                                        cfg.commission_type = 'basada_en_otra_comision'
                                        AND sol2.total_sold >= cfg.cant_min_base_otra_com
                                    )
                                )
                            ORDER BY
                                CASE cfg.commission_type
                                    WHEN 'fija' THEN cfg.cant_minima_base
                                    WHEN 'basada_en_otra_comision' THEN cfg.cant_min_base_otra_com
                                END DESC
                            LIMIT
                                1
                        ) AS total_amount_commissions
                    FROM (
                            SELECT
                                sol1.*,
                                SUM(sol1.quantity) FILTER (
                                    WHERE
                                        sol1.quantity > 0.0
                                ) OVER (
                                    PARTITION BY sol1.branch_id,
                                    sol1.commission_group_id,
                                    sol1.team_id,
                                    DATE_TRUNC('month', sol1."date")
                                ) AS total_sold
                            FROM (
                                    SELECT
                                        so.branch_id AS branch_id,
                                        MIN(pt.categ_id) AS categ_id,
                                        so.team_id AS team_id,
                                        DATE(so.date_order) AS "date",
                                        NULL :: INTEGER AS product_id,
                                        pp.commission_group_id AS commission_group_id,
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
                                        ) AS quantity,
                                        SUM(so.amount_total) AS amount_sale
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
                                    WHERE
                                        sol.quantity IS NOT NULL
                                        AND so.state = 'done'
                                        AND sol.order_id IS NOT NULL
                                        AND am.state = 'posted'
                                        AND am.move_type = 'out_invoice'
                                        AND aml.product_id IS NOT NULL
                                        AND aml.quantity > 0.0
                                        AND pp.commission_group_id IS NOT NULL
                                    GROUP BY
                                        so.branch_id,
                                        DATE(so.date_order),
                                        pp.commission_group_id,
                                        so.team_id
                                    ORDER BY
                                        so.branch_id,
                                        DATE(so.date_order),
                                        pp.commission_group_id,
                                        so.team_id
                                ) sol1
                        ) sol2
                )
            ) commissions 
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
    quantity = fields.Float(
        string="Cantidad",
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
