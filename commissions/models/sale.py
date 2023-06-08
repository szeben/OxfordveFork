
# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    team_id = fields.Many2one(
        related='order_id.partner_id.team_id',
        string="Equipo de ventas",
        store=True,
        domain=[('order_id', '!=', False)]
    )
