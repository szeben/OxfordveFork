# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    commission_id = fields.Many2one('commission.for.sale', string="Comisión")
