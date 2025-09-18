from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Direccion en factura
    check_invoice_shipping_address_block = fields.Boolean(
        string="Remove shipping address block in Invoice",
    )
    check_invoice_address_not_same_shipping = fields.Boolean(
        string="Remove address not same as shipping in Invoice",
    )
    check_invoice_address_same_shipping = fields.Boolean(
        string="Remove address same as shipping in Invoice",
    )
    check_invoice_no_shipping = fields.Boolean(
        string="Remove address no shipping in Invoice",
    )
    check_invoice_custom_address = fields.Boolean(
        string="Custom Address in Invoice",
    )
    check_invoice_partner_name = fields.Boolean(
        string="Add Partner Name in Invoice",
    )
    check_invoice_partner_street = fields.Boolean(
        string="Add Partner Street in Invoice",
    )
    check_invoice_partner_street2 = fields.Boolean(
        string="Add Partner Street2 in Invoice",
    )
    check_invoice_partner_city = fields.Boolean(
        string="Add Partner City in Invoice",
    )
    check_invoice_partner_state = fields.Boolean(
        string="Add Partner State in Invoice",
    )
    check_invoice_partner_country = fields.Boolean(
        string="Add Partner Country in Invoice",
    )
    check_invoice_partner_zip = fields.Boolean(
        string="Add Partner Zip in Invoice",
    )
    check_invoice_partner_phone = fields.Boolean(
        string="Add Partner Phone in Invoice",
    )
    check_invoice_partner_mobile = fields.Boolean(
        string="Add Partner Mobile in Invoice",
    )
    check_invoice_partner_email = fields.Boolean(
        string="Add Partner Email in Invoice",
    )
    check_invoice_partner_vat = fields.Boolean(
        string="Add Partner VAT in Invoice",
    )
    check_invoice_partner_website = fields.Boolean(
        string="Add Partner Website in Invoice",
    )
    check_invoice_partner_reference = fields.Boolean(
        string="Add Partner Reference in Invoice",
    )
    check_invoice_shipping_partner_name = fields.Boolean(
        string="Add Shipping Partner Name in Invoice",
    )
    check_invoice_shipping_partner_street = fields.Boolean(
        string="Add Shipping Partner Street in Invoice",
    )
    check_invoice_shipping_partner_street2 = fields.Boolean(
        string="Add Shipping Partner Street2 in Invoice",
    )
    check_invoice_shipping_partner_city = fields.Boolean(
        string="Add Shipping Partner City in Invoice",
    )
    check_invoice_shipping_partner_state = fields.Boolean(
        string="Add Shipping Partner State in Invoice",
    )
    check_invoice_shipping_partner_country = fields.Boolean(
        string="Add Shipping Partner Country in Invoice",
    )
    check_invoice_shipping_partner_zip = fields.Boolean(
        string="Add Shipping Partner Zip in Invoice",
    )
    check_invoice_shipping_partner_phone = fields.Boolean(
        string="Add Shipping Partner Phone in Invoice",
    )
    check_invoice_shipping_partner_mobile = fields.Boolean(
        string="Add Shipping Partner Mobile in Invoice",
    )
    check_invoice_shipping_partner_email = fields.Boolean(
        string="Add Shipping Partner Email in Invoice",
    )
    check_invoice_shipping_partner_vat = fields.Boolean(
        string="Add Shipping Partner VAT in Invoice",
    )
    check_invoice_shipping_partner_website = fields.Boolean(
        string="Add Shipping Partner Website in Invoice",
    )
    check_invoice_shipping_partner_reference = fields.Boolean(
        string="Add Shipping Partner Reference in Invoice",
    )
    # Quitar datos superiores a la tabla
    check_invoice_name = fields.Boolean(
        string="Remove Name in Invoice",
    )
    check_invoice_date = fields.Boolean(
        string="Remove Date in Invoice",
    )
    check_invoice_due_date = fields.Boolean(
        string="Remove Due Date in Invoice",
    )
    check_invoice_delivery_date = fields.Boolean(
        string="Remove Delivery Date in Invoice",
    )
    check_invoice_source = fields.Boolean(
        string="Remove Source in Invoice",
    )
    check_invoice_customer_code = fields.Boolean(
        string="Remove Customer Code in Invoice",
    )
    check_invoice_reference = fields.Boolean(
        string="Remove Reference in Invoice",
    )
    check_invoice_incoterm = fields.Boolean(
        string="Remove Incoterm in Invoice",
    )
    # Quitar Columnas en Factura
    check_invoice_description = fields.Boolean(
        string="Remove Description in Invoice",
    )
    check_invoice_description_reference = fields.Boolean(
        string="Remove Product Reference-Description in Invoice",
    )
    check_invoice_quantity = fields.Boolean(
        string="Remove Quantity in Invoice",
    )
    check_invoice_unit_price = fields.Boolean(
        string="Remove Unit Price in Invoice",
    )
    check_invoice_discount = fields.Boolean(
        string="Remove Discount in Invoice",
    )
    check_invoice_taxes = fields.Boolean(
        string="Remove Taxes in Invoice",
    )
    check_invoice_subtotal = fields.Boolean(
        string="Remove Subtotal in Invoice",
    )
    check_invoice_section = fields.Boolean(
        string="Remove Section in Invoice",
    )
    check_invoice_notes = fields.Boolean(
        string="Remove Notes in Invoice",
    )
    check_invoice_line_subtotal = fields.Boolean(
        string="Remove Line Subtotal in Invoice",
    )
    # Modificar decimales de la tabla
    decimals_quantity_invoice = fields.Integer(
        string="Decimals Quantity in Invoice",
        default=2,
    )
    decimals_price_invoice = fields.Integer(
        string="Decimals Price in Invoice",
        default=2,
    )
    decimals_discount_invoice = fields.Integer(
        string="Decimals Discount in Invoice",
        default=2,
    )
    decimals_subtotal_invoice = fields.Integer(
        string="Decimals Subtotal in Invoice",
        default=2,
    )
    # Agrega columnas
    check_invoice_description_reference_column = fields.Boolean(
        string="Add Product Reference Column in Invoice",
    )
    check_invoice_description_sale = fields.Boolean(
        string="Add Product Sale Description Column in Invoice",
    )
    check_invoice_lot_name_in_column = fields.Boolean(
        string="Add Lot Name Column in Invoice",
    )
    # Datos inferiores a la tabla
    check_invoice_total_table = fields.Boolean(
        string="Remove Total Table in Invoice",
    )
    check_invoice_payments_table = fields.Boolean(
        string="Remove Payments Table in Invoice",
    )
    check_invoice_payments_words_table = fields.Boolean(
        string="Remove Payments Words in Invoice",
    )
    check_invoice_fiscal_position = fields.Boolean(
        string="Remove Fiscal Position in Invoice",
    )
    check_invoice_payment_term_id = fields.Boolean(
        string="Remove Payment Term in Invoice",
    )
    check_invoice_show_payment_term_details = fields.Boolean(
        string="Remove Table Payment Term in Invoice",
    )
    check_invoice_payment_communication = fields.Boolean(
        string="Remove Payment Communication in Invoice",
    )
    check_invoice_qrcode = fields.Boolean(
        string="Remove QR Code in Invoice",
    )
    check_invoice_comment = fields.Boolean(
        string="Remove Note for settings in Invoice",
    )
    check_units_invoice = fields.Boolean(
        string="Remove Units in Invoice",
    )
    # Cuadro de totales
    check_total_subtotal = fields.Boolean(
        string="Remove Subtotal in Total Table",
    )
    check_total_taxes = fields.Boolean(
        string="Remove Taxes in Total Table",
    )
    check_total_total = fields.Boolean(
        string="Remove Total in Total Table",
    )
    check_rounding_total = fields.Boolean(
        string="Remove Rounding in Total Table",
    )
