import os
from barcode import Code128
from barcode.writer import ImageWriter
from django.conf import settings


def generate_barcode_image(barcode_value):
    """
    Generates a barcode image for the given barcode value.
    Saves the image in MEDIA_ROOT/barcodes/
    """

    if not barcode_value:
        return None

    # Ensure barcode directory exists
    barcode_dir = os.path.join(settings.MEDIA_ROOT, "barcodes")
    os.makedirs(barcode_dir, exist_ok=True)

    # File path (without extension, python-barcode adds .png)
    file_path = os.path.join(barcode_dir, str(barcode_value))

    # Skip regeneration if already exists
    if os.path.exists(file_path + ".png"):
        return file_path + ".png"

    # Generate barcode
    barcode = Code128(barcode_value, writer=ImageWriter())

    barcode.save(
        file_path,
        options={
            "write_text": True,     # shows barcode value below image
            "module_height": 15.0,  # barcode height
            "font_size": 10,
            "quiet_zone": 6.5,
        }
    )

    return file_path + ".png"
