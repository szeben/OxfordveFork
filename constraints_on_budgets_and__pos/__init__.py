# -*- coding: utf-8 -*-

from . import controllers
from . import models

# from odoo import api, SUPERUSER_ID


def constraints_on_budget_and_pos_uninstall_hook(cr, registry):
    # env = api.Environment(cr, SUPERUSER_ID, {})

    cr.execute("""UPDATE ir_model_access
               SET
               perm_create=TRUE,
               perm_read=TRUE,
               perm_unlink=TRUE,
               perm_write=TRUE
               WHERE group_id IN(
                   SELECT
                   DISTINCT ima.group_id
                   FROM
                   ir_model_access ima
                   INNER JOIN res_groups rg ON(ima.group_id=rg.id)
                   INNER JOIN ir_module_category imc ON(rg.category_id=imc.id)
                   WHERE
                   imc.name='Purchase'
                   AND rg.name IN('User', 'Administrator')
               )
               AND name='purchase.order'
        """)
    cr.commit()
