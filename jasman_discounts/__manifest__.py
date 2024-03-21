{
    "name": "Discounts related to sale order lines",
    "description": 
  """
    This module enhances the behavior of discounts through promotions and introduces amount discount and reduces price:
    - When a discount is applied through promotions (such as for the entire order, specific products, or the cheapest items), the quantity of the discount line is set to zero. This ensures that the total price remains unchanged by discount lines.
    - Discounts applied through promotions are now reflected in the sale order line discount, amount discount and reduced price fields.
    - Added sale order line domain to conditional and reward rules.
    - Discount management during sales by automatically adjusting the amount discount and reduced price when discounts change due to promotions. Allows manual changes only to the amount discount field, and recomputes discount and reduced price fields.
    - Button to delete promotion discounts in all sale order.
    - Task ID: 3730047
    """,
    "category": "Custom Development",
    "version": "1.0.0",
    "author": "Odoo Development Services",
  "maintainer": "Odoo Development Services",
  "website": "https://www.odoo.com/",
    "license": "OPL-1",
    "depends": [
        "sale_management",
        "sale_stock",
        "loyalty",
        "sale",
    ],
    "data": [
          'views/view_order_form.xml',
          'views/loyalty_program_views.xml',
          'views/loyalty_rule_views.xml',
          'views/loyalty_reward_views.xml',
    ],
}
