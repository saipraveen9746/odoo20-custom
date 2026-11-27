# -*- encoding: utf-8 -*-
##############################################################################
#
# ERP Heritage
# Copyright (C) 2026 (https://www.erpheritage.com.au/)
#
##############################################################################
from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    # Reporting menus of other accounting add-ons that this module already
    # covers with a dynamic report. They are hidden (archived), never deleted,
    # so they can be re-enabled by unarchiving the menu. Odoo core reports and
    # reports with no dynamic equivalent (Day Book, Journals Audit, Annual
    # Report, Aged Partner Balance, ...) are left untouched.
    _EH_DUPLICATE_REPORT_MENUS = (
        # accounting_pdf_reports
        'accounting_pdf_reports.menu_account_report_bs',          # Balance Sheet
        'accounting_pdf_reports.menu_account_report_pl',          # Profit and Loss
        'accounting_pdf_reports.menu_account_report_cash_flow',   # Cash Flow
        'accounting_pdf_reports.menu_partner_ledger',             # Partner Ledger
        'accounting_pdf_reports.menu_aged_receivable',            # Aged Receivable
        'accounting_pdf_reports.menu_aged_payable',               # Aged Payable
        'accounting_pdf_reports.menu_general_ledger',             # General Ledger
        'accounting_pdf_reports.menu_general_balance_report',     # Trial Balance
        'accounting_pdf_reports.menu_account_report',             # Tax Report
        # base_accounting_kit
        'base_accounting_kit.account_financial_reports_profit_loss',
        'base_accounting_kit._account_financial_reports_balance_sheet',
        'base_accounting_kit.menu_account_cash_flow_report',
        'base_accounting_kit.menu_partner_ledger',
        'base_accounting_kit.menu_general_ledger',
        'base_accounting_kit.menu_Balance_report',
        'base_accounting_kit.menu_tax_report',
    )

    @api.model
    def _eh_hide_duplicate_report_menus(self):
        for xmlid in self._EH_DUPLICATE_REPORT_MENUS:
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            if menu and menu._name == 'ir.ui.menu' and menu.active:
                menu.active = False
        return True
