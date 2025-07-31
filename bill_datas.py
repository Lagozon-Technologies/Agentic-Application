def invoice_data(results, bill_data):
    for invoice in bill_data.documents:
        invoice_info = {}

        # Vendor information
        vendor_name = invoice.fields.get("VendorName")
        if vendor_name and hasattr(vendor_name, 'content'):
            invoice_info["Vendor Name"] = vendor_name.content

        vendor_address = invoice.fields.get("VendorAddress")
        if vendor_address and hasattr(vendor_address, 'content'):
            invoice_info["Vendor Address"] = vendor_address.content

        vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
        if vendor_address_recipient and hasattr(vendor_address_recipient, 'content'):
            invoice_info["Vendor Address Recipient"] = vendor_address_recipient.content

        # Customer information
        customer_name = invoice.fields.get("CustomerName")
        if customer_name and hasattr(customer_name, 'content'):
            invoice_info["Customer Name"] = customer_name.content

        customer_id = invoice.fields.get("CustomerId")
        if customer_id and hasattr(customer_id, 'content'):
            invoice_info["Customer ID"] = customer_id.content

        customer_address = invoice.fields.get("CustomerAddress")
        if customer_address and hasattr(customer_address, 'content'):
            invoice_info["Customer Address"] = customer_address.content

        customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
        if customer_address_recipient and hasattr(customer_address_recipient, 'content'):
            invoice_info["Customer Address Recipient"] = customer_address_recipient.content

        # Invoice details
        invoice_id = invoice.fields.get("InvoiceId")
        if invoice_id and hasattr(invoice_id, 'content'):
            invoice_info["Invoice ID"] = invoice_id.content

        invoice_date = invoice.fields.get("InvoiceDate")
        if invoice_date and hasattr(invoice_date, 'content'):
            invoice_info["Invoice Date"] = invoice_date.content

        invoice_total = invoice.fields.get("InvoiceTotal")
        if invoice_total and hasattr(invoice_total, 'content'):
            invoice_info["Invoice Total"] = invoice_total.content

        due_date = invoice.fields.get("DueDate")
        if due_date and hasattr(due_date, 'content'):
            invoice_info["Due Date"] = due_date.content

        purchase_order = invoice.fields.get("PurchaseOrder")
        if purchase_order and hasattr(purchase_order, 'content'):
            invoice_info["Purchase Order"] = purchase_order.content

        # Billing information
        billing_address = invoice.fields.get("BillingAddress")
        if billing_address and hasattr(billing_address, 'content'):
            invoice_info["Billing Address"] = billing_address.content

        billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
        if billing_address_recipient and hasattr(billing_address_recipient, 'content'):
            invoice_info["Billing Address Recipient"] = billing_address_recipient.content

        # Shipping information
        shipping_address = invoice.fields.get("ShippingAddress")
        if shipping_address and hasattr(shipping_address, 'content'):
            invoice_info["Shipping Address"] = shipping_address.content

        shipping_address_recipient = invoice.fields.get("ShippingAddressRecipient")
        if shipping_address_recipient and hasattr(shipping_address_recipient, 'content'):
            invoice_info["Shipping Address Recipient"] = shipping_address_recipient.content

        # Totals
        subtotal = invoice.fields.get("SubTotal")
        if subtotal and hasattr(subtotal, 'content'):
            invoice_info["Subtotal"] = subtotal.content

        total_tax = invoice.fields.get("TotalTax")
        if total_tax and hasattr(total_tax, 'content'):
            invoice_info["Total Tax"] = total_tax.content

        previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
        if previous_unpaid_balance and hasattr(previous_unpaid_balance, 'content'):
            invoice_info["Previous Unpaid Balance"] = previous_unpaid_balance.content

        amount_due = invoice.fields.get("AmountDue")
        if amount_due and hasattr(amount_due, 'content'):
            invoice_info["Amount Due"] = amount_due.content

        # Service information
        service_start_date = invoice.fields.get("ServiceStartDate")
        if service_start_date and hasattr(service_start_date, 'content'):
            invoice_info["Service Start Date"] = service_start_date.content

        service_end_date = invoice.fields.get("ServiceEndDate")
        if service_end_date and hasattr(service_end_date, 'content'):
            invoice_info["Service End Date"] = service_end_date.content

        service_address = invoice.fields.get("ServiceAddress")
        if service_address and hasattr(service_address, 'content'):
            invoice_info["Service Address"] = service_address.content

        service_address_recipient = invoice.fields.get("ServiceAddressRecipient")
        if service_address_recipient and hasattr(service_address_recipient, 'content'):
            invoice_info["Service Address Recipient"] = service_address_recipient.content

        # Remittance information
        remittance_address = invoice.fields.get("RemittanceAddress")
        if remittance_address and hasattr(remittance_address, 'content'):
            invoice_info["Remittance Address"] = remittance_address.content

        remittance_address_recipient = invoice.fields.get("RemittanceAddressRecipient")
        if remittance_address_recipient and hasattr(remittance_address_recipient, 'content'):
            invoice_info["Remittance Address Recipient"] = remittance_address_recipient.content

        # Process Items as a table

        # items_field = invoice.fields.get("Items")
        # if items_field:
        #         print("Items:")
        #         print(items_field)
        #         print("--------------------------------------------------")


        
        # Process Items as a table
        items_field = invoice.fields.get("Items")
        if items_field and items_field.value is not None:
            table_data = {
                "table_number": 1,
                "cells": []
            }

            # Add header row
            headers = ["Item", "Description", "Product Code", "Quantity", "Unit Price", "Amount"]
            for col_idx, header in enumerate(headers):
                table_data["cells"].append({
                    "row_index": 0,
                    "column_index": col_idx,
                    "content": header
                })

            # Add data rows
            for row_idx, item in enumerate(items_field.value, 1):
                # Access the item dictionary directly (no need for .value here)
                item_dict = item.value if hasattr(item, 'value') else {}

                # Get field contents with safer access
                description = item_dict.get("Description", {}).content if item_dict.get("Description") else "N/A"
                product_code = item_dict.get("ProductCode", {}).content if item_dict.get("ProductCode") else "N/A"
                quantity = item_dict.get("Quantity", {}).content if item_dict.get("Quantity") else "N/A"
                unit_price = item_dict.get("UnitPrice", {}).content if item_dict.get("UnitPrice") else "N/A"
                amount = item_dict.get("Amount", {}).content if item_dict.get("Amount") else "N/A"

                # Create row data
                values = [
                    f"Item {row_idx}",  # or use actual item number if available
                    description,
                    product_code,
                    quantity,
                    unit_price,
                    amount
                ]

                for col_idx, value in enumerate(values):
                    table_data["cells"].append({
                        "row_index": row_idx,
                        "column_index": col_idx,
                        "content": str(value)
                    })

            invoice_info["tables"] = [table_data]

        results.append(invoice_info)

    return results

\
def awb_data(results, bill_data):
    for idx, doc in enumerate(bill_data.documents):
        doc_data = {}

        shipping_address = doc.fields.get('shipping_address')
        if shipping_address.value is not None:
            doc_data["Shipping Address"] = shipping_address.value

        consignee_name = doc.fields.get('consignee_name')
        if consignee_name.value is not None:
            doc_data["Consignee Name"] = consignee_name.value

        shipper_name = doc.fields.get('shipper_name')
        if shipper_name.value is not None:
            doc_data["Shipper Name"] = shipper_name.value

        consignee_address = doc.fields.get('consignee_address')
        if consignee_address.value is not None:
            doc_data["Consignee Address"] = consignee_address.value

        airway_bill_number = doc.fields.get('airway_bill_number')
        if airway_bill_number.value is not None:
            doc_data["Airway Bill Number"] = airway_bill_number.value

        issuer = doc.fields.get('Issuer')
        if issuer.value is not None:
            doc_data["Issuer"] = issuer.value

        total_weight = doc.fields.get('total_weight')
        if total_weight.value is not None:
            doc_data["Total Weight"] = total_weight.value

        execution_date = doc.fields.get('execution_date')
        if execution_date.value is not None:
            doc_data["Execution Date"] = execution_date.value

        total_bill = doc.fields.get('total_bill')
        if total_bill.value is not None:
            doc_data["Total Bill"] = total_bill.value

        currency = doc.fields.get('currency')
        if currency.value is not None:
            doc_data["Currency"] = currency.value

        departure_airport = doc.fields.get('departure_airport')
        if departure_airport.value is not None:
            doc_data["Departure Airport"] = departure_airport.value

        destination_airport = doc.fields.get('destination_airport')
        if destination_airport.value is not None:
            doc_data["Destination Airport"] = destination_airport.value

        shipper_account_number = doc.fields.get('Shipper_account_number')
        if shipper_account_number.value is not None:
            doc_data["Shipper Account Number"] = shipper_account_number.value
        results.append(doc_data)
    return results

# def renuka_data(results, bill_data):
#     for idx, doc in enumerate(bill_data.documents):
#         doc_data = {}

#         invoice_no = doc.fields.get("Invoice Number")
#         if invoice_no and invoice_no.value is not None:
#             doc_data["Invoice Number"] = invoice_no.value

#         gstin = doc.fields.get("GSTIN")
#         if gstin and gstin.value is not None:
#             doc_data["GSTIN"] = gstin.value

#         vendor_name = doc.fields.get("Vendor Name")
#         if vendor_name and vendor_name.value is not None:
#             doc_data["Vendor Name"] = vendor_name.value

#         description = doc.fields.get("Description")
#         if description and description.value is not None:
#             doc_data["Description"] = description.value

#         date = doc.fields.get("Invoice Date")
#         if date and date.value is not None:
#             doc_data["Invoice Date"] = date.value

#         total_amount = doc.fields.get("Total Amount (In Ruppees)")
#         if total_amount and total_amount.value is not None:
#             doc_data["Total Amount (In Ruppees)"] = total_amount.value

#         list_items = doc.fields.get("List Items")
#         if list_items and list_items.value is not None:
#             # Print table header
#             print("| # | Description of Goods | Qty | Weight | Rate | Amount |")
#             print("|---|---|---|---|---|---|")

#             for i, item in enumerate(list_items.value, 1):
#                 desc = item.value.get("Description of Goods")
#                 qty = item.value.get("Qty.")
#                 weight = item.value.get("Weight")
#                 rate = item.value.get("Rate")
#                 amount = item.value.get("Amount")

#                 # Get the values or empty string if None
#                 desc_val = desc.value if desc and desc.value is not None else ""
#                 qty_val = qty.value if qty and qty.value is not None else ""
#                 weight_val = weight.value if weight and weight.value is not None else ""
#                 rate_val = rate.value if rate and rate.value is not None else ""
#                 amount_val = amount.value if amount and amount.value is not None else ""

#                 # Print each row
#                 print(f"| {i} | {desc_val} | {qty_val} | {weight_val} | {rate_val} | {amount_val} |")



#         results.append(doc_data)
#         # print(results)

#     return results
def renuka_data(results, bill_data):
    for idx, doc in enumerate(bill_data.documents):
        doc_data = {}

        # Extract basic fields
        invoice_no = doc.fields.get("Invoice Number")
        if invoice_no and invoice_no.value is not None:
            doc_data["Invoice Number"] = invoice_no.value

        gstin = doc.fields.get("GSTIN")
        if gstin and gstin.value is not None:
            doc_data["GSTIN"] = gstin.value

        vendor_name = doc.fields.get("Vendor Name")
        if vendor_name and vendor_name.value is not None:
            doc_data["Vendor Name"] = vendor_name.value

        description = doc.fields.get("Description")
        if description and description.value is not None:
            doc_data["Description"] = description.value

        date = doc.fields.get("Invoice Date")
        if date and date.value is not None:
            doc_data["Invoice Date"] = date.value

        total_amount = doc.fields.get("Total Amount (In Ruppees)")
        if total_amount and total_amount.value is not None:
            doc_data["Total Amount (In Ruppees)"] = total_amount.value

        # Process List Items as a table
        list_items = doc.fields.get("List Items")
        if list_items and list_items.value is not None:
            table_data = {
                "table_number": 1,
                "cells": []
            }

            # Add header row
            headers = ["SL No", "Description of Goods", "Qty", "Weight", "Rate", "Amount"]
            for col_idx, header in enumerate(headers):
                table_data["cells"].append({
                    "row_index": 0,
                    "column_index": col_idx,
                    "content": header
                })

            # Add data rows
            for row_idx, item in enumerate(list_items.value, 1):
                desc = item.value.get("Description of Goods")
                qty = item.value.get("Qty.")
                weight = item.value.get("Weight")
                rate = item.value.get("Rate")
                amount = item.value.get("Amount")

                # Get values or empty string if None
                values = [
                    str(row_idx),
                    desc.value if desc and desc.value is not None else "",
                    qty.value if qty and qty.value is not None else "",
                    weight.value if weight and weight.value is not None else "",
                    rate.value if rate and rate.value is not None else "",
                    amount.value if amount and amount.value is not None else ""
                ]

                for col_idx, value in enumerate(values):
                    table_data["cells"].append({
                        "row_index": row_idx,
                        "column_index": col_idx,
                        "content": value
                    })

            doc_data["tables"] = [table_data]

        results.append(doc_data)

    return results
def packing_data(results, bill_data):
    for idx, doc in enumerate(bill_data.documents):
        doc_data = {}

        vendor_address = doc.fields.get('VendorAddress')
        if vendor_address.value is not None:
            doc_data["Vendor Address"] = vendor_address.value

        billing_address = doc.fields.get('BillingAddress')
        if billing_address.value is not None:
            doc_data["Billing Address"] = billing_address.value

        shipping_address = doc.fields.get('ShippingAddress')
        if shipping_address.value is not None:
            doc_data["Shipping Address"] = shipping_address.value

        vendor_name = doc.fields.get('VendorName')
        if vendor_name.value is not None:
            doc_data["Vendor Name"] = vendor_name.value

        invoice_date = doc.fields.get('InvoiceDate')
        if invoice_date.value is not None:
            doc_data["Invoice Date"] = invoice_date.value

        customer_name = doc.fields.get('CustomerName')
        if customer_name.value is not None:
            doc_data["Customer Name"] = customer_name.value

        shipping_date = doc.fields.get('shipping_date')
        if shipping_date.value is not None:
            doc_data["Shipping Date"] = shipping_date.value

        customer_email = doc.fields.get('customer_email')
        if customer_email.value is not None:
            doc_data["Customer Email"] = customer_email.value

        order_no = doc.fields.get('OrderNo')
        if order_no.value is not None:
            doc_data["Order Number"] = order_no.value

    results.append(doc_data)
    return results