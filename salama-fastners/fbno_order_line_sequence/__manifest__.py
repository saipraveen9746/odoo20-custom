{
    'name': 'Order Line Serial Number',
    'version': '20.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Serial number (Sl. No.) on purchase order and sale order lines',
    'description': """
Adds a Sl. No. (1, 2, 3, ...) to purchase order and sale order lines.

* Numbers follow the order of the lines and update when lines are added,
  removed or reordered.
* Section and note lines are not numbered.
* Shown on the PO / RFQ and quotation / sale order screens and PDF reports.
    """,
    'depends': ['purchase', 'sale'],
    'data': [
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'report/purchase_report_templates.xml',
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
