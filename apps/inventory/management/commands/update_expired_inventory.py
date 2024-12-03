# from django.core.management.base import BaseCommand
# from django.db import connection

# class Command(BaseCommand):
#     help = "Check for expired orders and add back blocked product quantities to Inventory."

#     def handle(self, *args, **kwargs):
#         try:
#             with connection.cursor() as cursor:
#                 # Restore blocked quantities to inventory
#                 cursor.execute("""
#                     UPDATE cnl_1.products p
#                     JOIN cnl_1.blocked_inventory bi
#                       ON p.product_id = bi.product_id
#                     SET p.balance = p.balance + bi.blocked_qty
#                     WHERE bi.expiration_time <= NOW()
#                       AND bi.is_expired = FALSE;
#                 """)
#                 self.stdout.write(self.style.SUCCESS("Successfully restored blocked quantities."))

#                 # Mark inventory blocks as expired
#                 cursor.execute("""
#                     UPDATE cnl_1.blocked_inventory
#                     SET is_expired = TRUE
#                     WHERE expiration_time <= NOW()
#                       AND is_expired = FALSE;
#                 """)
#                 self.stdout.write(self.style.SUCCESS("Successfully marked expired inventory blocks."))
#         except Exception as e:
#             self.stderr.write(self.style.ERROR(f"Error updating inventory: {e}"))

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Check for expired orders and add back blocked product quantities to Inventory."

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                # Restore blocked quantities to inventory
                cursor.execute("""
                    UPDATE products p
                    JOIN blocked_inventory bi
                      ON p.product_id = bi.product_id
                    SET p.balance = p.balance + bi.blocked_qty
                    WHERE bi.expiration_time <= NOW()
                      AND bi.is_expired = FALSE;
                """)
                self.stdout.write(self.style.SUCCESS("Successfully restored blocked quantities."))

                # Mark inventory blocks as expired
                cursor.execute("""
                    UPDATE blocked_inventory
                    SET is_expired = TRUE
                    WHERE expiration_time <= NOW()
                      AND is_expired = FALSE;
                """)
                self.stdout.write(self.style.SUCCESS("Successfully marked expired inventory blocks."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error updating inventory: {e}"))
