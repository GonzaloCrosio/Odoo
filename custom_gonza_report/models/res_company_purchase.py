from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # ORDEN DE COMPRA
    # Elimina dirección de envío de la compañía
    purchase_company_address = fields.Boolean(
        string="Remove Company Address in Purchase Order",
    )
    # Elimina dirección del partner que nos vende
    purchase_partner_address = fields.Boolean(
        string="Remove Partner Address in Purchase Order",
    )
    # Permite crear una dirección personalizada
    check_purchase_custom_address = fields.Boolean(
        string="Create Custom Address in Purchase Order",
    )
    # Campos de dirección personalizada
    check_purchase_partner_name = fields.Boolean(
        string="Add Partner Name in purchase",
    )
    check_purchase_partner_street = fields.Boolean(
        string="Add Partner Street in purchase",
    )
    check_purchase_partner_street2 = fields.Boolean(
        string="Add Partner Street2 in purchase",
    )
    check_purchase_partner_city = fields.Boolean(
        string="Add Partner City in purchase",
    )
    check_purchase_partner_state = fields.Boolean(
        string="Add Partner State in purchase",
    )
    check_purchase_partner_country = fields.Boolean(
        string="Add Partner Country in purchase",
    )
    check_purchase_partner_zip = fields.Boolean(
        string="Add Partner Zip in purchase",
    )
    check_purchase_partner_phone = fields.Boolean(
        string="Add Partner Phone in purchase",
    )
    check_purchase_partner_mobile = fields.Boolean(
        string="Add Partner Mobile in purchase",
    )
    check_purchase_partner_email = fields.Boolean(
        string="Add Partner Email in purchase",
    )
    check_purchase_partner_vat = fields.Boolean(
        string="Add Partner VAT in purchase",
    )
    check_purchase_partner_website = fields.Boolean(
        string="Add Partner Website in purchase",
    )
    check_purchase_partner_reference = fields.Boolean(
        string="Add Partner Reference in purchase",
    )
    check_purchase_shipping_company_name = fields.Boolean(
        string="Add Shipping Company Name in purchase",
    )
    check_purchase_shipping_company_street = fields.Boolean(
        string="Add Shipping Company Street in purchase",
    )
    check_purchase_shipping_company_street2 = fields.Boolean(
        string="Add Shipping Company Street2 in purchase",
    )
    check_purchase_shipping_company_city = fields.Boolean(
        string="Add Shipping Company City in purchase",
    )
    check_purchase_shipping_company_state = fields.Boolean(
        string="Add Shipping Company State in purchase",
    )
    check_purchase_shipping_company_country = fields.Boolean(
        string="Add Shipping Company Country in purchase",
    )
    check_purchase_shipping_company_zip = fields.Boolean(
        string="Add Shipping Company Zip in purchase",
    )
    check_purchase_shipping_company_phone = fields.Boolean(
        string="Add Shipping Company Phone in purchase",
    )
    check_purchase_shipping_company_mobile = fields.Boolean(
        string="Add Shipping Company Mobile in purchase",
    )
    check_purchase_shipping_company_email = fields.Boolean(
        string="Add Shipping Company Email in purchase",
    )
    check_purchase_shipping_company_vat = fields.Boolean(
        string="Add Shipping Company VAT in purchase",
    )
    check_purchase_shipping_company_website = fields.Boolean(
        string="Add Shipping Company Website in purchase",
    )
    check_purchase_shipping_company_reference = fields.Boolean(
        string="Add Shipping Company Reference in purchase",
    )
    # Elimina título de la orden de compra
    check_purchase_not_title = fields.Boolean(
        string="Remove Title in Purchase Order",
    )
    # Elimina comprador en datos superiores
    check_purchase_buyer = fields.Boolean(
        string="Remove Buyer in Purchase Order",
    )
    # Eliminar referencia en datos superiores
    check_purchase_reference = fields.Boolean(
        string="Remove Reference in Purchase Order",
    )
    # Elimina fecha en datos superiores
    check_purchase_date = fields.Boolean(
        string="Remove Date in Purchase Order",
    )
    # Elimina fecha de vencimiento en datos superiores
    check_purchase_deadline_date = fields.Boolean(
        string="Remove Deadline in Purchase Order",
    )
    # Elimina fecha de entrega en datos superiores
    check_purchase_date_planned = fields.Boolean(
        string="Remove Expected Arrival in Purchase Order",
    )
    # Elimina el incoterm en datos superiores
    check_purchase_incoterm = fields.Boolean(
        string="Remove Incoterm in Purchase Order",
    )
    # Datos de Tabla
    # Elimina la columna de descripción
    check_purchase_description = fields.Boolean(
        string="Remove Description in Purchase Order",
    )
    # Elimina la columna de cantidad
    check_purchase_quantity = fields.Boolean(
        string="Remove Quantity in Purchase Order",
    )
    # Elimina palabra unidad de medida
    check_purchase_uom_name = fields.Boolean(
        string="Remove Unit of Measure in Purchase Order",
    )
    # Elimina la palabra paquetes
    check_purchase_package_name = fields.Boolean(
        string="Remove Package in Purchase Order",
    )
    # Elimina la columna de precio unitario
    check_purchase_unit_price = fields.Boolean(
        string="Remove Unit Price in Purchase Order",
    )
    # Elimina la columna descuento
    check_purchase_discount = fields.Boolean(
        string="Remove Discount in Purchase Order",
    )
    # Elimina la columna de impuesto
    check_purchase_tax = fields.Boolean(
        string="Remove Tax in Purchase Order",
    )
    # Elimina la columna de importe subtotal
    check_purchase_subtotal = fields.Boolean(
        string="Remove Subtotal in Purchase Order",
    )
    # Separa referencia interna del producto
    check_purchase_product_reference = fields.Boolean(
        string="Remove Product Reference in Purchase Order",
    )
    # Crea columna de referencia del producto
    check_purchase_product_reference_column = fields.Boolean(
        string="Add Product Reference Column in Purchase Order",
    )
    # Agregar descripción de compra del producto
    check_purchase_product_description = fields.Boolean(
        string="Add Product Purchase Description in Purchase Order",
    )
    # Modifica decimales de las columnas
    check_purchase_quantity_decimals = fields.Integer(
        string="Quantity Decimals in Purchase Order",
        default=0,
    )
    check_purchase_unit_price_decimals = fields.Integer(
        string="Unit Price Decimals in Purchase Order",
        default=2,
    )
    check_purchase_discount_decimals = fields.Integer(
        string="Discount Decimals in Purchase Order",
        default=2,
    )
    # Elimina notas
    check_purchase_notes = fields.Boolean(
        string="Remove Notes in Purchase Order",
    )
    # Elimina secciones
    check_purchase_section = fields.Boolean(
        string="Remove Section in Purchase Order",
    )
    # Elimina fila de subtotal
    check_purchase_subtotal_row = fields.Boolean(
        string="Remove Subtotal Row in Purchase Order",
    )
    # Ocultar cuadro de totales
    check_purchase_totals = fields.Boolean(
        string="Remove Totals in Purchase Order",
    )
    # Ocultar notas de pie
    check_purchase_footer_notes = fields.Boolean(
        string="Remove Footer Notes in Purchase Order",
    )
    # Ocultar términos de pago
    check_purchase_payment_terms = fields.Boolean(
        string="Remove Payment Terms in Purchase Order",
    )


