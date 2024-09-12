from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer

def doc_heading(file_path, doc_header, sub_header):
    elements = []

    # Custom page size (11 inches wide, 10.5 inches high)
    page_width = 11 * inch
    page_height = 10.5 * inch

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

    if doc_header == "SALES ORDER":
        main_heading(doc_header)
        
    elif doc_header == "SALES QUOTATION":
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

def customer_details(cust_name, city, country, phone, destination):
    style_normal = getSampleStyleSheet()['Normal']
    table_data_2 = [[f"{cust_name} \n{city} {country}",f"Phone: {phone} \nDestination:   {destination}"]]
    table_2_col_widths = [5*inch, 5*inch]
    
    table = Table(table_data_2, colWidths=table_2_col_widths)
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

def product_details(data):
    style_normal = getSampleStyleSheet()['Normal']
    tbl_3_col_widths = [0.6 * inch, 3.4 * inch, 0.7 * inch, 0.9 * inch, 1.1 * inch, 1.2 * inch, 1.1 * inch, 1.0 * inch]
    table_3_heading = [["Idx", "Product", "Qty", "Unit Name", "Rate", "Amount", "Discount", "Tax"]]
    
    for index, item in enumerate(data):
        row = [
            str(index + 1),                   # Index
            item[1],                          # Product
            item[2],                          # Quantity
            item[3],                          # Unit Name
            item[4],                          # Rate
            item[5],                          # Amount
            item[6],                          # Discount
            item[7]                           # Tax
        ]
        # Convert each cell into a Paragraph with normal style
        wrapped_row = [Paragraph(cell, style_normal) for cell in row]
        table_3_heading.append(wrapped_row)

    table = Table(table_3_heading, colWidths=tbl_3_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 0, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    return table

def product_total_details(ttl_Qty, ttl_Amount,total_disc, ttl_Tax):
    table_4_col_widths = [0.6 * inch, 3.4 * inch, 0.7 * inch, 0.9 * inch, 1.1 * inch, 1.2 * inch, 1.1 * inch, 1.0 * inch]
    table_4_heading = [[' ','Total',ttl_Qty,' ',' ',ttl_Amount, total_disc, ttl_Tax]]
    
    table = Table(table_4_heading, colWidths=table_4_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 0, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    return table

def product_total_details_inwords(Bill_Amount_In_Words, Remark, Sub_Total, Discount_Amt, Round_Off, Bill_Total, Party_Old_Balance, net_lbl, Net_Total):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    # Create Paragraph objects for each cell to enable text wrapping
    bill_amount_paragraph = Paragraph(f"Bill Amount In Words: {Bill_Amount_In_Words}<br/>Tax Amount In Words: {Bill_Amount_In_Words}<br/>Remark: {Remark}", normal_style)
    financials_paragraph = Paragraph(f"<b>Sub Total: {Sub_Total}<br/>Discount Amt: {Discount_Amt}<br/>Round Off: {Round_Off}<br/>Bill Total: {Bill_Total}<br/>Party Old Balance: {Party_Old_Balance}<br/>{net_lbl} : {Net_Total} </b>", normal_style)
    # Table data with Paragraph objects
    table_data_5 = [
        [bill_amount_paragraph, financials_paragraph]
    ]
    table_5_col_widths = [5*inch, 5*inch]
    table = Table(table_data_5, colWidths=table_5_col_widths)
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

def declaration():
    table_data_6 = [['Declaration:' '\n' 'We declare that this invoice shows the actual price of the goods/services' '\n' 'described and that all particulars are true and correct.' '\n' 'Original For Recipient', 'Authorised Signatory']]
    table_6_col_widths = [5*inch, 5*inch]
    
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
