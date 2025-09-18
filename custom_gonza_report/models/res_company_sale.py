from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"
    # Pedido de venta
    # Dirección en pedido
    # Elimina bloque completo de dirección
    check_sale_block_address = fields.Boolean(
        string="Remove shipping address block in Sale Order",
    )
    # Elimina dirección de cliente
    check_sale_partner_address = fields.Boolean(
        string="Remove uniqle Customer Address in Sale Order",
    )
    # Elimina dirección de facturación y envío
    check_sale_customer_address = fields.Boolean(
        string="Remove Invoicing and Shipping Address Customer Address in Sale Order",
    )
    # Crea dirección customizada
    check_sale_custom_address = fields.Boolean(
        string="Custom Address in Sale Order",
    )
    check_sale_partner_name = fields.Boolean(
        string="Add Partner Name in sale",
    )
    check_sale_partner_street = fields.Boolean(
        string="Add Partner Street in sale",
    )
    check_sale_partner_street2 = fields.Boolean(
        string="Add Partner Street2 in sale",
    )
    check_sale_partner_city = fields.Boolean(
        string="Add Partner City in sale",
    )
    check_sale_partner_state = fields.Boolean(
        string="Add Partner State in sale",
    )
    check_sale_partner_country = fields.Boolean(
        string="Add Partner Country in sale",
    )
    check_sale_partner_zip = fields.Boolean(
        string="Add Partner Zip in sale",
    )
    check_sale_partner_phone = fields.Boolean(
        string="Add Partner Phone in sale",
    )
    check_sale_partner_mobile = fields.Boolean(
        string="Add Partner Mobile in sale",
    )
    check_sale_partner_vat = fields.Boolean(
        string="Add Partner VAT in sale",
    )
    check_sale_partner_email = fields.Boolean(
        string="Add Partner Email in sale",
    )
    check_sale_partner_website = fields.Boolean(
        string="Add Partner Website in sale",
    )
    check_sale_partner_reference = fields.Boolean(
        string="Add Partner Reference in sale",
    )
    check_sale_shipping_partner_name = fields.Boolean(
        string="Add Shipping Partner Name in sale",
    )
    check_sale_shipping_partner_street = fields.Boolean(
        string="Add Shipping Partner Street in sale",
    )
    check_sale_shipping_partner_street2 = fields.Boolean(
        string="Add Shipping Partner Street2 in sale",
    )
    check_sale_shipping_partner_city = fields.Boolean(
        string="Add Shipping Partner City in sale",
    )
    check_sale_shipping_partner_state = fields.Boolean(
        string="Add Shipping Partner State in sale",
    )
    check_sale_shipping_partner_country = fields.Boolean(
        string="Add Shipping Partner Country in sale",
    )
    check_sale_shipping_partner_zip = fields.Boolean(
        string="Add Shipping Partner Zip in sale",
    )
    check_sale_shipping_partner_phone = fields.Boolean(
        string="Add Shipping Partner Phone in sale",
    )
    check_sale_shipping_partner_mobile = fields.Boolean(
        string="Add Shipping Partner Mobile in sale",
    )
    check_sale_shipping_partner_email = fields.Boolean(
        string="Add Shipping Partner Email in sale",
    )
    check_sale_shipping_partner_vat = fields.Boolean(
        string="Add Shipping Partner VAT in sale",
    )
    check_sale_shipping_partner_website = fields.Boolean(
        string="Add Shipping Partner Website in sale",
    )
    check_sale_shipping_partner_reference = fields.Boolean(
        string="Add Shipping Partner Reference in sale",
    )
    # Datos encabezado
    # Elimina título del presupuesto
    sale_not_title = fields.Boolean(
        string="Remove Title in Sale Order",
    )
    # Elimina palabra de proforma
    sale_not_proforma = fields.Boolean(
        string="Remove Proforma in Sale Order",
    )
    # Elimina palabra presupuesto
    sale_not_quotation = fields.Boolean(
        string="Remove Quotation in Sale Order",
    )
    # Elimina palabra pedido
    sale_not_order = fields.Boolean(
        string="Remove Order in Sale Order",
    )
    # Elimina número de presupuesto
    sale_name_order = fields.Boolean(
        string="Remove Number in Sale Order",
    )
    # Elimina Referencia
    sale_reference = fields.Boolean(
        string="Remove Reference in Sale Order",
    )
    # Elimina Fecha
    sale_date = fields.Boolean(
        string="Remove Date in Sale Order",
    )
    # Elimina Fecha de vencimiento
    sale_due_date = fields.Boolean(
        string="Remove Due Date in Sale Order",
    )
    # Elimina comercial
    sale_salesperson = fields.Boolean(
        string="Remove Salesperson in Sale Order",
    )
    # Tabla pedido de venta
    # Elimina columna descripción
    sale_description_column = fields.Boolean(
        string="Remove Description Column in Sale Order",
    )
    # Elimina columna descripción pero agrega producto name
    sale_description_column_product_name = fields.Boolean(
        string="Remove Reference-Description Column in Sale Order",
    )
    # Agrega descripción de venta en producto
    sale_description_product_description = fields.Boolean(
        string="Add Product Sale Description in Sale Order",
    )
    # Agrega columna referencia de producto
    sale_reference_column = fields.Boolean(
        string="Add Reference Column in Sale Order",
    )
    # Elimina columna cantidad
    sale_quantity_column = fields.Boolean(
        string="Remove Quantity Column in Sale Order",
    )
    # Elimina columna precio unitario
    sale_price_column = fields.Boolean(
        string="Remove Price Column in Sale Order",
    )
    # Elimina columna descuento
    sale_discount_column = fields.Boolean(
        string="Remove Discount Column in Sale Order",
    )
    # Elimina columna impuestos
    sale_taxes_column = fields.Boolean(
        string="Remove Taxes Column in Sale Order",
    )
    # Elimina columna totales
    sale_total_column = fields.Boolean(
        string="Remove Subtotal Column in Sale Order",
    )
    # Oculta palabra unidades
    sale_units_word = fields.Boolean(
        string="Remove Units Word in Sale Order",
    )
    # Oculta palabra paquetes
    sale_packaging_word = fields.Boolean(
        string="Remove Packaging Word in Sale Order",
    )
    # Modificar decimales de la tabla
    sale_decimals_quantity = fields.Integer(
        string="Decimals Quantity in Sale",
        default=2,
    )
    sale_decimals_price = fields.Integer(
        string="Decimals Price in Sale",
        default=2,
    )
    sale_decimals_discount = fields.Integer(
        string="Decimals Discount in Sale",
        default=2,
    )
    sale_decimals_subtotal = fields.Integer(
        string="Decimals Subtotal in Sale",
        default=2,
    )
    # Elimina fila notas
    sale_note = fields.Boolean(
        string="Remove Note in Sale"
    )
    # Elimina fila secciones
    sale_section = fields.Boolean(
        string="Remove Sections in Sale"
    )
    # Elimina fila de subtotales
    sale_subtotal_row = fields.Boolean(
        string="Remove Subtotal row in Sale"
    )
    # Oculta tabla de totales
    sale_total_table = fields.Boolean(
        string="Remove Total Table in Sale"
    )
    # Datos inferiores pedido de venta
    # Oculta firma
    sale_signature = fields.Boolean(
        string="Remove Signature in Sale"
    )
    # Oculta Términos de Pago
    sale_terms_payments = fields.Boolean(
        string="Remove Terms of Payment in Sale"
    )
    # Oculta Nota de Ajustes
    sale_note_settings = fields.Boolean(
        string="Remove Note Settings in Sale"
    )
    # Oculta posición fiscal
    sale_fiscal_position_remark = fields.Boolean(
        string="Remove Fiscal Position in Sale"
    )
