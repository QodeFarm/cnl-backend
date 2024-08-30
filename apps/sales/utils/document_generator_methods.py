import os
import shutil
import inflect
from config.settings import MEDIA_ROOT
from apps.sales.utils import sales_order_rcpt_word_docx as wd


def convert_amount_to_words(amount):
    '''
This Code convert amount into world.
Ex. amount = 784365923.04
    O/P = INR Seventy-Eight Crore Forty-Three Lakh Sixty-Five Thousand Nine Hundred Twenty-Three And Four Paise
-------------For Testing---------------
# # Example usage:
# amount = 784365923.04
# result = convert_amount_to_words(amount)
# print((result))  

'''
    # Split amount into rupees and paise
    amount_parts = str(amount).split(".")
    
    # Convert rupees part
    rupees_part = int(amount_parts[0])
    
    # Check if there are paise
    paise_part = int(amount_parts[1]) if len(amount_parts) > 1 else 0
    
    # Convert rupees to words
    rupees_in_words = convert_rupees_to_indian_words(rupees_part)
    
    # Convert paise to words
    p = inflect.engine()
    paise_in_words = (
        p.number_to_words(paise_part).replace(",", "") if paise_part > 0 else "zero"
    )
    
    amt_world = f"{rupees_in_words} and {paise_in_words} paise"
    return "INR " + amt_world.title() 

def convert_rupees_to_indian_words(number):
    p = inflect.engine()
    if number == 0:
        return "zero rupees"
    
    parts = []
    
    # Define thresholds and labels
    units = [
        (1000000000, "arab"),
        (10000000, "crore"),
        (100000, "lakh"),
        (1000, "thousand"),
        (100, "hundred")
    ]
    
    for value, name in units:
        if number >= value:
            quotient, number = divmod(number, value)
            parts.append(f"{p.number_to_words(quotient)} {name}")
    
    if number > 0:
        parts.append(p.number_to_words(number))
    
    return " ".join(parts)



def extract_product_data(data):
    product_data = []
    
    for index, item in enumerate(data, start=1):
        product = item['product']
        unit_options = item['unit_options']        
        product_name = product['name']
        quantity = item['quantity']
        unit_name = unit_options['unit_name']
        rate = item['rate']
        amount = item['amount']
        discount = item['discount']
        tax = str(item['tax'] if item['tax'] is not None else 0)
        
        product_data.append([
            str(index), product_name, quantity, unit_name, rate, amount, discount, tax])

    return product_data


def save_sales_order_pdf_to_media(product_data, cust_data):
    # Generate the PDF file
    pdf_file_path = wd.create_sales_order_doc(product_data, cust_data)
    
    # Define the directory where the file will be saved
    sales_order_dir = os.path.join(MEDIA_ROOT, 'sales order receipt')

    # Create the directory if it doesn't exist
    if not os.path.exists(sales_order_dir):
        os.makedirs(sales_order_dir)

    # Define the new file path in the media directory
    new_file_path = os.path.join(sales_order_dir, os.path.basename(pdf_file_path))
    
    # Move the PDF file to the new directory
    shutil.move(pdf_file_path, new_file_path)

    # Return the relative path to the file (relative to MEDIA_ROOT)
    relative_file_path = os.path.join('sales order receipt', os.path.basename(pdf_file_path))
    return relative_file_path