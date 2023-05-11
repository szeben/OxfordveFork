# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'account.payment'

    is_payment_validated = fields.Boolean(
        string='Pago validado',
        help = 'Establece si el pago ha sido validado.',
        tracking = 10,
        default=False
    )