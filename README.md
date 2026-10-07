# Medicine Expiry and Inventory Analyzer

A beginner-friendly, menu-driven **CLI** project (Python 3, standard library only — no external packages, **no database**). All data is kept in simple Python lists in memory.

## Problem Statement

Track medicine inventory, expiry dates and sales to identify medicines approaching expiry and slow-moving stock. The program tells the pharmacist what is expired, what is about to expire, what is not selling, what is running out — and what action to take.

## Features

1. Add medicine (store inventory)
2. Validate / update expiry date (`DD-MM-YYYY` input, rejects invalid dates, warns if already expired)
3. Search medicines by name (partial match), batch, or expiry status
4. View all medicines with expiry status
5. Record purchase (increase stock) / record sale (decrease stock — blocked when stock is insufficient; monthly sales updated automatically)
6. Expiry report grouped as Expired / Nearing Expiry / Safe
7. Analysis report: nearing expiry, slow-moving stock, stock shortages + suggested actions
8. Export any report to **CSV** or **TXT** in the `exports/` folder
9. Exit

Bad input never crashes the program — invalid entries are rejected and the user is asked again.

## Setup / Run

Requires Python 3 (tested with Python 3.14). No installation step needed.

```
cd medicine-expiry-analyzer
python main.py
```

Run the unit tests:

```
python -m unittest discover -s tests -v
```

Sample medicines (including Amoxicillin, batch AMX24) load automatically at start-up. Data lives in memory, so it resets each run.

## Business Rules (constants at the top of `analyzer.py`)

**Expiry status** (`days_left = expiry - today`)

| days_left | Status |
|---|---|
| `< 0` | Expired |
| `<= 90` (EXPIRY_NEARING_DAYS) | Nearing Expiry |
| else | Safe |

**Sales rate** (`months_of_stock = quantity / monthly_sales`)

| Value | Rate |
|---|---|
| `monthly_sales == 0` | No Sales |
| `> 6` (SLOW_MONTHS) | Slow |
| `2 – 6` | Moderate |
| `< 2` | Fast |

**Shortage:** `quantity <= reorder_level` → "Shortage"

**Suggested action** (checked in this order)

1. Expired → `Remove from stock`
2. Nearing Expiry + Slow → `Review stock`
3. Nearing Expiry (other) → `Prioritize sales / discount`
4. Shortage → `Reorder`
5. Otherwise → `No action needed`

## Sample Input / Output

Input: *Medicine: Amoxicillin, Batch: AMX24, Quantity: 120, Expiry Date: 30-10-2026, Monthly Sales: 10*

Output (menu 4 or search by name "Amoxicillin"):

```
  Expiry Status: Nearing Expiry
  Current Stock: 120
  Sales Rate: Slow
  Action: Review stock
```

## Project Structure

```
medicine-expiry-analyzer/
  main.py                 # CLI menu loop and input handling
  inventory.py            # in-memory storage: add/update/search/transactions
  validators.py           # date and quantity validation (DD-MM-YYYY)
  analyzer.py             # business rules (expiry, sales rate, shortage, action)
  reports.py              # console reports + CSV/TXT export to exports/
  sample_data.py          # seeds 10+ realistic medicines
  tests/test_analyzer.py  # unittest for business rules
  tests/test_validators.py# unittest for input validation
  README.md
  .gitignore              # ignores __pycache__/, exports/, *.db
```
