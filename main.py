"""
main.py
-------
Console menu for the Medicine Expiry and Inventory Analyzer.

Run it with:      python main.py
Run the tests:    python -m unittest discover -s tests -v

Data is kept in memory (plain lists) - there is no database.
Sample medicines are loaded automatically at start-up.
"""
from datetime import date

import inventory
import reports
import sample_data
from validators import (
    format_date,
    is_past,
    to_iso,
    validate_non_empty,
    validate_non_negative_int,
    validate_positive_int,
)

# Today's date is created once and passed into every analysis call.
TODAY = date.today()


# ---------------------------------------------------------------------------
# Small input helpers (they re-ask until the input is valid)
# ---------------------------------------------------------------------------
def ask_until(prompt, check, label=None):
    """Keep asking until the check function succeeds.

    check raises ValueError for bad input -> we show the message and retry.
    """
    while True:
        text = input(prompt)
        try:
            if label is None:
                return check(text)
            return check(text, label)
        except ValueError as error:
            print("  Invalid input: " + str(error))


def ask_date(prompt):
    """Ask for a DD-MM-YYYY date; blank means today."""
    while True:
        text = input(prompt).strip()
        if text == "":
            return TODAY.isoformat()
        try:
            return to_iso(text)
        except ValueError as error:
            print("  Invalid input: " + str(error))


# ---------------------------------------------------------------------------
# Menu option handlers
# ---------------------------------------------------------------------------
def menu_add_medicine(medicines):
    """1. Add medicine (store inventory)."""
    print("")
    print("--- 1. Add medicine ---")
    name = ask_until("Medicine name: ", validate_non_empty, "Medicine name")
    batch = ask_until("Batch: ", validate_non_empty, "Batch")
    quantity = ask_until("Quantity: ", validate_positive_int, "Quantity")
    expiry_iso = ask_until("Expiry date (DD-MM-YYYY): ", to_iso)
    monthly_sales = ask_until("Monthly sales: ", validate_non_negative_int, "Monthly sales")
    reorder_level = ask_until("Reorder level: ", validate_non_negative_int, "Reorder level")

    if is_past(expiry_iso, TODAY):
        print("  Warning: this expiry date is already in the past - the medicine is EXPIRED.")

    medicine = {
        "id": inventory.next_id(medicines),
        "name": name,
        "batch": batch.upper(),
        "quantity": quantity,
        "expiry_date": expiry_iso,
        "monthly_sales": monthly_sales,
        "reorder_level": reorder_level,
        "created_at": TODAY.isoformat(),
    }
    inventory.add_medicine(medicines, medicine)   # raises ValueError if duplicate
    print("  Medicine '" + medicine["name"] + "' added with ID " +
          str(medicine["id"]) + ".")


def menu_update_expiry(medicines):
    """2. Validate / update expiry date."""
    print("")
    print("--- 2. Validate / update expiry date ---")
    if not medicines:
        print("  No medicines in inventory.")
        return
    medicine_id = ask_until("Medicine ID (use option 4 to see IDs): ",
                            validate_positive_int, "Medicine ID")
    medicine = inventory.get_medicine(medicines, medicine_id)
    if medicine is None:
        raise ValueError("No medicine found with ID " + str(medicine_id) + ".")
    print("  Current: " + medicine["name"] + " (Batch: " + medicine["batch"] +
          ") expires " + format_date(medicine["expiry_date"]))
    new_iso = ask_until("New expiry date (DD-MM-YYYY): ", to_iso)
    if is_past(new_iso, TODAY):
        print("  Warning: the new date is in the past - the medicine is already EXPIRED.")
    inventory.update_expiry(medicines, medicine_id, new_iso)
    print("  Expiry date updated to " + format_date(new_iso) + ".")


def menu_search(medicines):
    """3. Search by name (partial), batch, or expiry status."""
    print("")
    print("--- 3. Search medicines ---")
    print("  1. By name (partial match)")
    print("  2. By batch")
    print("  3. By expiry status")
    choice = input("  Choice: ").strip()

    if choice == "1":
        term = input("  Name fragment: ").strip()
        if not term:
            print("  Please type something to search for.")
            return
        results = inventory.search_by_name(medicines, term)
    elif choice == "2":
        term = input("  Batch: ").strip()
        if not term:
            print("  Please type something to search for.")
            return
        results = inventory.search_by_batch(medicines, term)
    elif choice == "3":
        print("  a. Expired   b. Nearing Expiry   c. Safe")
        pick = input("  Choice (a/b/c): ").strip().lower()
        status = {"a": "Expired", "b": "Nearing Expiry", "c": "Safe"}.get(pick)
        if status is None:
            print("  Invalid choice.")
            return
        results = inventory.filter_by_status(medicines, status, TODAY)
    else:
        print("  Invalid choice.")
        return

    reports.print_medicine_list(results, TODAY, heading="SEARCH RESULTS")


def menu_record_transaction(medicines, transactions):
    """5. Record purchase (add stock) or sale (remove stock)."""
    print("")
    print("--- 5. Record purchase / sale ---")
    if not medicines:
        print("  No medicines in inventory.")
        return
    medicine_id = ask_until("Medicine ID (use option 4 to see IDs): ",
                            validate_positive_int, "Medicine ID")
    kind = input("  Type (P = purchase, S = sale): ").strip().upper()
    if kind not in ("P", "S"):
        print("  Invalid type - please enter P or S.")
        return
    quantity = ask_until("  Quantity: ", validate_positive_int, "Quantity")
    tx_date = ask_date("  Date (DD-MM-YYYY, blank = today): ")

    if kind == "P":
        medicine = inventory.record_purchase(
            medicines, transactions, medicine_id, quantity, tx_date)
        print("  Purchase recorded. New stock of " + medicine["name"] + ": " +
              str(medicine["quantity"]))
    else:
        medicine = inventory.record_sale(
            medicines, transactions, medicine_id, quantity, tx_date)
        print("  Sale recorded. New stock of " + medicine["name"] + ": " +
              str(medicine["quantity"]))


def menu_export(medicines):
    """8. Export a report to CSV or TXT inside exports/."""
    print("")
    print("--- 8. Export report ---")
    print("  1. Medicine list")
    print("  2. Expiry report")
    print("  3. Analysis report")
    what = input("  Choose report (1-3): ").strip()
    print("  1. CSV")
    print("  2. TXT")
    how = input("  Choose format (1-2): ").strip()

    if what == "1":
        rows, name = reports.medicine_rows(medicines, TODAY), "medicines"
    elif what == "2":
        rows, name = reports.expiry_rows(medicines, TODAY), "expiry_report"
    elif what == "3":
        rows, name = reports.analysis_rows(medicines, TODAY), "analysis_report"
    else:
        print("  Invalid report choice.")
        return

    if how == "1":
        file_format = "CSV"
    elif how == "2":
        file_format = "TXT"
    else:
        print("  Invalid format choice.")
        return

    path = reports.export_rows(rows, name, file_format)
    if path is None:
        print("  Nothing to export.")
    else:
        print("  Report exported to: " + path)


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------
def show_menu():
    print("")
    print("========================================================")
    print("   MEDICINE EXPIRY AND INVENTORY ANALYZER")
    print("========================================================")
    print("1. Add medicine")
    print("2. Validate / update expiry date")
    print("3. Search medicines")
    print("4. View all medicines")
    print("5. Record purchase / sale")
    print("6. Expiry report")
    print("7. Analysis report")
    print("8. Export report (CSV / TXT)")
    print("9. Exit")


def handle_choice(choice, medicines, transactions):
    if choice == "1":
        menu_add_medicine(medicines)
    elif choice == "2":
        menu_update_expiry(medicines)
    elif choice == "3":
        menu_search(medicines)
    elif choice == "4":
        reports.print_medicine_list(medicines, TODAY, heading="ALL MEDICINES")
    elif choice == "5":
        menu_record_transaction(medicines, transactions)
    elif choice == "6":
        reports.print_expiry_report(medicines, TODAY)
    elif choice == "7":
        reports.print_analysis_report(medicines, TODAY)
    elif choice == "8":
        menu_export(medicines)


def main():
    medicines = sample_data.seed_medicines()
    transactions = sample_data.seed_transactions()
    print("Welcome! " + str(len(medicines)) +
          " sample medicines loaded (in-memory storage, no database needed).")

    while True:
        try:
            show_menu()
            choice = input("Enter your choice (1-9): ").strip()
            if choice == "9":
                print("Thank you for using Medicine Expiry and Inventory Analyzer. Goodbye!")
                break
            if choice in ("1", "2", "3", "4", "5", "6", "7", "8"):
                handle_choice(choice, medicines, transactions)
            else:
                print("Invalid choice - please enter a number from 1 to 9.")
        except ValueError as error:
            # Bad input never crashes the program - we just show the reason.
            print("  Error: " + str(error))
        except (EOFError, KeyboardInterrupt):
            print("")
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
