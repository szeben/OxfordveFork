# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_shipped = fields.Boolean(store=True)


    

