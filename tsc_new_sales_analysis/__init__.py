# -*- coding: utf-8 -*-
# from odoo import api, SUPERUSER_ID

from . import controllers
from . import models


# def _tsc_remove_module_groups(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})

#     group_report_oxford_sales = env.ref(
#         'tsc_new_sales_analysis.tsc_restrict_report_oxford_sales_analysis', raise_if_not_found=False)

#     if group_report_oxford_sales:

#         for record in group_report_oxford_sales.model_access:
#             record.unlink()

#         group_report_oxford_sales.unlink()
