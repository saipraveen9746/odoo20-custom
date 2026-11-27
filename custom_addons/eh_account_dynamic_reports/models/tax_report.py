# -*- encoding: utf-8 -*-
##############################################################################
#
# ERP Heritage
# Copyright (C) 2026 (https://www.erpheritage.com.au/)
#
##############################################################################
"""
Tax Report (VAT Return - SA / GCC) handler for Dynamic Reports.

Renders the official 13-box VAT Return:
VAT on Sales:
1. Standard rated sales
2. Private Healthcare / Private Education / First house sales to citizens
3. Zero rated domestic sales
4. Exports
5. Exempt sales
6. Total Sales

VAT on Purchases:
7. Standard rated domestic purchases
8. Imports subject to VAT paid at customs
9. Imports subject to VAT accounted for through reverse charge mechanism
10. Zero rated purchases
11. Exempt purchases
12. Total Purchases

Summary:
13. Total VAT due for current period
"""

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import SQL
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)


class EhTaxReportHandler(models.AbstractModel):
    _name = 'eh.account.dynamic.report.handler.tax_report'
    _inherit = 'eh.account.dynamic.report.handler.sectioned'
    _description = "Tax Report handler"

    REPORT_CODE = 'tax_report'
    REPORT_NAME = _lt("Tax Report")

    @api.model
    def compute(self, options):
        self, options = self._eh_with_ledger_scope(options)
        date_from = self._extract_date(options, 'date_from')
        date_to = self._extract_date(options, 'date_to')
        company_ids = options.get('company_ids') or [self.env.company.id]
        posted_only = bool(options.get('posted_only', True))

        currency = self._eh_monetary_currency(
            options=options, company_ids=company_ids, presentation_converted=True,
        )

        box_data = self._compute_vat_boxes(
            company_ids, date_from, date_to, posted_only, options=options,
        )

        lines = []

        # --- VAT on Sales Section ---
        lines.append({
            'id': 'section-vat_sales-header',
            'name': _("VAT on Sales:"),
            'level': 0,
            'columns': [
                {'expression_label': 'net_amount', 'value': ''},
                {'expression_label': 'tax_amount', 'value': ''},
            ],
            'unfoldable': False,
            'meta': {'kind': 'section_header', 'section_id': 'vat_sales'},
        })

        sales_boxes = [
            ('1', _("1. Standard rated sales"), True),
            ('2', _("2. Private Healthcare / Private Education / First house sales to citizens"), False),
            ('3', _("3. Zero rated domestic sales"), False),
            ('4', _("4. Exports"), False),
            ('5', _("5. Exempt sales"), False),
        ]

        sales_base_sum = 0.0
        sales_vat_sum = 0.0

        for box_no, label, has_vat in sales_boxes:
            b_data = box_data.get(box_no, {'base': 0.0, 'vat': 0.0, 'tax_id': False})
            b_base = self._eh_round_monetary(b_data['base'], currency=currency)
            b_vat = self._eh_round_monetary(b_data['vat'], currency=currency)
            sales_base_sum += b_base
            sales_vat_sum += b_vat

            lines.append({
                'id': "box-%s" % box_no,
                'name': label,
                'level': 1,
                'columns': [
                    {'expression_label': 'net_amount', 'value': b_base},
                    {'expression_label': 'tax_amount', 'value': b_vat if has_vat or b_vat != 0 else ''},
                ],
                'unfoldable': False,
                'meta': {
                    'kind': 'account_total',
                    'section_id': 'vat_sales',
                    'box_no': box_no,
                    'tax_id': b_data.get('tax_id'),
                },
            })

        # Line 6: Total Sales
        lines.append({
            'id': 'box-6',
            'name': _("6. Total Sales"),
            'level': 0,
            'columns': [
                {'expression_label': 'net_amount', 'value': self._eh_round_monetary(sales_base_sum, currency=currency)},
                {'expression_label': 'tax_amount', 'value': self._eh_round_monetary(sales_vat_sum, currency=currency)},
            ],
            'unfoldable': False,
            'meta': {'kind': 'section_total', 'section_id': 'vat_sales'},
        })

        # --- VAT on Purchases Section ---
        lines.append({
            'id': 'section-vat_purchases-header',
            'name': _("VAT on Purchases:"),
            'level': 0,
            'columns': [
                {'expression_label': 'net_amount', 'value': ''},
                {'expression_label': 'tax_amount', 'value': ''},
            ],
            'unfoldable': False,
            'meta': {'kind': 'section_header', 'section_id': 'vat_purchases'},
        })

        purchase_boxes = [
            ('7', _("7. Standard rated domestic purchases"), True),
            ('8', _("8. Imports subject to VAT paid at customs"), True),
            ('9', _("9. Imports subject to VAT accounted for through reverse charge mechanism"), True),
            ('10', _("10. Zero rated purchases"), False),
            ('11', _("11. Exempt purchases"), False),
        ]

        purchase_base_sum = 0.0
        purchase_vat_sum = 0.0

        for box_no, label, has_vat in purchase_boxes:
            b_data = box_data.get(box_no, {'base': 0.0, 'vat': 0.0, 'tax_id': False})
            b_base = self._eh_round_monetary(b_data['base'], currency=currency)
            b_vat = self._eh_round_monetary(b_data['vat'], currency=currency)
            purchase_base_sum += b_base
            purchase_vat_sum += b_vat

            lines.append({
                'id': "box-%s" % box_no,
                'name': label,
                'level': 1,
                'columns': [
                    {'expression_label': 'net_amount', 'value': b_base},
                    {'expression_label': 'tax_amount', 'value': b_vat if has_vat or b_vat != 0 else (0.0 if box_no in ('8', '9') else '')},
                ],
                'unfoldable': False,
                'meta': {
                    'kind': 'account_total',
                    'section_id': 'vat_purchases',
                    'box_no': box_no,
                    'tax_id': b_data.get('tax_id'),
                },
            })

        # Line 12: Total Purchases
        lines.append({
            'id': 'box-12',
            'name': _("12. Total Purchases"),
            'level': 0,
            'columns': [
                {'expression_label': 'net_amount', 'value': self._eh_round_monetary(purchase_base_sum, currency=currency)},
                {'expression_label': 'tax_amount', 'value': self._eh_round_monetary(purchase_vat_sum, currency=currency)},
            ],
            'unfoldable': False,
            'meta': {'kind': 'section_total', 'section_id': 'vat_purchases'},
        })

        # Line 13: Total VAT due for current period
        total_vat_due = self._eh_round_monetary(sales_vat_sum - purchase_vat_sum, currency=currency)
        lines.append({
            'id': 'box-13',
            'name': _("13. Total VAT due for current period"),
            'level': 0,
            'columns': [
                {'expression_label': 'net_amount', 'value': ''},
                {'expression_label': 'tax_amount', 'value': total_vat_due},
            ],
            'unfoldable': False,
            'meta': {'kind': 'net_profit', 'higher_is_better': False},
        })

        columns = [
            {'expression_label': 'name', 'name': _("Description"), 'figure_type': 'string'},
            {'expression_label': 'net_amount', 'name': _("Amount"), 'figure_type': 'monetary'},
            {'expression_label': 'tax_amount', 'name': _("VAT Amount"), 'figure_type': 'monetary'},
        ]

        meta = {
            'report_code': self.REPORT_CODE,
            'date_from': self._iso_date(date_from),
            'date_to': self._iso_date(date_to),
            'company_ids': sorted(int(c) for c in company_ids),
            'posted_only': posted_only,
        }

        return {
            'columns': columns,
            'lines': lines,
            'totals': {
                'net_amount': sales_base_sum - purchase_base_sum,
                'tax_amount': total_vat_due,
            },
            'generated_at': fields.Datetime.now().isoformat(),
            'meta': meta,
            'currency': self.resolve_currency_info(options),
        }

    # Tag names look like "+1(B)" / "-7(T)": box number, then (B)ase or (T)ax.
    _BOX_TAG_RE = r'^[+-]?([0-9]+)\((B|T)\)$'
    _SALES_BOXES = ('1', '2', '3', '4', '5')
    _PURCHASE_BOXES = ('7', '8', '9', '10', '11')

    @api.model
    def _compute_vat_boxes(self, company_ids, date_from, date_to,
                           posted_only=True, options=None):
        """Aggregate the VAT return boxes.

        Tagged journal items drive the boxes (base from "(B)" tags, VAT
        from "(T)" tags). Tax lines carrying no box tag fall back to box 1
        (sales taxes) or box 7 (purchase taxes) so non-KSA tax setups still
        produce a usable return.
        """
        options = options or {}
        wheres = [
            SQL("aml.company_id IN %s", tuple(int(c) for c in company_ids)),
            SQL("am.state = %s", 'posted') if posted_only
            else SQL("am.state != %s", 'cancel'),
        ]
        if date_from:
            wheres.append(SQL("aml.date >= %s", date_from))
        if date_to:
            wheres.append(SQL("aml.date <= %s", date_to))
        ledger_ids = self.env.context.get('eh_report_ledger_journal_ids')
        if ledger_ids is not None:
            wheres.append(
                SQL("aml.journal_id IN %s", tuple(ledger_ids))
                if ledger_ids else SQL("FALSE"))
        if options.get('journal_ids'):
            wheres.append(SQL(
                "aml.journal_id IN %s",
                tuple(int(i) for i in options['journal_ids'])))
        where = SQL(" AND ").join(wheres)

        tagged = self.env.execute_query_dict(SQL("""
            SELECT box.no AS box_no, box.kind AS kind,
                   SUM(aml.balance) AS balance, MIN(aml.tax_line_id) AS tax_id
              FROM account_move_line aml
              JOIN account_move am ON am.id = aml.move_id
              JOIN LATERAL (
                    SELECT m[1] AS no, m[2] AS kind
                      FROM account_account_tag_account_move_line_rel rel
                      JOIN account_account_tag tag
                        ON tag.id = rel.account_account_tag_id
                      CROSS JOIN LATERAL regexp_match(
                            COALESCE(tag.name->>'en_US', ''), %s) AS m
                     WHERE rel.account_move_line_id = aml.id
                       AND m IS NOT NULL
                     LIMIT 1
              ) box ON TRUE
             WHERE %s
             GROUP BY box.no, box.kind
        """, self._BOX_TAG_RE, where))

        untagged = self.env.execute_query_dict(SQL("""
            SELECT tax.type_tax_use AS use, tax.id AS tax_id,
                   SUM(aml.balance) AS tax_balance,
                   SUM(COALESCE(aml.tax_base_amount, 0)) AS base_amount
              FROM account_move_line aml
              JOIN account_move am ON am.id = aml.move_id
              JOIN account_tax tax ON tax.id = aml.tax_line_id
             WHERE %s
               AND tax.type_tax_use IN ('sale', 'purchase')
               AND NOT EXISTS (
                    SELECT 1
                      FROM account_account_tag_account_move_line_rel rel
                      JOIN account_account_tag tag
                        ON tag.id = rel.account_account_tag_id
                     WHERE rel.account_move_line_id = aml.id
                       AND COALESCE(tag.name->>'en_US', '') ~ %s)
             GROUP BY tax.type_tax_use, tax.id
        """, where, self._BOX_TAG_RE))

        boxes = {str(i): {'base': 0.0, 'vat': 0.0, 'tax_id': False}
                 for i in range(1, 14)}

        for r in tagged:
            box_no = r['box_no']
            if box_no not in boxes or box_no in ('6', '12', '13'):
                continue
            # Sales are credits (negative balance); purchases are debits.
            sign = -1.0 if box_no in self._SALES_BOXES else 1.0
            key = 'base' if r['kind'] == 'B' else 'vat'
            boxes[box_no][key] += float(r['balance'] or 0.0) * sign
            if not boxes[box_no]['tax_id'] and r['tax_id']:
                boxes[box_no]['tax_id'] = r['tax_id']

        for r in untagged:
            is_sale = r['use'] == 'sale'
            box_no = '1' if is_sale else '7'
            sign = -1.0 if is_sale else 1.0
            boxes[box_no]['base'] += float(r['base_amount'] or 0.0)
            boxes[box_no]['vat'] += float(r['tax_balance'] or 0.0) * sign
            if not boxes[box_no]['tax_id']:
                boxes[box_no]['tax_id'] = r['tax_id']

        return boxes

    @api.model
    def _box_tags(self, box_no):
        """Tax tags (both base and tax kinds) that belong to ``box_no``."""
        pattern = re.compile(self._BOX_TAG_RE)
        tags = self.env['account.account.tag'].search(
            [('applicability', '=', 'taxes')])
        return tags.filtered(
            lambda t: (m := pattern.match(t.name or '')) and m.group(1) == box_no)

    @api.model
    def get_drilldown_action(self, options, line_id):
        if not line_id or not isinstance(line_id, str):
            return None
        if not line_id.startswith('box-'):
            return None
        box_no = line_id.split('-', 1)[1]
        if box_no in ('6', '12', '13'):
            return None

        self, options = self._eh_with_ledger_scope(options)
        try:
            date_from = self._extract_date(options, 'date_from')
            date_to = self._extract_date(options, 'date_to')
        except UserError:
            return None

        company_ids = options.get('company_ids') or [self.env.company.id]
        posted_only = bool(options.get('posted_only', True))

        domain = [
            ('company_id', 'in', list(company_ids)),
            ('date', '>=', self._iso_date(date_from)),
            ('date', '<=', self._iso_date(date_to)),
            ('move_id.state', '=', 'posted') if posted_only
            else ('move_id.state', '!=', 'cancel'),
        ]
        ledger_ids = self.env.context.get('eh_report_ledger_journal_ids')
        if ledger_ids is not None:
            domain.append(('journal_id', 'in', list(ledger_ids)))
        if options.get('journal_ids'):
            domain.append(('journal_id', 'in', [int(i) for i in options['journal_ids']]))

        tag_domain = [('tax_tag_ids', 'in', self._box_tags(box_no).ids)]
        if box_no in ('1', '7'):
            all_tags = self.env['account.account.tag'].search(
                [('applicability', '=', 'taxes')]).filtered(
                lambda t: re.match(self._BOX_TAG_RE, t.name or ''))
            use = 'sale' if box_no == '1' else 'purchase'
            tag_domain = [
                '|', ('tax_tag_ids', 'in', self._box_tags(box_no).ids),
                '&', ('tax_line_id.type_tax_use', '=', use),
                ('tax_tag_ids', 'not in', all_tags.ids),
            ]
        domain += tag_domain

        return {
            'type': 'ir.actions.act_window',
            'name': _("Box %s Journal Items", box_no),
            'res_model': 'account.move.line',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': domain,
            'context': {'search_default_group_move': 1},
        }
