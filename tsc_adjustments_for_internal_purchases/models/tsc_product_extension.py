# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError

class tsc_ProductTemplate(models.Model):

    _inherit = 'product.template'

    def tsc_in_internal_group(self):
        return self.env.user.has_group('tsc_adjustments_for_internal_purchases.tsc_internal_purchases_group')

    def tsc_in_merchandise_group(self):
        return self.env.user.has_group('tsc_adjustments_for_internal_purchases.tsc_merchandise_purchase_group')
    
    #@tools.ormcache()
    def _get_default_category_id(self):
        tsc_user_in_internal_group = self.tsc_in_internal_group()
        tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()
        if (tsc_user_in_internal_group and not tsc_user_in_merchandise_group) or (not tsc_user_in_internal_group and tsc_user_in_merchandise_group):
            tsc_value = True if tsc_user_in_internal_group and not tsc_user_in_merchandise_group else False
            tsc_find_category = self.env['product.category'].search([('tsc_internal_purpose_category', '=', tsc_value)])
            return tsc_find_category[:1]
        return self.env.ref('product.product_category_all')

    @api.model
    def tsc_get_categories(self):
        tsc_user_in_internal_group = self.tsc_in_internal_group()
        tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()
        if (tsc_user_in_internal_group and not tsc_user_in_merchandise_group) or \
        (not tsc_user_in_internal_group and tsc_user_in_merchandise_group):
            tsc_value = True if (tsc_user_in_internal_group and not tsc_user_in_merchandise_group) else False
            return [('tsc_internal_purpose_category', '=', tsc_value)]
        return []
        
    
    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, domain=tsc_get_categories, default=_get_default_category_id, group_expand='_read_group_categ_id', required=True, help="Select category for the current product")

    def tsc_check_category(self, tsc_product_category):
        tsc_user_in_internal_group = self.tsc_in_internal_group()
        tsc_user_in_merchandise_group = self.tsc_in_merchandise_group()

        if tsc_product_category.tsc_internal_purpose_category and not tsc_user_in_internal_group:
            raise UserError(_("You are not currently allowed to create products under the selected category. Merchandise purchase or internal purchase permissions are needed."))
            
    @api.model
    def create(self, vals):
        if vals.get('categ_id'):
            tsc_product_category = self.env['product.category'].browse(vals.get('categ_id'))
            self.tsc_check_category(tsc_product_category)
        return super(tsc_ProductTemplate, self).create(vals)

    def write(self, vals):
        for tsc_category in self:
            tsc_category_categ = tsc_category.categ_id
            if vals.get('categ_id'):
                tsc_id = vals.get('categ_id')
                tsc_category_categ = self.env['product.category'].browse(tsc_id)
            self.tsc_check_category(tsc_category_categ)
        return super(tsc_ProductTemplate, self).write(vals)


class tsc_ProductCategory(models.Model):

    _inherit = 'product.category'

    tsc_internal_purpose_category = fields.Boolean(string="Is it for internal use?",
                                                   help="Mark as checked if the category will contain products of internal use. In other words, products not available for sale.",
                                                   default=False)
    
