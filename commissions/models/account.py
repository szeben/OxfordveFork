# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    collection_id = fields.Many2one('configuration.collection', string="Cobranza")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    commission_id = fields.Many2one(
        'commission.for.sale',
        string="Comisión"
    )
    team_id = fields.Many2one(
        related='partner_id.team_id',
        string="Equipo de ventas",
        readonly=True,
        store=True
    )
    collection_id = fields.Many2one(
        related='account_id.collection_id',
        string="Cobranza",
        readonly=True,
        store=True
    )
    commission_by_collection = fields.Float(
        compute="_compute_commission_by_collection",
        string="Comisión por cobranza",
        store=True
    )

    @api.depends(
        "parent_state",
        "date",
        "collection_id",
        "collection_id.percentage",
        "debit",
        "payment_id",
        "move_id"
    )
    def _compute_commission_by_collection(self):
        for line in self:
            if (
                line.parent_state == 'posted'
                and line.date
                and line.collection_id != False
                and line.debit != 0
                and line.partner_id != False
            ):
                line.commission_by_collection = line.debit * line.collection_id.percentage
            else:
                line.commission_by_collection = 0
