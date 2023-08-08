# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def copy(self, default=None):
        res = super().copy(default)

        body = _('Purchase order created from: <a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a>') % (self.id, self.name)
        res.message_post(body=body)

        return res