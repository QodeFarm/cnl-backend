import inflect
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

def convert_amount_to_words(amount):
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

