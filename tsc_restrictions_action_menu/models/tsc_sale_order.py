# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def copy(self, default=None):
        res = super().copy(default)

        body = _('Sales order created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>') % (self.id, self.name)
        res.message_post(body=body)

        return res