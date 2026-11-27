{
    'name': 'Product Last Purchase Price',
    'version': '20.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Show the last purchase price and vendor on products, updated from purchase orders',
    'description': """
Adds Last Purchase Price, Last Vendor and Last Purchase Date to products.

* Values are taken from the most recently confirmed purchase order line of the product.
* Price is the discounted unit price, converted to the product's unit of measure
  and to the company currency at the order confirmation date.
* Updated automatically when a purchase order is confirmed or cancelled, or when
  the price of a confirmed line changes.
* Existing confirmed purchase orders are used to fill the values on installation.
* Shown in the product (template and variant) list views and on the product form.
    """,
    'depends': ['purchase'],
    'data': [
        'views/product_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
