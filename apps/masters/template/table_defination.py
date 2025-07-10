import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image  

from apps.company.models import Companies

def doc_heading(file_path, doc_header, sub_header):
    elements = []

    # Custom page size (11 inches wide, 10.5 inches high)
    page_width = 11 * inch
    page_height = 16 * inch

    # Create the PDF document
    doc = SimpleDocTemplate(file_path, pagesize=(page_width, page_height))
    
    # Get the default styles
    styles = getSampleStyleSheet()
    
    def main_heading(doc_header):
        # Modify the heading style to be bold
        style_heading = ParagraphStyle(
            name='Heading1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',  # Set font to Helvetica-Bold to make it bold
            fontSize=16,                # You can adjust the font size if needed
            spaceAfter=3,              # Adjust space after heading if needed
            alignment=1,                # Center align the text (0=left, 1=center, 2=right)
        )
        
        # Add a bold heading
        elements.append(Paragraph(doc_header, style_heading))

    # if doc_header == "SALES ORDER":
    #     main_heading(doc_header)
    # Match exact header text (all uppercase as shown in your image)
    if doc_header.upper() == "SALES ORDER" or doc_header.upper() == "SALES QUOTATION":
        main_heading(doc_header.upper())  # Force uppercase to match your style
        
    elif doc_header == "TAX INVOICE":
        main_heading(doc_header)
        # Modify the heading style to be bold
        sub_style_heading = ParagraphStyle(
        name='Heading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',  # Set font to Helvetica-Bold to make it bold
        fontSize=10,                # You can adjust the font size if needed
        alignment=1,                # Center align the text (0=left, 1=center, 2=right)
        )    
        # Add a bold heading
        elements.append(Paragraph(sub_header, sub_style_heading))
    elif doc_header == "Purchase Bill" or doc_header == "Purchase Return":
        # Define styles
        styles = getSampleStyleSheet()
        bold_style = ParagraphStyle(
                'BoldStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                alignment=0,  # 0 = left aligned
                textColor=colors.black
            )

        normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=12,
                alignment=0,  # 0 = left aligned
                textColor=colors.black
            )
        elements.append(Paragraph(sub_header[0], bold_style))  # Bold and capitalized text
        elements.append(Spacer(1, 2))
        elements.append(Paragraph(sub_header[1], normal_style))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph('Phone No: ' + sub_header[2] + ' | ' + 'Email: ' + sub_header[3], normal_style))
        # Add a spacer
        elements.append(Spacer(1, 18))

        main_heading(doc_header)

    return elements, doc


def doc_details(cust_bill_dtl, sno_lbl, sno, sdate_lbl, sdate): 
    col_widths = [3.3*inch, 3.4*inch, 3.3*inch]
    table_data_1 = [
        [cust_bill_dtl, f'{sno_lbl} : {sno}', f'{sdate_lbl} : {sdate}'],
    ]
    
    table = Table(table_data_1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def customer_details(cust_name, billing_address, phone, city):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    
    # Create structured content with bold headers
    billing_content = Paragraph(
        f"<b>{cust_name}</b>"
        f"<br/>{billing_address}<br/>", 
        style_normal
    )
    
    shipping_content = Paragraph(
        f"<b>Mobile: {phone}</b><br/>"
        f"Destination: {city}", 
        style_normal
    )
    
    table_data = [
        [billing_content, shipping_content]
    ]
    
    table_col_widths = [6.7*inch, 3.3*inch]
    
    table = Table(table_data, colWidths=table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def format_numeric(cell):
    try:
        return "{:.2f}".format(float(cell))
    except (ValueError, TypeError):
        return str(cell)

def product_details(data, show_gst=True):
    style_normal = getSampleStyleSheet()['Normal']

    tbl_3_col_widths = [
        0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch,
        1.0 * inch, 1.0 * inch, 0.7 * inch, 0.8 * inch
    ]

    table_3_heading = [["Idx", "Product", "Boxes", "Qty", "Unit Name", "Rate", "Amount", "Disc(%)", "Disc(Rs)"]]

    if show_gst:
        table_3_heading[0].append("GST(Rs)")
        table_3_heading[0].append("Total Amount")
        tbl_3_col_widths += [0.8 * inch, 1.0 * inch]
    else:
        table_3_heading[0].append("Total Amount")
        tbl_3_col_widths += [1.0 * inch]

    for index, item in enumerate(data):
        if len(item) < 11:
            continue

        row = item[:9]  # First 9 fields are common

        if show_gst:
            row.append(format_numeric(item[9]))  # GST(Rs)
            row.append(format_numeric(item[10]))  # Total Amount
        else:
            row.append(format_numeric(item[10]))  # Total Amount (shift left)

        wrapped_row = [Paragraph(str(cell), style_normal) for cell in row]
        table_3_heading.append(wrapped_row)

    # Ensure minimum rows for spacing
    while len(table_3_heading) < 6:
        table_3_heading.append([" "] * len(table_3_heading[0]))

    table = Table(table_3_heading, colWidths=tbl_3_col_widths)
    # table = Table(table_3_heading, colWidths=tbl_3_col_widths)
    table.setStyle(TableStyle([
        # Basic styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Alignment
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numeric columns right-aligned
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),    # Text columns left-aligned
        
        # Vertical lines
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),  
        ('LINEAFTER', (6, 0), (10, -1), 1, colors.black),   
        
        # Horizontal lines
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),  # Header top
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header bottom
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Last row
        
        # Increase row padding for spacing
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    return table


# def product_total_details(ttl_Qty, final_Amount, ttl_Amount,total_disc):
#     table_4_col_widths = [
#         0.5 * inch,   # Idx
#         2.0 * inch,   # Product
#         0.7 * inch,   # Boxes
#         0.7 * inch,   # Qty
#         0.8 * inch,   # Unit Name
#         1.0 * inch,   # Rate
#         1.0 * inch,   # Amount
#         0.7 * inch,   # Dis(%)
#         0.8 * inch,   # Disc(Rs)
#         0.8 * inch,    # Total Amount
#         1.0 * inch    # Total Amount
#     ]

#     # table_4_col_widths = [0.7 * inch, 3.5 * inch, 0.8 * inch, 1.1 * inch, 1.4 * inch, 1.3 * inch, 1.2 * inch]
#     # table_4_heading = [[' ','Total',ttl_Qty,' ',' ',ttl_Amount, total_disc]]
#     table_4_heading = [[
#         '',            # Idx
#         'Total',       # Product
#         '',            # Boxes
#         ttl_Qty,       # Qty
#         '',            # Unit Name
#         '',            # Rate
#         final_Amount,    # Amount
#         '',            # Dis(%)
#         total_disc,    # Disc(Rs)
#         '',
#         ttl_Amount     # Total Amount
#     ]]
    
#     table = Table(table_4_heading, colWidths=table_4_col_widths)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#         ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
#         ('VALIGN', (0, 1), (-1, -1), 'TOP'),
#         ('GRID', (0, 0), (-1, 0), 1, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0, colors.black),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#     ]))
#     return table
def product_total_details(ttl_Qty, final_Amount, ttl_Amount, total_disc, show_gst=False):
    if show_gst:
        print("Entered with show_gst")
        col_widths = [
            0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch,
            0.8 * inch, 0.8 * inch, 1.0 * inch
        ]
        row = [
            '', 'Total', '', ttl_Qty, '', '', final_Amount,
            '', total_disc, '', ttl_Amount
        ]
    else:
        print("Entered with out show_gst")
        col_widths = [
            0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch  # One less column
        ]
        row = [
            '', 'Total', '', ttl_Qty, '', '', final_Amount,
            '', total_disc, ttl_Amount
        ]

    table = Table([row], colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def product_total_details_purchase(ttl_Qty, final_Amount, total_disc, ttl_Amount, show_gst=False):
    if show_gst:
        print("Entered with show_gst")
        col_widths = [
            0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch,
            0.8 * inch, 0.8 * inch, 1.0 * inch
        ]
        row = [
            '', 'Total', '', ttl_Qty, '', '', final_Amount,
            '', total_disc, '', ttl_Amount
        ]
    else:
        print("Entered with out show_gst")
        col_widths = [
            0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch  # One less column
        ]
        row = [
            '', 'Total', '', ttl_Qty, '', '', final_Amount,
            '', total_disc, ttl_Amount
        ]

    table = Table([row], colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table



def product_total_details_inwords(
    Bill_Amount_In_Words, SubTotal, Discount_Amt,
    total_cgst, total_sgst, total_igst, cess_amount,
    round_off, Party_Old_Balance, net_lbl, net_value,
    tax_type='Exclusive'
):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bill_amount_paragraph = Paragraph(f"<b>Bill Amount In Words:</b> {Bill_Amount_In_Words}", normal_style)

    financials_data = [
        [Paragraph("<b>Sub Total:</b>", normal_style), Paragraph(f"<b>{SubTotal}</b>", normal_style)],
        [Paragraph("<b>Total Discount:</b>", normal_style), Paragraph(f"<b>-{Discount_Amt}</b>", normal_style)]
    ]

    # Show only if tax_type is not 'Inclusive'
    if tax_type != 'Inclusive':
        if total_igst > 0:
            financials_data.append([Paragraph("<b>IGST:</b>", normal_style), Paragraph(f"<b>{total_igst}</b>", normal_style)])
        elif total_cgst > 0 and total_sgst > 0:
            financials_data.append([Paragraph("<b>CGST:</b>", normal_style), Paragraph(f"<b>{total_cgst}</b>", normal_style)])
            financials_data.append([Paragraph("<b>SGST:</b>", normal_style), Paragraph(f"<b>{total_sgst}</b>", normal_style)])

    financials_data.extend([
        [Paragraph("<b>Cess AMT:</b>", normal_style), Paragraph(f"<b>{cess_amount}</b>", normal_style)],
        [Paragraph("<b>Round Off:</b>", normal_style), Paragraph(f"<b>{round_off}</b>", normal_style)],
        [Paragraph("<b>Party Old Balance:</b>", normal_style), Paragraph(f"<b>{Party_Old_Balance}</b>", normal_style)],
        [Paragraph(f"<b>{net_lbl}:</b>", normal_style), Paragraph(f"<b>{net_value}</b>", normal_style)]
    ])

    financials_table = Table(financials_data, colWidths=[2.0 * inch, 1.3 * inch])
    financials_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),  # Party Old Balance in Bold
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Net Total in Bold
        ('BOTTOMPADDING', (0, -2), (-1, -1), 5),
        ('TOPPADDING', (0, -2), (-1, -1), 5),
    ]))

    # Combine bill amount and financials
    table_data = [
        [bill_amount_paragraph, financials_table]
    ]

    # Main Table
    table = Table(table_data, colWidths=[6.7 * inch, 3.3 * inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
    ]))

    return table



def declaration():
    table_data_6 = [['Declaration:' '\n' 'We declare that this invoice shows the actual price of the goods/services' '\n' 'described and that all particulars are true and correct.' '\n' 'Original For Recipient', 'Authorised Signatory']]
    table_6_col_widths = [6.7*inch, 3.3*inch]
    
    table = Table(table_data_6, colWidths=table_6_col_widths)
    table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color for the entire table
    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),   # Text color for the entire table
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),              # Left align all cells
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),              # Top align all cells
    ('ALIGN', (1, 0), (1, 0), 'CENTER'),              # Center align text in the second column header cell
    ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),             # Bottom align text in the second column header cell
    
    # Add border around header cells
    ('GRID', (0, 0), (-1, 0), 1, colors.black),  # Add border around the header row
    
    # Optional: Additional styling
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),  # Font for the header row
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),       # Padding for the header row
    ]))
    return table


#====PURCHASE ORDER RELATED TBL
def shipping_details(destination, tax_type,  shipping_mode_name, port_of_landing, port_of_discharge, sdate):
    style_normal = getSampleStyleSheet()['Normal']
    shipping_details_table_data = [[f"Destination: {destination} \nShipping Mode :{shipping_mode_name} \nPort of Loading: {port_of_landing}  \nPort of Discharge: {port_of_discharge}",f"Tax Preference: {tax_type} \nRef Date : {sdate}  \n   \n   \n "]]
    shipping_details_table_col_widths = [5*inch, 5*inch]
    
    table = Table(shipping_details_table_data, colWidths=shipping_details_table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table


def vendor_details(customer_name, v_billing_address, v_shipping_address_lbl, v_shipping_address):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']   

    # Create Paragraph objects for each cell with proper HTML-like tags
    cust_bill_paragraph = Paragraph(f"<b>{customer_name}</b><br/>{v_billing_address}<br/>", normal_style)
    cust_ship_paragraph = Paragraph(f"<b>{v_shipping_address_lbl}</b><br/>{v_shipping_address}<br/>", normal_style)
    # Table data with Paragraph objects
    vendor_table_data_2 = [
        [cust_bill_paragraph, cust_ship_paragraph]
    ]

    table_2_col_widths = [5*inch, 5*inch]
    
    table = Table(vendor_table_data_2, colWidths=table_2_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def narration_and_total(comp_name, sdate, total_sub_amt, total_bill_amt):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']   

    # Create Paragraph objects for each cell with proper HTML-like tags
    narration_paragraph = Paragraph(f"<b>Narration :</b> Being Goods Purchase From {comp_name }  { sdate}", normal_style)
    total_paragraph = Paragraph(f"<b> Sub Total : {total_sub_amt}<br/>Bill Total : {total_bill_amt}<br/> </b>", normal_style)
    # Table data with Paragraph objects
    vendor_table_data_2 = [
        [narration_paragraph, total_paragraph]
    ]

    narration_and_total_table_col_widths = [5*inch, 5*inch]
    
    table = Table(vendor_table_data_2, colWidths=narration_and_total_table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def logistics_info(shipping_company_name, shipping_tracking_no , vehicle_vessel, no_of_packets, shipping_date, shipping_charges, weight):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']   

    # Create Paragraph objects for each cell with proper HTML-like tags
    logistics_info  = Paragraph(f"<b>Logistics Info : </b> <br/> <br/> Shipping Company  : {shipping_company_name} <br/> Tracking No: {shipping_tracking_no} <br/> Vehicle/Vessel No. : {vehicle_vessel}  <br/> No of Packets: {no_of_packets}", normal_style)
    doc_extra_info = Paragraph(f"<b> Document extra info :</b> <br/> <br/> Shipping Date : {shipping_date} <br/> Charges Paid  {shipping_charges} <br/> Weight : {weight}", normal_style)
    # Table data with Paragraph objects
    logistics_info_table_data = [
        [logistics_info, doc_extra_info]
    ]

    logistics_info_table_col_widths = [5*inch, 5*inch]
    
    table = Table(logistics_info_table_data, colWidths = logistics_info_table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def purchase_declaration(comp_name):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    table_data_6 = [[f"For {comp_name}  \n\n\n\n  Authorised Signatory"]]
    table_6_col_widths = [10*inch]
    
    table = Table(table_data_6, colWidths=table_6_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color for the entire table
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),   # Text color for the entire table
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),             # Right align all cells
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),              # Top align all cells
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'), # Use bold font for all text
        ('FONTSIZE', (0, 0), (-1, -1), 10),               # Set font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),      # Add border around all cells
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),          # Padding for all cells
    ]))
    return table

def comp_address_last_tbl(comp_address, comp_phone, comp_email):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    comp_address_last_tbl_data_ = [[f"{comp_address}  {comp_phone}  {comp_email}"]]
    comp_address_last_tbl_data__col_widths = [10*inch]
    
    table = Table(comp_address_last_tbl_data_, colWidths=comp_address_last_tbl_data__col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color for the entire table
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),   # Text color for the entire table
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),             # CENTER align all cells
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),              # Top align all cells
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'), # Use bold font for all text
        ('FONTSIZE', (0, 0), (-1, -1), 8),               # Set font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),      # Add border around all cells
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),          # Padding for all cells
    ]))
    return table

#Sale invoice logics ....
# def invoice_doc_details(company_logo, company_name, company_gst, company_address, company_phone, company_email, sno_lbl, sno, sdate_lbl, sdate): 
#     styles = getSampleStyleSheet()
#     style_normal = styles['Normal']
#     style_bold = styles['Heading4']

#     image_filename = "company_1_1afdb5.jpg"
#     media_folder = r"C:/Users/Pramod Kumar/CNL_Backend/document_format/cnl-backend/media/doc_generater"
#     image_path = os.path.join(media_folder, image_filename)

#     # Check if image exists
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"Image file not found: {image_path}")

#     # Create an image object
#     company_logo = Image(image_path, width=60, height=60)

#     # Define company details as a Paragraph
#     company_details_content = Paragraph(
#         f"<b>{company_name}</b><br/>"
#         f"<b>GSTIN: {company_gst}</b><br/>"
#         f"{company_address}<br/>"
#         f"<b>Mobile:</b> {company_phone}<br/>"
#         f"<b>Email:</b> {company_email}",
#         style_normal
#     )

#     # Create a table with two columns: [Logo, Company Details]
#     col_widths = [1.2*inch, 3.8*inch, 2.5*inch, 2.5*inch]  # Adjust width for better spacing

#     table_data_1 = [
#         [company_logo, company_details_content, f'{sno_lbl} : \n{sno}', f'{sdate_lbl} : \n{sdate}']
#     ]
    
#     table = Table(table_data_1, colWidths=col_widths)
#     table.setStyle(TableStyle([
        
#         ('BACKGROUND', (0, 0), (-1, 0), colors.white),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#         ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#         ('GRID', (2, 0), (-1, 0), 1, colors.black),  # Only add grid for Invoice No. and Invoice Date
#         ('BOX', (0, 0), (-1, 0), 1, colors.black),  # Full outer border
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#     ]))
    
#     return table

def invoice_doc_details(company_logo, company_name, company_gst, company_address, company_phone, company_email, sno_lbl, sno, sdate_lbl, sdate): 
    from reportlab.platypus import Image, Paragraph, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    import os

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_bold = styles['Heading4']

    # Check if image path is valid
    # if not os.path.exists(company_logo):
    #     raise FileNotFoundError(f"Company logo file not found: {company_logo}")

    # # Create an image object from the provided dynamic path
    # company_logo = Image(company_logo, width=60, height=60)
    
    # ✅ Validate and convert path string to Image object
    if company_logo and os.path.exists(company_logo):
        company_logo = Image(company_logo, width=80, height=80)
    else:
        # Fallback to empty space or a default image
        company_logo = Paragraph("<b>No Logo</b>", getSampleStyleSheet()['Normal'])

    # Define company details as a Paragraph
    company_details_content = Paragraph(
        f"<b>{company_name}</b><br/>"
        f"<b>GSTIN: {company_gst}</b><br/>"
        f"{company_address}<br/>"
        f"<b>Mobile:</b> {company_phone}<br/>"
        f"<b>Email:</b> {company_email}",
        style_normal
    )

    # Table layout
    col_widths = [1.2*inch, 3.8*inch, 2.5*inch, 2.5*inch]

    table_data_1 = [
        [company_logo, company_details_content, f'{sno_lbl} : \n{sno}', f'{sdate_lbl} : \n{sdate}']
    ]

    table = Table(table_data_1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (2, 0), (-1, 0), 1, colors.black),
        ('BOX', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))

    return table




def invoice_customer_details(cust_name, city, country, phone, destination, shipping_address, billing_address):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    # style_bold = styles['Normal']
    # style_bold.fontName = 'Helvetica-Bold'
    
    # Create structured content with bold headers
    billing_content = Paragraph(
        f"<b>Customer Details: </b><br/>{cust_name}<br/>"
        f"<b>Billing Address:</b><br/>{billing_address}", 
        style_normal
    )
    
    shipping_content = Paragraph(
        f"<b>Shipping Address:</b><br/>{shipping_address}", 
        style_normal
    )
    
    table_data = [
        [billing_content, shipping_content]
    ]
    
    table_col_widths = [5*inch, 5*inch]
    
    table = Table(table_data, colWidths=table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    return table

# def invoice_product_details(data, show_gst=True):
    
#     style_normal = getSampleStyleSheet()['Normal']

#     tbl_3_col_widths = [
#         0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch,
#         1.0 * inch, 1.0 * inch, 0.7 * inch, 0.8 * inch
#     ]

#     table_3_heading = [["Idx", "Product", "Boxes", "Qty", "Unit Name", "Rate", "Amount", "Disc(%)", "Disc(Rs)"]]

#     if show_gst:
#         table_3_heading[0].append("GST(Rs)")
#         table_3_heading[0].append("Total Amount")
#         tbl_3_col_widths += [0.8 * inch, 1.0 * inch]
#     else:
#         table_3_heading[0].append("Total Amount")
#         tbl_3_col_widths += [1.0 * inch]

#     for index, item in enumerate(data):
#         if len(item) < 11:
#             continue

#         row = item[:9]  # First 9 fields are common

#         if show_gst:
#             row.append(format_numeric(item[9]))  # GST(Rs)
#             row.append(format_numeric(item[10]))  # Total Amount
#         else:
#             row.append(format_numeric(item[10]))  # Total Amount (shift left)

#         wrapped_row = [Paragraph(str(cell), style_normal) for cell in row]
#         table_3_heading.append(wrapped_row)

#     # Ensure minimum rows for spacing
#     while len(table_3_heading) < 6:
#         table_3_heading.append([" "] * len(table_3_heading[0]))

#     table = Table(table_3_heading, colWidths=tbl_3_col_widths)
#     # table = Table(table_3_heading, colWidths=tbl_3_col_widths)
#     table.setStyle(TableStyle([
#         # Basic styling
#         ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
#         # Alignment
#         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header alignment
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numeric columns right-aligned
#         ('ALIGN', (0, 1), (1, -1), 'LEFT'),    # Text columns left-aligned
        
#         # Vertical lines
#         ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),  
#         ('LINEAFTER', (6, 0), (10, -1), 1, colors.black),   
        
#         # Horizontal lines
#         ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),  # Header top
#         ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header bottom
#         ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Last row
        
#         # Increase row padding for spacing
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#         ('TOPPADDING', (0, 0), (-1, -1), 12),
#         ('LEFTPADDING', (0, 0), (-1, -1), 6),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#     ]))
    
#     return table

def invoice_product_details(data, show_gst=True):
    style_normal = getSampleStyleSheet()['Normal']

    tbl_3_col_widths = [
        0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch,
        1.0 * inch, 1.0 * inch, 0.7 * inch, 0.8 * inch
    ]

    table_3_heading = [["Idx", "Product", "Boxes", "Qty", "Unit Name", "Rate", "Amount", "Disc(%)", "Disc(Rs)"]]

    # ✅ Respect passed-in flag without overriding
    if show_gst:
        table_3_heading[0].append("GST(Rs)")
        table_3_heading[0].append("Total Amount")
        tbl_3_col_widths += [0.8 * inch, 1.0 * inch]
    else:
        table_3_heading[0].append("Total Amount")
        tbl_3_col_widths += [1.0 * inch]

    for index, item in enumerate(data):
        if len(item) < 11:
            continue

        row = item[:9]

        if show_gst:
            row.append(format_numeric(item[9]))  # GST(Rs)
            row.append(format_numeric(item[10]))  # Total Amount
        else:
            row.append(format_numeric(item[10]))  # Total Amount (shift left)

        wrapped_row = [Paragraph(str(cell), style_normal) for cell in row]
        table_3_heading.append(wrapped_row)

    # Padding
    while len(table_3_heading) < 6:
        table_3_heading.append([" "] * len(table_3_heading[0]))

    table = Table(table_3_heading, colWidths=tbl_3_col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),
        ('LINEAFTER', (6, 0), (10, -1), 1, colors.black),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    return table

    # style_normal = getSampleStyleSheet()['Normal']
    
    # # Adjusted column widths (Total = 10 inches)
    # # tbl_3_col_widths = [0.7 * inch, 3.5 * inch, 0.8 * inch, 1.1 * inch, 1.4 * inch, 1.3 * inch, 1.2 * inch]
    # tbl_3_col_widths = [
    #     0.5 * inch,   # Idx
    #     2.0 * inch,   # Product
    #     0.7 * inch,   # Boxes
    #     0.7 * inch,   # Qty
    #     0.8 * inch,   # Unit Name
    #     1.0 * inch,   # Rate
    #     1.0 * inch,   # Amount
    #     0.7 * inch,   # Dis(%)
    #     0.8 * inch,   # Disc(Rs)
    #     0.8 * inch,    # Total Amount
    #     1.0 * inch    # Total Amount
    # ]


    # table_3_heading = [["Idx", "Product", "Boxes", "Qty", "Unit Name", "Rate", "Amount", "Disc(%)", "Disc(Rs)", "GST(Rs)", "Total Amount" ]]
    
    # EXPECTED_FIELDS = 8  # Originally had 8 fields, now using only 7
    
    # for index, item in enumerate(data):
    #     if len(item) < EXPECTED_FIELDS:
    #         print(f"Skipping row {index}: Insufficient fields")
    #         continue
            
    #     row = [
    #         str(index + 1),                   # Index
    #         str(item[1]),                     # Product (force string)
    #         format_numeric(item[2]),          # Boxes
    #         str(item[3]),                     # Unit Name
    #         format_numeric(item[4]),          # Rate
    #         format_numeric(item[5]),          # Amount
    #         format_numeric(item[6]),          # Discount_percentage
    #         format_numeric(item[7]),          # Discount
    #         format_numeric(item[8]),          # Boxes
    #         format_numeric(item[9]),          # Amount
    #         format_numeric(item[10]),          # Amount
    #     ]
    #     # Convert each cell into a Paragraph with normal style
    #     wrapped_row = [Paragraph(cell, style_normal) for cell in row]
    #     table_3_heading.append(wrapped_row)
    
    # # Ensure a minimum of 5 rows for spacing
    # while len(table_3_heading) < 6:
    #     table_3_heading.append([" "] * 7)
    
    
    # table = Table(table_3_heading, colWidths=tbl_3_col_widths)
    # table.setStyle(TableStyle([
    #     # Basic styling
    #     ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
    #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
    #     # Alignment
    #     ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header alignment
    #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    #     ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numeric columns right-aligned
    #     ('ALIGN', (0, 1), (1, -1), 'LEFT'),    # Text columns left-aligned
        
    #     # Vertical lines
    #     ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),  
    #     ('LINEAFTER', (6, 0), (10, -1), 1, colors.black),   
        
    #     # Horizontal lines
    #     ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),  # Header top
    #     ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header bottom
    #     ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Last row
        
    #     # Increase row padding for spacing
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    #     ('TOPPADDING', (0, 0), (-1, -1), 12),
    #     ('LEFTPADDING', (0, 0), (-1, -1), 6),
    #     ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    # ]))
    # # style_normal = getSampleStyleSheet()['Normal']
    
    # # # Adjusted column widths (Total = 10 inches)
    # # tbl_3_col_widths = [0.7 * inch, 3.5 * inch, 0.8 * inch, 1.1 * inch, 1.4 * inch, 1.3 * inch, 1.2 * inch]
    # # table_3_heading = [["Idx", "Product", "Qty", "Unit Name", "Rate", "Amount", "Discount"]]
    
    # # EXPECTED_FIELDS = 8  # Originally had 8 fields, now using only 7
    
    # # for index, item in enumerate(data):
    # #     if len(item) < EXPECTED_FIELDS:
    # #         print(f"Skipping row {index}: Insufficient fields")
    # #         continue
            
    # #     row = [
    # #         str(index + 1),                   # Index
    # #         str(item[1]),                     # Product (force string)
    # #         format_numeric(item[2]),          # Qty
    # #         str(item[3]),                     # Unit Name
    # #         format_numeric(item[4]),          # Rate
    # #         format_numeric(item[5]),          # Amount
    # #         format_numeric(item[6])           # Discount
    # #     ]
    # #     # Convert each cell into a Paragraph with normal style
    # #     wrapped_row = [Paragraph(cell, style_normal) for cell in row]
    # #     table_3_heading.append(wrapped_row)
    
    # # # Ensure a minimum of 5 rows for spacing
    # # while len(table_3_heading) < 6:
    # #     table_3_heading.append([" "] * 7)
    
    # # table = Table(table_3_heading, colWidths=tbl_3_col_widths)
    # # table.setStyle(TableStyle([
    # #     # Basic styling
    # #     ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
    # #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    # #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    # #     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
    # #     # Alignment
    # #     ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header alignment
    # #     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    # #     ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numeric columns right-aligned
    # #     ('ALIGN', (0, 1), (1, -1), 'LEFT'),    # Text columns left-aligned
        
    # #     # Vertical lines
    # #     ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),  
    # #     ('LINEAFTER', (6, 0), (6, -1), 1, colors.black),   
        
    # #     # Horizontal lines
    # #     ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),  # Header top
    # #     ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header bottom
    # #     ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Last row
        
    # #     # Increase row padding for spacing
    # #     ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    # #     ('TOPPADDING', (0, 0), (-1, -1), 12),
    # #     ('LEFTPADDING', (0, 0), (-1, -1), 6),
    # #     ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    # # ]))
    
    # return table

def invoice_product_total_details(ttl_Qty, final_Amount, ttl_Amount, total_disc, show_gst=False):
    # table_4_col_widths = [0.7 * inch, 3.5 * inch, 0.8 * inch, 1.1 * inch, 1.4 * inch, 1.3 * inch, 1.2 * inch]
    # table_4_heading = [[' ','Total',ttl_Qty,' ',' ',ttl_Amount, total_disc]]
    
    # table = Table(table_4_heading, colWidths=table_4_col_widths)
    # table.setStyle(TableStyle([
    #     ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
    #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    #     ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    #     ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    #     ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
    #     ('VALIGN', (0, 1), (-1, -1), 'TOP'),
    #     ('GRID', (0, 0), (-1, 0), 1, colors.black),
    #     ('BOX', (0, 0), (-1, -1), 0, colors.black),
    #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    #     ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    # ]))
    # return table
    
    if show_gst:
        print("Entered with show_gst")
        col_widths = [
            0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch,
            0.8 * inch, 0.8 * inch, 1.0 * inch
        ]
        row = [
            '', 'Total', '', ttl_Qty, '', '', final_Amount,
            '', total_disc, '', ttl_Amount
        ]
    else:
        print("Entered with out show_gst")
        col_widths = [
            0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch,
            0.8 * inch, 1.0 * inch  # One less column
        ]
        row = [
            '', 'Total', '', ttl_Qty, '', '', final_Amount,
            '', total_disc, ttl_Amount
        ]

    table = Table([row], colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def create_footer_section(bank_name, bank_acno, bank_ifsc, bank_branch):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    
    # --- Top Row: Bank Details + Signature ---
    bank_content = Paragraph(
        f"<b>Bank Details:</b><br/>"
        f"Bank: <b>{bank_name}</b><br/>"
        f"Account #:<b>{bank_acno}</b><br/>"
        f"IFSC:<b>{bank_ifsc}</b><br/>"
        f"Branch:<b>{bank_branch}</b><br/>",
        style_normal
    )
    
    signature_content = Paragraph(
        "<br/><br/><br/>"  # Spacer for alignment
        "<b>Authorized Signature</b>",
        style_normal
    )
    
    # --- Bottom Row: Notes + Terms ---
    notes_content = Paragraph(
        "<b>Notes:</b><br/>"
        "Thank you for the Business",
        style_normal
    )
    
    terms_content = Paragraph(
        "<b>Terms and Conditions:</b><br/>"
        "1. Goods once sold cannot be taken back<br/>"
        "2. Warranty per manufacturer terms<br/>"
        "3. 24% p.a. interest after 15 days<br/>"
        "4. Subject to local Jurisdiction",
        style_normal
    )
    
    # Column widths (equal columns)
    col_widths = [6.1*inch, 3.9*inch]
    
    # Create the table structure
    table_data = [
        [bank_content, signature_content],  # Row 1
        [notes_content, terms_content]      # Row 2
    ]
    
    table = Table(table_data, colWidths=col_widths, rowHeights=[2*inch, 1.2*inch])
    
    table.setStyle(TableStyle([
        # Basic styling
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        
        # Borders
        ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Outer border
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),  # Vertical line
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Horizontal after bank
        
        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Center signature
        ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),
        
        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    return table

# Sale returns logic ...

def return_company_header(company_name, company_address, company_phone):
    styles = getSampleStyleSheet()
    
    # Style for company name (bold and centered)
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,  # 1 = Center
        spaceAfter=6
    )
    
    # Style for address/phone (normal and centered)
    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=2
    )
    
    # Build content
    content = [
        Paragraph(f"<b>{company_name}</b>", company_style),
        Paragraph(company_address, address_style),
        Paragraph(f"Phone No: {company_phone}", address_style),
        Spacer(1, 12),  # Add space before "BILL OF SUPPLY"
        # Paragraph("<b>BILL OF SUPPLY</b>", company_style),  # Subheader
        Spacer(1, 12)   # Space after header
    ]
    
    return content

def return_doc_details(cust_bill_dtl, sno_lbl, sno, sdate_lbl, sdate): 
    col_widths = [3.3*inch, 2.8*inch, 3.9*inch]
    table_data = [
        [cust_bill_dtl, f'{sno_lbl} : {sno}', f'{sdate_lbl} : {sdate}'],
    ]
    
    
    
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def return_customer_details(cust_name, billing_address, phone, city):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    
    content = Paragraph(
        f"<b>{cust_name}</b><br/>"
        f"{billing_address}<br/>"
        f"Phone: {phone}<br/>"
        f"Destination: {city}", 
        style_normal
    )
    
    table_data = [[content]]
    table = Table(table_data, colWidths=[10*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return table

# def return_product_details(data):
#     styles = getSampleStyleSheet()
#     style_normal = styles['Normal']
    
#     # Column widths (match financial section)
#     col_widths = [4.5*inch, 1.5*inch, 1.5*inch, 2.5*inch]
    
#     # Table data with headers and products
#     table_data = [
#         [Paragraph("<b>Description</b>", style_normal),
#          Paragraph("<b>Qty</b>", style_normal),
#          Paragraph("<b>MRP</b>", style_normal),
#          Paragraph("<b>Amount</b>", style_normal)]
#     ]
    
#     # Add product rows
#     for item in data:
#         table_data.append([
#             Paragraph(str(item[1])),  # Description
#             Paragraph(format_numeric(item[2])),  # Qty
#             Paragraph(format_numeric(item[4])),  # MRP
#             Paragraph(format_numeric(item[5]))   # Amount
#         ])
    
#     # Add empty rows for spacing (optional)
#     for _ in range(4 - len(data)):
#         table_data.append(["", "", "", ""])
    
#     return table_data

# def return_complete_table(data, total_qty, sub_total, discount_amt, cess_amount,
#                           total_cgst, total_sgst, total_igst, round_0ff, bill_total,
#                           amount_in_words, show_gst=None):
#     styles = getSampleStyleSheet()
#     normal_style = styles['Normal']

#     # Column widths
#     col_widths = [4.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch]

#     # Table data with headers
#     table_data = [
#         [
#             Paragraph("<b>Description</b>", normal_style),
#             Paragraph("<b>Qty</b>", normal_style),
#             Paragraph("<b>MRP</b>", normal_style),
#             Paragraph("<b>Amount</b>", normal_style),
#             Paragraph("<b>Discount</b>", normal_style)
#         ]
#     ]

#     # Add product rows
#     for item in data:
#         table_data.append([
#             Paragraph(str(item[1])),                # Description
#             Paragraph(format_numeric(item[3])),     # Qty
#             Paragraph(format_numeric(item[5])),     # MRP
#             Paragraph(format_numeric(item[6])),     # Amount
#             Paragraph(format_numeric(item[8]))      # Discount
#         ])

#     # Add empty rows if less than 4 products
#     while len(table_data) < 5:
#         table_data.append(["", "", "", "", ""])

#     # Add financial summary rows
#     table_data.extend([
#         ["Total Quantity", "", "", "", total_qty],
#         ["Sub Total", "", "", "", sub_total],
#         ["Total Discount", "", "", "", f"-{discount_amt}"],
#         ["Cess Amt", "", "", "", f"{cess_amount}"]
#     ])

#     # Conditionally add tax rows based on tax_type
#     if show_gst == 'cnl-ex-sale-order':
#         if float(total_igst) > 0:
#             table_data.append(["IGST", "", "", "", f"{total_igst}"])
#         else:
#             if float(total_cgst) > 0:
#                 table_data.append(["CGST", "", "", "", f"{total_cgst}"])
#             if float(total_sgst) > 0:
#                 table_data.append(["SGST", "", "", "", f"{total_sgst}"])

#     # Continue with remaining rows
#     table_data.extend([
#         ["Round Off", "", "", "", round_0ff],
#         ["Bill Total", "", "", "", bill_total],
#         [Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", normal_style), "", "", "", ""]
#     ])

#     # Create table
#     table = Table(table_data, colWidths=col_widths)

#     # Apply styling
#     table.setStyle(TableStyle([
#         ('BOX', (0, 0), (-1, -1), 1, colors.black),
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),  # Above Total
#         ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),                    # Above Bill Total
#         ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.grey),                   # Above Amount in Words
#         ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
#         ('SPAN', (0, -1), (-1, -1)),  # Amount in words
#         ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
#         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
#     ]))

#     return table

def return_complete_table(data, total_qty, sub_total, discount_amt, cess_amount,
                          total_cgst, total_sgst, total_igst, round_0ff, bill_total,
                          amount_in_words, show_gst=False):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Column widths
    col_widths = [4.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch]

    # Table header
    table_data = [[
        Paragraph("<b>Description</b>", normal_style),
        Paragraph("<b>Qty</b>", normal_style),
        Paragraph("<b>MRP</b>", normal_style),
        Paragraph("<b>Amount</b>", normal_style),
        Paragraph("<b>Discount</b>", normal_style)
    ]]

    # Add product rows
    for item in data:
        table_data.append([
            Paragraph(str(item[1])),                  # Description
            Paragraph(format_numeric(item[3])),       # Qty
            Paragraph(format_numeric(item[5])),       # MRP
            Paragraph(format_numeric(item[6])),       # Amount
            Paragraph(format_numeric(item[8]))        # Discount
        ])

    # Fill with empty rows if less than 4 items (for layout consistency)
    while len(table_data) < 5:
        table_data.append(["", "", "", "", ""])

    # Add financial rows
    table_data.extend([
        ["Total Quantity", "", "", "", format_numeric(total_qty)],
        ["Sub Total", "", "", "", format_numeric(sub_total)],
        ["Total Discount", "", "", "", f"-{format_numeric(discount_amt)}"],
        ["Cess Amt", "", "", "", format_numeric(cess_amount)],
    ])

    # GST handling based on tax type
    if show_gst:
        if float(total_igst) > 0:
            table_data.append(["IGST", "", "", "", format_numeric(total_igst)])
        else:
            if float(total_cgst) > 0:
                table_data.append(["CGST", "", "", "", format_numeric(total_cgst)])
            if float(total_sgst) > 0:
                table_data.append(["SGST", "", "", "", format_numeric(total_sgst)])

    # Round Off, Bill Total, and Amount in Words
    table_data.extend([
        ["Round Off", "", "", "", format_numeric(round_0ff)],
        ["Bill Total", "", "", "", format_numeric(bill_total)],
        [Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", normal_style), "", "", "", ""]
    ])

    # Create table
    table = Table(table_data, colWidths=col_widths)

    # Styling
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),

        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # Divider above totals
        ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),  # Above "Total Quantity"

        # Divider before final rows (Round Off)
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),  # Above Bill Total

        # Divider before amount in words
        ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.grey),

        # Right-align all numeric columns
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),

        # Left-align Description and Amount in Words
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),

        # Amount in words spans all columns
        ('SPAN', (0, -1), (-1, -1)),

        # Make final two rows bold
        ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    return table



# def return_complete_table(data, total_qty, sub_total, discount_amt, cess_amount, total_cgst, total_sgst, total_igst, round_0ff, bill_total, amount_in_words):
#     styles = getSampleStyleSheet()
#     normal_style = styles['Normal']
    
#     # Column widths
#     col_widths = [4.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch]
    
#     # Table data with headers
#     table_data = [
#         [
#             Paragraph("<b>Description</b>", normal_style),
#             Paragraph("<b>Qty</b>", normal_style),
#             Paragraph("<b>MRP</b>", normal_style),
#             Paragraph("<b>Amount</b>", normal_style),
#             Paragraph("<b>Discount</b>", normal_style)
#         ]
#     ]
    
#     # Add product rows
#     for item in data:
#         table_data.append([
#             Paragraph(str(item[1])),  # Description
#             Paragraph(format_numeric(item[3])),  # Qty
#             Paragraph(format_numeric(item[5])),  # MRP
#             Paragraph(format_numeric(item[6])),   # Amount
#             Paragraph(format_numeric(item[8]))   # Amount
#         ])
    
#     # Add empty rows if less than 4 products
#     while len(table_data) < 5:  # Header + min 3 products + empty row
#         table_data.append(["", "", "", ""])
    
#     # Add financial rows
#     table_data.extend([
#         ["Total Quantity", "", "", "", total_qty],
#         ["Sub Total", "", "", "", sub_total],
#         ["Total Discount", "", "", "", f"-{discount_amt}"],
#         ["Cess Amt", "", "", "", f"{cess_amount}"] #cess_amount
#     ])

#     if float(total_igst) > 0:
#         table_data.append(["IGST", "", "", "", f"{total_igst}"])
#     elif float(total_cgst) > 0 and float(total_sgst) > 0:
#         table_data.append(["CGST", "", "", "", f"{total_cgst}"])
#         table_data.append(["SGST", "", "", "", f"{total_sgst}"])

#     table_data.extend([
#         ["Round Off", "", "", "", round_0ff],
#         ["Bill Total", "", "", "", bill_total],
#         [Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", normal_style), "", "", ""]
#     ])

    
#     # Create table
#     table = Table(table_data, colWidths=col_widths)
    
#     # Apply styling
#     table.setStyle(TableStyle([
#         # Outer border
#         ('BOX', (0, 0), (-1, -1), 1, colors.black),
        
#         # Header styling
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
#         # Key dividers
#         ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),  # Above Total
#         ('LINEABOVE', (0, len(data)+3), (-1, len(data)+3), 1, colors.black),  # Above Bill Total
        
#         # Key dividers
#         ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),  # Above Total
#         ('LINEABOVE', (0, len(data)+3), (-1, len(data)+3), 1, colors.black),  # Above Bill Total
#         ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.grey),  # Line above Amount in Words
        
#         # Right-align numbers
#         ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        
       
#         # Span amount in words
#         ('SPAN', (0, -1), (-1, -1)),
        
#         # Bold important rows
#         ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
#         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
#     ]))
    
#     return table

#Payment receipt logic ...
def payment_receipt_header(company_name, company_address, company_phone, company_email):
    styles = getSampleStyleSheet()
    elements = []
    
    # Main header style
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=1,  # Center
        spaceAfter=12
    )
    
    # Subheader style
    subheader_style = ParagraphStyle(
        'SubheaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=6
    )
    
    # Contact style
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        spaceAfter=12
    )
    
    elements.append(Paragraph(company_name.upper(), header_style))
    elements.append(Paragraph(company_address, subheader_style))
    elements.append(Paragraph(f"Phone: {company_phone} | Email: {company_email}", contact_style))
    
    return elements

def payment_receipt_voucher_table(data):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Main voucher table data
    table_data = [
        [
            Paragraph(f"<b>Customer Name</b>", bold_style),
            Paragraph(f"Voucher No: {data['voucher_no']}", normal_style),
            Paragraph(f"Voucher Date: {data['voucher_date']}", normal_style)
        ],
        [
            Paragraph(data['customer_name'], normal_style),
            "Bills Ref",
            "-"
        ],
        [
            "",
            "Transfer No.",
            "-"
        ],
        [
            Paragraph(f"<b>Transfer Name</b>", bold_style),
            data['transfer_name'],
            Paragraph(f"<b>Transfer Date</b>", bold_style),
            data['transfer_date']
        ],
        [
            Paragraph(f"<b>Bill No:</b>", bold_style),
            "Bill Date",
            "D/C",
            "Transfer Amount",
            "Adjusted Amt (Cash Discount)",
            "Net Receipt"
        ],
        # Sample transaction rows (replace with actual data)
        [
            "09:45/24-25",
            "06/03/2025",
            "D",
            "31,216.00",
            "31,216.00",
            "0.00",
            "31,216.00"
        ],
        [
            "05/23/24-25",
            "06/03/2025",
            "D",
            "",
            "(1) 300.00",
            "0.00",
            "(1) 300.00"
        ],
        [
            "05/23/24-25",
            "07/03/2025",
            "D",
            "",
            "3,384.00",
            "0.00",
            "3,384.00"
        ]
    ]
    
    col_widths = [1.5*inch, 1*inch, 0.5*inch, 1*inch, 1.5*inch, 1*inch, 1*inch]
    
    table = Table(table_data, colWidths=col_widths, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 1), (0, 2)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (3, 3)),
        ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
    ]))
    
    return table

def payment_amount_section(amount, amount_in_words, outstanding, total):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Amount in words
    amount_words = Paragraph(
        f"<b>Amount:</b> {amount_in_words}", 
        normal_style
    )
    
    # Amount breakdown table
    amounts_data = [
        [Paragraph("<b>Amount Paid:</b>", bold_style), Paragraph(f"<b>{amount:,.2f}</b>", bold_style)],
        [Paragraph("<b>Outstanding:</b>", normal_style), Paragraph(f"{outstanding:,.2f}", normal_style)],
        [Paragraph("<b>Original Total:</b>", normal_style), Paragraph(f"{total:,.2f}", normal_style)],
    ]
    
    amounts_table = Table(amounts_data, colWidths=[3*inch, 2*inch])
    amounts_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Combine both in a single table
    combined_data = [[amount_words, amounts_table]]
    table = Table(combined_data, colWidths=[4*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    return table

def payment_approval_section():
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    table_data = [
        ["", "Authorized Signatory"],
        ["Prepared By:", ""],
        ["Approved By:", ""]
    ]
    
    table = Table(table_data, colWidths=[3*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),
        ('SPAN', (1, 0), (1, 2)),
    ]))
    
    return table

def payment_receipt_amount_section(data):
    """Creates the amount section with amount in words and numeric breakdown"""
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Amount in words
    amount_words = Paragraph(
        f"<b>Amount Paid:</b> {data['amount_in_words']}", 
        normal_style
    )
    
    # Amount breakdown table
    amounts_data = [
        [Paragraph("<b>Amount Paid:</b>", bold_style), f"{data['amount']:,.2f}"],
        [Paragraph("Outstanding:", normal_style), f"{data['outstanding']:,.2f}"],
        [Paragraph("Original Total:", normal_style), f"{data['total']:,.2f}"],
    ]
    
    amounts_table = Table(amounts_data, colWidths=[2.0*inch, 1.5*inch])
    amounts_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    # Combine both sections
    combined_table = Table([
        [amount_words, amounts_table]
    ], colWidths=[4.0*inch, 3.5*inch])
    
    combined_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    return combined_table

def payment_receipt_voucher_table(data):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Main voucher table data
    table_data = [
        [
            Paragraph(f"<b>Customer Name</b>", bold_style),
            Paragraph(f"Voucher No: {data['voucher_no']}", normal_style),
            Paragraph(f"Voucher Date: {data['voucher_date']}", normal_style)
        ],
        [
            Paragraph(data['customer_name'], normal_style),
            "Bills Ref",
            "-"
        ],
        [
            "",
            "Transfer No.",
            "-"
        ],
        [
            Paragraph(f"<b>Transfer Name</b>", bold_style),
            data['transfer_name'],
            Paragraph(f"<b>Transfer Date</b>", bold_style),
            data['transfer_date']
        ],
        [
            Paragraph(f"<b>Bill No:</b>", bold_style),
            "Bill Date",
            "D/C",
            "Transfer Amount",
            "Adjusted Amt (Cash Discount)",
            "Net Receipt"
        ],
        # Sample transaction rows (replace with actual data)
        [
            "09:45/24-25",
            "06/03/2025",
            "D",
            "31,216.00",
            "31,216.00",
            "0.00",
            "31,216.00"
        ],
        [
            "05/23/24-25",
            "06/03/2025",
            "D",
            "",
            "(1) 300.00",
            "0.00",
            "(1) 300.00"
        ],
        [
            "05/23/24-25",
            "07/03/2025",
            "D",
            "",
            "3,384.00",
            "0.00",
            "3,384.00"
        ]
    ]
    
    col_widths = [1.5*inch, 1*inch, 0.5*inch, 1*inch, 1.5*inch, 1*inch, 1*inch]
    
    table = Table(table_data, colWidths=col_widths, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
        # Vertical lines only
        ('LINEBEFORE', (0, 0), (0, -1), 1, colors.black),  # First column
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),  # Second column
        ('LINEBEFORE', (2, 0), (2, -1), 1, colors.black),  # Third column
        ('LINEBEFORE', (3, 0), (3, -1), 1, colors.black),  # Fourth column
        ('LINEBEFORE', (4, 0), (4, -1), 1, colors.black),  # Fifth column
        ('LINEBEFORE', (5, 0), (5, -1), 1, colors.black),  # Sixth column
        ('LINEBEFORE', (6, 0), (6, -1), 1, colors.black),  # Seventh column
        
        # Remove all horizontal lines by removing GRID and LINEABOVE/BELOW
        ('SPAN', (0, 1), (0, 2)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (3, 3)),
        ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
        
        # Right align numeric columns
        ('ALIGN', (3, 5), (6, -1), 'RIGHT'),
    ]))
    
    return table

def payment_customer_details(cust_name, billing_address, phone, email):
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    
    # Create structured content for payment receipts
    customer_content = Paragraph(
        f"<b>{cust_name}</b><br/>"
        f"{billing_address}<br/>"
        f"<b>Phone:</b> {phone}<br/>"
        f"<b>Email:</b> {email}",
        style_normal
    )
    
    table_data = [
        [customer_content]
    ]
    
    table = Table(table_data, colWidths=[10*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    return table

def payment_details_table(payment_data):
    style_normal = getSampleStyleSheet()['Normal']
    
    # Column widths similar to sale order
    col_widths = [1.5*inch, 3*inch, 1.5*inch, 2*inch, 2*inch]
    
    # Table headers
    table_data = [
        [
            Paragraph("<b>Invoice No.</b>", style_normal),
            Paragraph("<b>Invoice Date</b>", style_normal),
            Paragraph("<b>Payment Method</b>", style_normal),
            Paragraph("<b>Reference No.</b>", style_normal),
            Paragraph("<b>Amount Paid</b>", style_normal)
        ]
    ]
    
    # Add payment rows
    for payment in payment_data:
        row = [
            Paragraph(payment['invoice_no'], style_normal),
            Paragraph(payment['invoice_date'], style_normal),
            Paragraph(payment['payment_method'], style_normal),
            Paragraph(payment.get('cheque_no', 'N/A'), style_normal),
            Paragraph(format_numeric(payment['amount']), style_normal)
        ]
        table_data.append(row)
    
    # Ensure minimum rows for spacing
    while len(table_data) < 6:
        table_data.append([" "] * 5)
    
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Amount right-aligned
        
        # Vertical lines between all columns
        ('LINEBEFORE', (0, 0), (0, -1), 1, colors.black),  # First column
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),  # Second column
        ('LINEBEFORE', (2, 0), (2, -1), 1, colors.black),  # Third column
        ('LINEBEFORE', (3, 0), (3, -1), 1, colors.black),  # Fourth column
        ('LINEBEFORE', (4, 0), (4, -1), 1, colors.black),  # Fifth column
        ('LINEAFTER', (4, 0), (4, -1), 1, colors.black),
        
        # Horizontal line only below header and above last row
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Below header
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Above last row
        
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        
        # Remove all other horizontal lines
        ('TOPPADDING', (0, 1), (-1, -2), 8),  # Add some padding between rows
    ]))
    
    return table

def payment_amount_summary(outstanding, amount_in_words):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Amount in words
    amount_paragraph = Paragraph(
        f"<b>Amount in Words:</b> {amount_in_words}",
        normal_style
    )
    
    # Amount breakdown
    amounts_data = [
        # [Paragraph("<b>Amount Paid:</b>", bold_style), format_numeric(amount)],
        [Paragraph("Outstanding Balance:", normal_style), format_numeric(outstanding)],
        # [Paragraph("Original Total:", normal_style), format_numeric(total)],
    ]
    
    amounts_table = Table(amounts_data, colWidths=[3*inch, 2*inch])
    amounts_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Combine both sections
    combined = Table([
        [amount_paragraph, amounts_table]
    ], colWidths=[6*inch, 4*inch])
    
    combined.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    return combined