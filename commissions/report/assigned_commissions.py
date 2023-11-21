# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CommissionAssignmentReport(models.Model):
    _name = "commission.assignment.report"
    _description = "Reporte de comisiones asignadas"
    _auto = False

    @property
    def _table_query(self):
        Report = self.env["commissions.sales.report.mixin"]

        extra = (
            (
                "summary_collection",
                """
                SELECT
                    aml.branch_id,
                    aml.team_id,
                    DATE(DATE_TRUNC('month', aml.date)) AS "date",
                    SUM(aml.commission_by_collection) AS commission_by_collection,
                    SUM(aml.debit) AS debit
                FROM
                    account_move_line aml
                    LEFT JOIN account_account aa ON (aml.account_id = aa.id)
                WHERE
                    aml.parent_state = 'posted'
                    AND aa.collection_id IS NOT NULL
                    AND aml.debit != 0
                    AND aml.partner_id IS NOT NULL
                    AND aml.date IS NOT NULL
                GROUP BY
                    aml.branch_id,
                    aml.team_id,
                    DATE(DATE_TRUNC('month', aml."date"))
                """
            ),
            (
                "commission_group",
                Report._generate_commission_query(
                    "commission_for_group",
                    "summary_group",
                    "group_id",
                    False
                )
            ),
            (
                "commission_product",
                Report._generate_commission_query(
                    "commission_for_sale",
                    "summary_product",
                    "product_id",
                    False
                )
            ),
            (
                "commission_category",
                Report._generate_commission_query(
                    "commission_for_category",
                    "summary_category",
                    "categ_id",
                    False
                )
            ),
            (
                "ucommissions",
                """
                SELECT
                    sc.branch_id,
                    sc.team_id,
                    sc."date",
                    0.0 AS amount_sale,
                    0.0 AS total_sold,
                    0.0 AS commission,
                    sc.commission_by_collection AS commission_by_collection,
                    sc.debit AS debit
                FROM
                    summary_collection sc
                UNION ALL
                SELECT
                    cg.branch_id,
                    cg.team_id,
                    cg."date",
                    cg.amount_sale,
                    cg.total_sold,
                    cg.amount_commissions AS commission,
                    0.0 AS commission_by_collection,
                    0.0 AS debit
                FROM
                    commission_group cg
                UNION ALL
                SELECT
                    cp.branch_id,
                    cp.team_id,
                    cp."date",
                    cp.amount_sale,
                    cp.total_sold,
                    cp.amount_commissions AS commission,
                    0.0 AS commission_by_collection,
                    0.0 AS debit
                FROM
                    commission_product cp
                UNION ALL
                SELECT
                    cc.branch_id,
                    cc.team_id,
                    cc."date",
                    0.0 AS amount_sale,
                    0.0 AS total_sold,
                    cc.amount_commissions AS commission,
                    0.0 AS commission_by_collection,
                    0.0 AS debit
                FROM
                    commission_category cc
                """,
            ),
        )

        return Report._get_with_query(
            "sol", "summary_product", "summary_group", "summary_category"
        ).rstrip() + ", " + ", ".join(
            f"{key} AS ({query})"
            for key, query in extra
        )  + """
            SELECT
                ROW_NUMBER() OVER () AS "id",
                uc.branch_id,
                uc.team_id,
                uc.date,
                SUM(uc.total_sold) AS total_vendidos,
                SUM(uc.amount_sale) AS total_amount_sales,
                SUM(uc.commission) AS amount_commissions,
                SUM(uc.commission_by_collection) AS commission_by_collection,
                SUM(uc.debit) AS debit,
                SUM(uc.commission + uc.commission_by_collection) AS total_commissions
            FROM ucommissions uc
            WHERE uc.date IS NOT NULL
            GROUP BY
                uc.team_id,
                uc.branch_id,
                uc.date
            ORDER BY
                uc.team_id,
                uc.branch_id,
                uc.date
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
    amount_commissions = fields.Float(
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
