from django.core.management.base import BaseCommand
from apps.masters.models import LedgerGroups
from apps.customer.models import LedgerAccounts


# Standard Indian ERP ledger group hierarchy 
# Format: (name, nature, under_group_name_or_None, purpose)
# purpose is the STABLE system flag used for context-aware filtering — never changes
# even if the user renames the group. This is how Tally/SAP/AlignBooks work internally.
STANDARD_GROUPS = [
    # Format: (name, nature, parent_name, purpose)
    # ── Root groups ───────────────────────────────────────────────────────
    ("Capital Account",          "Liability", None,                    "General"),
    ("Loans (Liability)",        "Liability", None,                    "General"),
    ("Current Liabilities",      "Liability", None,                    "General"),
    ("Fixed Assets",             "Asset",     None,                    "General"),
    ("Current Assets",           "Asset",     None,                    "General"),
    ("Investments",              "Asset",     None,                    "General"),
    ("Misc. Expenses (Asset)",   "Asset",     None,                    "General"),
    ("Sales Accounts",           "Income",    None,                    "General"),
    ("Direct Incomes",           "Income",    None,                    "General"),
    ("Indirect Incomes",         "Income",    None,                    "General"),
    ("Purchase Accounts",        "Expense",   None,                    "General"),
    ("Direct Expenses",          "Expense",   None,                    "General"),
    ("Indirect Expenses",        "Expense",   None,                    "General"),

    # ── Under Capital Account ─────────────────────────────────────────────
    ("Reserves & Surplus",       "Liability", "Capital Account",       "General"),

    # ── Under Loans (Liability) ───────────────────────────────────────────
    ("Bank OD Accounts",         "Liability", "Loans (Liability)",     "Bank"),
    ("Secured Loans",            "Liability", "Loans (Liability)",     "General"),
    ("Unsecured Loans",          "Liability", "Loans (Liability)",     "General"),

    # ── Under Current Liabilities ─────────────────────────────────────────
    ("Sundry Creditors",         "Liability", "Current Liabilities",   "AccountsPayable"),
    ("Duties & Taxes",           "Liability", "Current Liabilities",   "General"),
    ("Provisions",               "Liability", "Current Liabilities",   "General"),
    ("Advance from Customers",   "Liability", "Current Liabilities",   "AccountsReceivable"),

    # ── Under Current Assets ──────────────────────────────────────────────
    ("Cash-in-Hand",             "Asset",     "Current Assets",        "Cash"),
    ("Bank Accounts",            "Asset",     "Current Assets",        "Bank"),
    ("Sundry Debtors",           "Asset",     "Current Assets",        "AccountsReceivable"),
    ("Stock-in-Hand",            "Asset",     "Current Assets",        "General"),
    ("Deposits (Asset)",         "Asset",     "Current Assets",        "General"),
    ("Loans & Advances (Asset)", "Asset",     "Current Assets",        "General"),

    # ── Under Fixed Assets ───────────────────────────────────────────────
    ("Plant & Machinery",        "Asset",     "Fixed Assets",          "General"),
    ("Furniture & Fixtures",     "Asset",     "Fixed Assets",          "General"),
    ("Land & Building",          "Asset",     "Fixed Assets",          "General"),
]

# Standard master LedgerAccounts to seed after groups are created.
# Format: (account_name, ledger_group_name, type)
# These are the "header" accounts used in Customer/Vendor "Under Ledger" dropdowns.
STANDARD_ACCOUNTS = [
    # ── Customer-related accounts (shown in Customer "Under Ledger") ──────────
    # type=General matches AlignBooks — the Group name, not account type, drives context
    ("Sundry Debtors",              "Sundry Debtors",             "General"),
    ("Advance Received From Customers", "Advance from Customers", "General"),

    # ── Vendor-related accounts (shown in Vendor "Under Ledger") ─────────────
    ("Sundry Creditors",            "Sundry Creditors",           "General"),
    ("Sundry Creditors-Capital Goods", "Sundry Creditors",        "General"),
    ("Sundry Creditors-Expenses",   "Sundry Creditors",           "General"),
    ("Advance To Vendors",          "Sundry Creditors",           "General"),

    # ── Bank/Cash master accounts ─────────────────────────────────────────────
    ("Cash-in-Hand",                "Cash-in-Hand",               "Cash"),
    ("Bank Account",                "Bank Accounts",              "Bank"),
]


class Command(BaseCommand):
    help = "Seed standard Indian ERP ledger groups and master accounts (safe to run multiple times)"

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        # First pass: create/update root groups
        name_to_instance = {}
        for name, nature, parent_name, purpose in STANDARD_GROUPS:
            if parent_name is not None:
                continue

            obj, created = LedgerGroups.objects.get_or_create(
                name=name,
                defaults={"nature": nature, "under_group_id": None, "purpose": purpose},
            )
            # Always stamp the purpose even on existing rows (safe idempotent update)
            if not created and obj.purpose != purpose:
                obj.purpose = purpose
                obj.save(update_fields=['purpose'])
            name_to_instance[name] = obj
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {name} (purpose={purpose})")
            else:
                skipped_count += 1

        # Second pass: create/update child groups
        for name, nature, parent_name, purpose in STANDARD_GROUPS:
            if parent_name is None:
                continue

            parent = name_to_instance.get(parent_name) or LedgerGroups.objects.filter(name=parent_name).first()
            if not parent:
                self.stdout.write(self.style.WARNING(f"  Skipped '{name}': parent '{parent_name}' not found"))
                continue

            obj, created = LedgerGroups.objects.get_or_create(
                name=name,
                defaults={"nature": nature, "under_group_id": parent, "purpose": purpose},
            )
            # Always stamp the purpose even on existing rows
            if not created and obj.purpose != purpose:
                obj.purpose = purpose
                obj.save(update_fields=['purpose'])
            name_to_instance[name] = obj
            if created:
                created_count += 1
                self.stdout.write(f"  Created: {name} under {parent_name} (purpose={purpose})")
            else:
                skipped_count += 1

        # Fix: correct type on accounts previously seeded with wrong type
        WRONG_TYPE_FIXES = {
            "Sundry Debtors": "General",
            "Advance Received From Customers": "General",
            "Sundry Creditors": "General",
            "Sundry Creditors-Capital Goods": "General",
            "Sundry Creditors-Expenses": "General",
            "Advance To Vendors": "General",
        }
        for acct_name, correct_type in WRONG_TYPE_FIXES.items():
            LedgerAccounts.objects.filter(name=acct_name).exclude(type=correct_type).update(type=correct_type)

        # Fix: move "Advance To Vendors" to "Sundry Creditors" group so it appears in vendor dropdown
        sundry_creditors_group = LedgerGroups.objects.filter(name="Sundry Creditors").first()
        if sundry_creditors_group:
            LedgerAccounts.objects.filter(name="Advance To Vendors").exclude(
                ledger_group_id=sundry_creditors_group
            ).update(ledger_group_id=sundry_creditors_group)

        # Third pass: seed master LedgerAccounts
        acct_created = 0
        acct_skipped = 0
        for acct_name, group_name, acct_type in STANDARD_ACCOUNTS:
            group = LedgerGroups.objects.filter(name=group_name).first()
            if not group:
                self.stdout.write(self.style.WARNING(
                    f"  Skipped account '{acct_name}': group '{group_name}' not found"
                ))
                continue

            obj, created = LedgerAccounts.objects.get_or_create(
                name=acct_name,
                defaults={"ledger_group_id": group, "type": acct_type},
            )
            if created:
                acct_created += 1
                self.stdout.write(f"  Account created: {acct_name} ({acct_type})")
            else:
                acct_skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nGroups  — Created: {created_count}, Already existed: {skipped_count}"
            f"\nAccounts — Created: {acct_created}, Already existed: {acct_skipped}"
        ))
