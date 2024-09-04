from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Flowable





def create_table_1(sno, sdate):
    col_widths = [3.3*inch, 3.4*inch, 3.3*inch]
    table_data_1 = [
        ['Customer Billing Detail', f'SO No. {sno}', f'SO Date {sdate}'],
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

def create_table_2(cust_name, city, country, phone, destination):
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

def create_table_3(data):
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

def create_table_4(ttl_Qty, ttl_Amount, ttl_Tax):
    table_4_col_widths = [0.6 * inch, 3.4 * inch, 0.7 * inch, 0.9 * inch, 1.1 * inch, 1.2 * inch, 1.1 * inch, 1.0 * inch]
    table_4_heading = [[' ','Total',ttl_Qty,' ',' ',ttl_Amount,' ',ttl_Tax]]
    
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

def create_table_5(Bill_Amount_In_Words, Tax_Amount_In_Words, Remark, Sub_Total, Discount_Amt, Round_Off, Bill_Total, Party_Old_Balance,  Net_Total):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    # Create Paragraph objects for each cell to enable text wrapping
    bill_amount_paragraph = Paragraph(f"Bill Amount In Words: {Bill_Amount_In_Words}<br/>Tax Amount In Words: {Tax_Amount_In_Words}<br/>Remark: {Remark}", normal_style)
    financials_paragraph = Paragraph(f"Sub Total: {Sub_Total}<br/>Discount Amt: {Discount_Amt}<br/>Round Off: {Round_Off}<br/>Bill Total: {Bill_Total}<br/>Party Old Balance: {Party_Old_Balance}<br/>Net Total: {Net_Total}", normal_style)
    
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

def create_table_6():
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
