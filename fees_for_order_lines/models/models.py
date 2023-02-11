# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        default=lambda self: self.order_id.pricelist_id,
        store=True,
        check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )


    def get_price_inline(self):
        self.ensure_one()

        if self.pricelist_id:
            quantity = self.product_uom_qty or 1.0
            return self.pricelist_id.get_products_price(
                [self.product_id],
                [quantity],
                [self.order_id.partner_id]
            )

        return {}

    @api.onchange('product_id')
    def _onchange_pricelist_from_order(self):
        for line in self:
            line.pricelist_id = line.order_id.pricelist_id

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        self.ensure_one()
        for line in self:
            if not (not line.display_type and line.order_id):
                continue

            order_id = line.order_id

            product = line.product_id.with_context(
                partner=order_id.partner_id,
                quantity=line.product_uom_qty,
                date=order_id.date_order,
                pricelist=line.pricelist_id.id,
                uom=line.product_uom.id
            )

            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product),
                line.product_id.taxes_id,
                line.tax_id,
                line.company_id
            )

            if line.pricelist_id.discount_policy == 'without_discount' and price_unit:
                price_discount_unrounded = line.pricelist_id.get_product_price(
                    product,
                    line.product_uom_qty,
                    order_id.partner_id,
                    order_id.date_order,
                    line.product_uom.id
                )
                discount = max(0, (price_unit - price_discount_unrounded) * 100 / price_unit)
            else:
                discount = 0
            line.update({'price_unit': price_unit, 'discount': discount})
            # self.order_id.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", line.pricelist_id.display_name))
            # line.order_id.message_post(body="Hello, good morning all", subject="Today in this video")        

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        self.ensure_one()

        for line in self:
            if line.pricelist_id:
                order_id = line.order_id
                # product = line.product_id
                no_variant_attributes_price_extra = [
                    ptav.price_extra for ptav in line.product_no_variant_attribute_value_ids.filtered(
                        lambda ptav:
                            ptav.price_extra and
                            ptav not in product.product_template_attribute_value_ids
                    )
                ]

                if no_variant_attributes_price_extra:
                    product = product.with_context(
                        no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                    )

                if line.pricelist_id.discount_policy == 'with_discount':
                    return product.with_context(
                        pricelist=line.pricelist_id.id,
                        uom=line.product_uom.id
                    ).price

                product_context = dict(
                    self.env.context,
                    partner_id=order_id.partner_id.id,
                    date=order_id.date_order,
                    uom=line.product_uom.id
                )

                final_price, rule_id = line.pricelist_id.with_context(product_context).get_product_price_rule(
                    product or self.product_id,
                    line.product_uom_qty or 1.0,
                    order_id.partner_id
                )

                base_price, currency = line.with_context(product_context)._get_real_price_currency(
                    product,
                    rule_id,
                    line.product_uom_qty,
                    line.product_uom,
                    line.pricelist_id.id
                )

                if currency != line.pricelist_id.currency_id:
                    base_price = currency._convert(
                        base_price,
                        line.pricelist_id.currency_id,
                        order_id.company_id or line.env.company,
                        order_id.date_order or fields.Date.today()
                    )

                return max(base_price, final_price)

            # negative discounts (= surcharge) are included in the display price

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['name', 'price_unit',
                           'pricelist_id', 'product_uom', 'tax_id']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(
                        line[field], line)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, pricelist_id=False,
                              product_uom_qty=0, product_uom=False, customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))

        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.order_id.state == 'sale':
                msg = _("Extra line with %s", line.product_id.display_name)
                line.order_id.message_post(body=msg)
                # create an analytic account if at least an expense product
                if line.product_id.expense_policy not in [False, 'no'] and not line.order_id.analytic_account_id:
                    line.order_id._create_analytic_account()
        return lines


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    requires_approval = fields.Boolean(
        string='Requiere Aprobación',
        default=False
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def update_prices(self):
        self.ensure_one()
        lines_to_update = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            line.pricelist_id = line.order_id.pricelist_id
            product = line.product_id.with_context(
                partner=self.partner_id,
                quantity=line.product_uom_qty,
                date=self.date_order,
                pricelist=line.pricelist_id.id,
                uom=line.product_uom.id
            )
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product), line.product_id.taxes_id, line.tax_id, line.company_id)
            if line.pricelist_id.discount_policy == 'without_discount' and price_unit:
                price_discount_unrounded = line.pricelist_id.get_product_price(
                    product, line.product_uom_qty, self.partner_id, self.date_order, line.product_uom.id)
                discount = max(0, (price_unit - price_discount_unrounded) * 100 / price_unit)
            else:
                discount = 0
            lines_to_update.append((1, line.id, {'price_unit': price_unit, 'discount': discount}))
        self.update({'order_line': lines_to_update})
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", line.pricelist_id.display_name))

    def _action_confirm(self):
        """
            Inherited method to add validation if user has no permissions to confirm
            a sale order if some of the products has a pricelist with requires_approval = True
        """
        for ol in self.order_line:
            if ol.pricelist_id:
                if ol.pricelist_id.id != 1 and ol.pricelist_id.requires_approval == True and not self.env.user.has_group('__export__.res_groups_72_45e737e5'):
                    raise UserError(_('No tiene permitido confirmar la orden de venta ya que hay uno o más productos que poseen una Tarifa Unitaria que requiere aprobación\n\n'
                                    'Por favor comuníquese con su supervisor'))
        """ Implementation of additionnal mecanism of Sales Order confirmation.
            This method should be extended when the confirmation should generated
            other documents. In this method, the SO are in 'sale' state (not yet 'done').
        """
        # create an analytic account if at least an expense product
        for order in self:
            if any(expense_policy not in [False, 'no'] for expense_policy in order.order_line.mapped('product_id.expense_policy')):
                if not order.analytic_account_id:
                    order._create_analytic_account()

        return True
    
    def write(self, values):
        if values.get('order_line') and self.state == 'sale':
            for order in self:
                pre_order_line_qty = {order_line: order_line.product_uom_qty for order_line in order.mapped('order_line') if not order_line.is_expense}
                

        if values.get('partner_shipping_id'):
            new_partner = self.env['res.partner'].browse(values.get('partner_shipping_id'))
            for record in self:
                picking = record.mapped('picking_ids').filtered(lambda x: x.state not in ('done', 'cancel'))
                addresses = (record.partner_shipping_id.display_name, new_partner.display_name)
                message = _("""The delivery address has been changed on the Sales Order<br/>
                        From <strong>"%s"</strong> To <strong>"%s"</strong>,
                        You should probably update the partner on this document.""") % addresses
                picking.activity_schedule('mail.mail_activity_data_warning', note=message, user_id=self.env.user.id)

        if values.get('commitment_date'):
            # protagate commitment_date as the deadline of the related stock move.
            # TODO: Log a note on each down document
            self.order_line.move_ids.date_deadline = fields.Datetime.to_datetime(values.get('commitment_date'))
        

        if values.get('order_line'):
            dc_id, tf_na, tf_ol, prod, mss = [], [], [] ,[], []
            for s in values.get('order_line'):
                if s[-1] != False and s[-1].get('pricelist_id') and isinstance(s[1], int):
                    tf_na.append(' '.join([str(elem) for elem in (((self.env['product.pricelist'].search([('id', '=', (s[-1].get('pricelist_id')))])).mapped('name')))]))
                    dc_id.append(s[1])

            for order in self:
                for order_line in order.mapped('order_line'):
                    if order_line.id in dc_id:
                        tf_ol.append(order_line.pricelist_id.name)
                        prod.append(order_line.product_id.name)
            print(dc_id, tf_na, tf_ol, prod)
            if tf_ol and prod:
                for index in range(len(tf_na)):
                    if tf_ol[index] == False:
                        message = f'El producto: <strong>{prod[index]}</strong> le fue asignado la tarifa: <strong>{tf_na[index]}</strong>.<br/>'
                    else:
                        message = f'La tarifa <strong>{tf_ol[index]}</strong> fue cambiada por <strong>{tf_na[index]}</strong> en el producto: <strong>{prod[index]}</strong>.<br/>'
                    mss.append(message)

                self.message_post(body=(' '.join([str(elem) for elem in mss])))

        res = super(SaleOrder, self).write(values)
        if values.get('order_line') and self.state == 'sale':
            for order in self:
                to_log = {}
                for order_line in order.order_line:
                    if float_compare(order_line.product_uom_qty, pre_order_line_qty.get(order_line, 0.0), order_line.product_uom.rounding) < 0:
                        to_log[order_line] = (order_line.product_uom_qty, pre_order_line_qty.get(order_line, 0.0))
                if to_log:
                    documents = self.env['stock.picking']._log_activity_get_documents(to_log, 'move_ids', 'UP')
                    documents = {k:v for k, v in documents.items() if k[0].state != 'cancel'}
                    order._log_decrease_ordered_quantity(documents)

        return res
