# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    collection_id = fields.Many2one('configuration.collection', string="Cobranza")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    team_id = fields.Many2one(
        related='partner_id.team_id',
        string="Equipo de ventas",
        store=True
    )
    collection_id = fields.Many2one(
        related='account_id.collection_id',
        string="Cobranza",
        store=True
    )
    commission_by_collection = fields.Float(
        compute="_compute_commission_by_collection",
        string="Comisión por cobranza",
        store=True
    )
    quantity_product_uom = fields.Float(
        string="Cantidad en unidad de medida del producto",
        compute="_compute_quantity_product_uom",
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
                and line.collection_id != False
                and line.date
                and line.debit != 0
                and line.partner_id != False
            ):
                line.commission_by_collection = line.debit * line.collection_id.percentage
            else:
                line.commission_by_collection = 0

    @api.depends("quantity", "product_uom_id", "product_id", "product_id.uom_id")
    def _compute_quantity_product_uom(self):
        for line in self:
            quantity = 0.0

            if line.product_uom_id and line.quantity:
                quantity = line.product_uom_id._compute_quantity(
                    line.quantity,
                    line.product_id.uom_id,
                    round=False
                )

            line.quantity_product_uom = quantity
