from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    # Albarán de entrega
    # Direcciones
    # Elimina bloque completo de dirección

    check_picking_outgoing_address_block = fields.Boolean(
        string="Remove shipping outgoing address block in picking",
    )
    check_picking_outgoing_warehouse_address = fields.Boolean(
        string="Remove outgoing warehouse address shipping in internal picking",
    )
    check_incoming_picking_vendor_address_shipping = fields.Boolean(
        string="Remove vendor address shipping in incoming picking",
    )
    check_outgoing_picking_customer_address = fields.Boolean(
        string="Remove customer address shipping in outgoing picking",
    )
    check_picking_custom_address = fields.Boolean(
        string="Custom Address in picking",
    )
    check_picking_partner_name = fields.Boolean(
        string="Add Partner Name in picking",
    )
    check_picking_partner_street = fields.Boolean(
        string="Add Partner Street in picking",
    )
    check_picking_partner_street2 = fields.Boolean(
        string="Add Partner Street2 in picking",
    )
    check_picking_partner_city = fields.Boolean(
        string="Add Partner City in picking",
    )
    check_picking_partner_state = fields.Boolean(
        string="Add Partner State in picking",
    )
    check_picking_partner_country = fields.Boolean(
        string="Add Partner Country in picking",
    )
    check_picking_partner_zip = fields.Boolean(
        string="Add Partner Zip in picking",
    )
    check_picking_partner_phone = fields.Boolean(
        string="Add Partner Phone in picking",
    )
    check_picking_partner_mobile = fields.Boolean(
        string="Add Partner Mobile in picking",
    )
    check_picking_partner_email = fields.Boolean(
        string="Add Partner Email in picking",
    )
    check_picking_partner_vat = fields.Boolean(
        string="Add Partner VAT in picking",
    )
    check_picking_partner_website = fields.Boolean(
        string="Add Partner Website in picking",
    )
    check_picking_partner_reference = fields.Boolean(
        string="Add Partner Reference in picking",
    )
    check_picking_shipping_company_name = fields.Boolean(
        string="Add Company Name in picking",
    )
    check_picking_shipping_company_street = fields.Boolean(
        string="Add Company Street in picking",
    )
    check_picking_shipping_company_street2 = fields.Boolean(
        string="Add Company Street2 in picking",
    )
    check_picking_shipping_company_city = fields.Boolean(
        string="Add Company City in picking",
    )
    check_picking_shipping_company_state = fields.Boolean(
        string="Add Company State in picking",
    )
    check_picking_shipping_company_country = fields.Boolean(
        string="Add Company Country in picking",
    )
    check_picking_shipping_company_zip = fields.Boolean(
        string="Add Company Zip in picking",
    )
    check_picking_shipping_company_phone = fields.Boolean(
        string="Add Company Phone in picking",
    )
    check_picking_shipping_company_mobile = fields.Boolean(
        string="Add Company Mobile in picking",
    )
    check_picking_shipping_company_email = fields.Boolean(
        string="Add Company Email in picking",
    )
    check_picking_shipping_company_vat = fields.Boolean(
        string="Add Company VAT in picking",
    )
    check_picking_shipping_company_website = fields.Boolean(
        string="Add Company Website in picking",
    )
    check_picking_shipping_company_reference = fields.Boolean(
        string="Add Company Reference in picking",
    )
    # Oculta datos encabezado
    check_picking_title_outgoing = fields.Boolean(
        string="Remove Title in Outgoing Delivery"
    )
    check_picking_title_incoming = fields.Boolean(
        string="Remove Title in Incoming Delivery"
    )
    check_picking_informations_outgoing = fields.Boolean(
        string="Remove Total Informations in Outgoing Delivery"
    )
    check_picking_informations_incoming = fields.Boolean(
        string="Remove Total Informations in Incoming Delivery"
    )
    check_picking_order_outgoing = fields.Boolean(
        string="Remove Order in Outgoing Delivery"
    )
    check_picking_order_incoming = fields.Boolean(
        string="Remove Order in Incoming Delivery"
    )
    check_picking_shipping_date_outgoing = fields.Boolean(
        string="Remove Shipping Date in Outgoing Delivery"
    )
    check_picking_shipping_date_incoming = fields.Boolean(
        string="Remove Shipping Date in Incoming Delivery"
    )
    # Campos de tabla de albarán con state distinto de done
    picking_table_not_done_product_outgoing = fields.Boolean(
        string="Remove Product in Outgoing Picking Table with state not done"
    )
    check_picking_table_not_done_product_incoming = fields.Boolean(
        string="Remove Product in Incoming Picking Table with state not done"
    )
    picking_table_not_done_ordered_outgoing = fields.Boolean(
        string="Remove Ordered in Outgoing Picking Table with state not done"
    )
    picking_table_not_done_ordered_incoming = fields.Boolean(
        string="Remove Ordered in Incoming Picking Table with state not done"
    )
    picking_table_not_done_delivered_outgoing = fields.Boolean(
        string="Remove Delivered in Outgoing Picking Table with state not done"
    )
    picking_table_not_done_delivered_incoming = fields.Boolean(
        string="Remove Delivered in Incoming Picking Table with state not done"
    )
    # Campos de tabla de albarán con state igual a done
    picking_table_done_product_outgoing = fields.Boolean(
        string="Remove Product in Outgoing Picking Table with state done"
    )
    picking_table_done_product_incoming = fields.Boolean(
        string="Remove Product in Incoming Picking Table with state done"
    )
    picking_table_done_ordered_outgoing = fields.Boolean(
        string="Remove Ordered in Outgoing Picking Table with state done"
    )
    picking_table_done_ordered_incoming = fields.Boolean(
        string="Remove Ordered in Incoming Picking Table with state done"
    )
    picking_table_done_lot_outgoing = fields.Boolean(
        string="Remove Lot/Serial Number in Outgoing Picking Table with state done"
    )
    picking_table_done_lot_incoming = fields.Boolean(
        string="Remove Lot/Serial in Incoming Picking Table with state done"
    )
    picking_table_done_delivered_outgoing = fields.Boolean(
        string="Remove Delivered in Outgoing Picking Table with state done"
    )
    picking_table_done_delivered_incoming = fields.Boolean(
        string="Remove Delivered in Incoming Picking Table with state done"
    )
    # Modificar decimales de la tabla
    picking_table_decimals_quantity_ordered = fields.Integer(
        string="Decimals Quantity Ordered in Picking",
        default=2,
    )
    picking_table_decimals_quantity_delivered = fields.Integer(
        string="Decimals Quantity Delivered in Picking",
        default=2,
    )
    # Oculta datos paquetes en tabla de albarán
    check_picking_table_info_package_outgoing = fields.Boolean(
        string="Remove Info Package in Outgoing Picking Table"
    )
    check_picking_table_info_package_incoming = fields.Boolean(
        string="Remove Info Package in Incoming Picking Table"
    )
    # Datos inferiores del albarán
    check_picking_outgoing_backorders = fields.Boolean(
        string="Remove BackOrderds Table in Outgoing Picking",
    )
    check_picking_incoming_backorders = fields.Boolean(
        string="Remove BackOrderds Table in Incoming Picking",
    )
    check_picking_outgoing_signature = fields.Boolean(
        string="Remove Signature in Outgoing Picking",
    )
    check_picking_incoming_signature = fields.Boolean(
        string="Remove Signature in Incoming Picking",
    )

