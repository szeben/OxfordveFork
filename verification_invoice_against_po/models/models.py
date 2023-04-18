# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VerificationInvoiceAgainstPo(models.Model):

    _inherit = "account.move"

    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        for record in self:
            if record.move_type == 'in_invoice':
                return True

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self.env['account.move.line'].flush(
            self.env['account.move.line']._fields)
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        if query_res:
            ids = [res[0] for res in query_res]
            sums = [res[1] for res in query_res]
            raise UserError(
                _("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))

    def validar_cantidades(self):

        for record in self:

            account_move_id = int(record.id)

            account_obj = self.env['account.move'].search(
                [('id', '=', account_move_id)]).with_context(check_move_validity=False)

            for invoice_line_id in account_obj.invoice_line_ids:

                if (invoice_line_id.quantity != invoice_line_id.purchase_line_id.qty_received):

                    body = ('Journal Item %s, Quantity: %s has been update to %s') % (invoice_line_id.id,
                                                                                      invoice_line_id.quantity, invoice_line_id.purchase_line_id.qty_received)

                    invoice_line_id.quantity = invoice_line_id.purchase_line_id.qty_received

                    self.message_post(body=body)

        self.message_post(body="Validación de cantidades realizada")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'info',
                'sticky': False,
                'message': "Validación de cantidades realizada, puede confirmar la factura",
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class TrackingAndChatterAccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    quantity = fields.Float(tracking=True)

    # @api.onchange('quantity')
    # def _onchange_quantity(self):

    #     body = f"Hola probando quantity = {self.quantity}"
    #     self._origin.move_id.message_post(body=body)
