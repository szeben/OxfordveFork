# -*- coding: utf-8 -*-
from itertools import chain

from odoo import api, fields, models

CALIFICACION_CHOICES = [
    ('0', 'Normal'),
    ('1', 'Bajo'),
    ('2', 'Alto'),
    ('3', 'Muy alto'),
]

CLASIFICACION_CHOICES = [
    ('Mayorista', 'Mayorista'),
    ('Integrador', 'Integrador'),
    ('Usuario final', 'Usuario final'),
    ('Direccion', 'Dirección'),
]

class AccountMove(models.Model):
    _inherit = 'account.move'

    date_first_payment = fields.Date(
        string="Fecha del primer pago",
        compute="_compute_date_first_payment",
        store=True
    )

    def _compute_date_first_payment(self):
        for move in self:
            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                pay_term_lines = move.line_ids.filtered(
                    lambda line: line.account_internal_type in (
                        'receivable', 'payable')
                )
                date = next(chain(
                    map(lambda m: m.debit_move_id.date,
                        pay_term_lines.matched_debit_ids),
                    map(lambda m: m.credit_move_id.date,
                        pay_term_lines.matched_credit_ids)
                ), None)

                if date:
                    move.date_first_payment = date
                    continue

            move.date_first_payment = False


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    marca = fields.Char("Marca", readonly=True)
    barcode = fields.Char("Código de barra", readonly=True)
    reference = fields.Char("Referencia interna", readonly=True)
    date_first_payment = fields.Date("Fecha del primer pago", readonly=True)
    x_studio_clasificacion = fields.Selection([
        ('Mayorista', 'Mayorista'),
        ('Integrador', 'Integrador'),
        ('Usuario final', 'Usuario final'),
        ('Direccion', 'Dirección')],
        string="Clasificacion")
    x_studio_calificacion_1 = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Bajo'),
        ('2', 'Alto'),
        ('3', 'Muy alto')],
        string="Calificacion")

    @api.model
    def _select(self):
        return '''
            SELECT

                line.id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.analytic_account_id,
                line.journal_id,
                line.company_id,
                line.company_currency_id,
                line.partner_id AS commercial_partner_id,
                move.state,
                move.move_type,
                move.partner_id,
                move.invoice_user_id,
                move.fiscal_position_id,
                move.invoice_date,
                move.invoice_date_due,
                uom_template.id                                             AS product_uom_id,
                template.categ_id                                           AS product_categ_id,
                line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                                                                            AS quantity,
                -line.balance * currency_table.rate                         AS price_subtotal,
                -COALESCE(
                   -- Average line price
                   (line.balance / NULLIF(line.quantity, 0.0)) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                   -- convert to template uom
                   * (NULLIF(COALESCE(uom_line.factor, 1), 0.0) / NULLIF(COALESCE(uom_template.factor, 1), 0.0)),
                   0.0) * currency_table.rate                               AS price_average,
                COALESCE(partner.country_id, commercial_partner.country_id) AS country_id,

                template.x_studio_marca          AS marca,
                product.default_code             AS reference,
                product.barcode                  AS barcode,
                move.date_first_payment          AS date_first_payment,
                partner.x_studio_clasificacion   AS x_studio_clasificacion,
                partner.x_studio_calificacion_1  AS x_studio_calificacion_1

        '''
