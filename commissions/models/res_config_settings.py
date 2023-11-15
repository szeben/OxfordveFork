# -*- coding: utf-8 -*-

import pytz
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commissions_tz = fields.Selection(
        selection=lambda self: [
            (tz, tz) for tz in sorted(
                pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_'
            )
        ],
        string="Zona horaria de comisiones",
        config_parameter='commissions.tz'
    )
