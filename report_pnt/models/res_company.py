from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Quitar datos superiores a la tabla
    pnt_check_invoice_shipping_address_block = fields.Boolean(
        string="Remove shipping address block in Invoice",
    )
    pnt_check_invoice_address_not_same_shipping = fields.Boolean(
        string="Remove address not same as shipping in Invoice",
    )
    pnt_check_invoice_address_same_shipping = fields.Boolean(
        string="Remove address same as shipping in Invoice",
    )
    pnt_check_invoice_no_shipping = fields.Boolean(
        string="Remove address no shipping in Invoice",
    )
    pnt_check_invoice_date = fields.Boolean(
        string="Remove Date in Invoice",
    )
    pnt_check_invoice_due_date = fields.Boolean(
        string="Remove Due Date in Invoice",
    )
    pnt_check_invoice_delivery_date = fields.Boolean(
        string="Remove Delivery Date in Invoice",
    )
    pnt_check_invoice_source = fields.Boolean(
        string="Remove Source in Invoice",
    )
    pnt_check_invoice_customer_code = fields.Boolean(
        string="Remove Customer Code in Invoice",
    )
    pnt_check_invoice_reference = fields.Boolean(
        string="Remove Reference in Invoice",
    )
    pnt_check_invoice_incoterm = fields.Boolean(
        string="Remove Incoterm in Invoice",
    )
    # Quitar Columnas
    pnt_check_invoice_description = fields.Boolean(
        string="Remove Description in Invoice",
    )
    pnt_check_invoice_quantity = fields.Boolean(
        string="Remove Quantity in Invoice",
    )
    pnt_check_invoice_unit_price = fields.Boolean(
        string="Remove Unit Price in Invoice",
    )
    pnt_check_invoice_discount = fields.Boolean(
        string="Remove Discount in Invoice",
    )
    pnt_check_invoice_taxes = fields.Boolean(
        string="Remove Taxes in Invoice",
    )
    pnt_check_invoice_subtotal = fields.Boolean(
        string="Remove Subtotal in Invoice",
    )
    # Datos inferiores a la tabla
    pnt_check_invoice_total_table = fields.Boolean(
        string="Remove Total Table in Invoice",
    )
    pnt_check_invoice_fiscal_position = fields.Boolean(
        string="Remove Fiscal Position in Invoice",
    )
    pnt_check_invoice_payment_term_id = fields.Boolean(
        string="Remove Payment Term in Invoice",
    )
    pnt_check_invoice_show_payment_term_details = fields.Boolean(
        string="Remove Table Payment Term in Invoice",
    )
    # Llegué hasta acá <p name="payment_communication">

