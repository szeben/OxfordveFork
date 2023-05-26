# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class TeamSaleReport(models.Model):
    _name = "team.sale.report"
    _description = "Reporte de comisiones asignadas"
    _auto = False

    _table_query = """
        WITH commission_by_sale AS (
            SELECT
                date,
                team_id,
                SUM(total_vendidos) AS total_vendidos,
                SUM(total_amount_sales) AS total_amount_sales,
                SUM(total_amount_commissions) AS total_amount_commissions,
                0.0 AS commission_by_collection,
                0.0 AS debit
            FROM sale_order_line sol
            WHERE
                sol.order_id IS NOT NULL
                AND sol.order_partner_id IS NOT NULL
            GROUP BY
                date,
                team_id
            ORDER BY
                date
        ),
        commission_by_collection AS (
            SELECT
                aml.date,
                aml.team_id,
                0.0 AS total_vendidos,
                0.0 AS total_amount_sales,
                0.0 AS total_amount_commissions,
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
            GROUP BY
                aml.date,
                aml.team_id
            ORDER BY date
        )
        SELECT
            ROW_NUMBER() OVER () AS id,
            ucommisions.date,
            ucommisions.team_id,             
            SUM(total_vendidos) AS total_vendidos,
            SUM(total_amount_sales) AS total_amount_sales,
            SUM(total_amount_commissions) AS total_amount_commissions,
            SUM(commission_by_collection) AS commission_by_collection,
            SUM(debit) AS debit,
            SUM(COALESCE(total_amount_commissions, 0) + COALESCE(commission_by_collection, 0)) AS total_commissions
        FROM (
                SELECT *
                FROM
                    commission_by_sale
                UNION ALL
                SELECT *
                FROM
                    commission_by_collection
            ) AS ucommisions
        WHERE
            ucommisions.date IS NOT NULL
        GROUP BY
            ucommisions.team_id,
            ucommisions.date
        ORDER BY
            ucommisions.team_id,
            ucommisions.date
    """

    date = fields.Datetime(
        string="Fecha",
        readonly=True
    )

    team_id = fields.Many2one(
        'crm.team',
        string="Equipo de ventas", readonly=True
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
