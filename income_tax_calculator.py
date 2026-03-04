# Indian Income Tax Calculator — New Regime FY 2024-25
# Uses progressive (slab-wise) taxation: each rupee is taxed only at the rate of the slab it falls into, not the highest applicable rate on the full income.

# Standard deduction allowed under the new regime (Budget 2024)
STANDARD_DEDUCTION = 75_000

# Tax slabs as (upper_limit, rate) pairs; None means "no upper limit" (top slab)
# Each tuple: (slab ceiling in rupees, tax rate as a fraction)
TAX_SLABS = [
    (3_00_000,  0.00),   # 0 – 3 L  →  0 %
    (7_00_000,  0.05),   # 3 – 7 L  →  5 %
    (10_00_000, 0.10),   # 7 – 10 L → 10 %
    (12_00_000, 0.15),   # 10 – 12 L→ 15 %
    (15_00_000, 0.20),   # 12 – 15 L→ 20 %
    (None,      0.30),   # Above 15 L→ 30 %
]

# Section 87A rebate: if taxable income is ≤ 7 L, the entire tax is waived
REBATE_87A_LIMIT = 7_00_000


def get_income_input() -> float:
    """Prompt the user for a positive annual income figure."""
    while True:
        raw = input("Enter your annual gross income (₹): ").strip()
        # Remove commas so users can type 10,00,000 or 1000000 interchangeably
        raw = raw.replace(",", "")
        try:
            income = float(raw)
        except ValueError:
            print("  ✗ Please enter a valid numeric amount.")
            continue
        if income < 0:
            print("  ✗ Income cannot be negative.")
            continue
        return income


def compute_tax(taxable_income: float) -> list[dict]:
    """
    Apply progressive slab taxation to taxable_income.

    Returns a list of dicts — one per slab — each containing:
        slab_label   : human-readable range string
        income_in_slab: amount of income that falls within this slab
        rate         : tax rate for this slab (0.0 – 1.0)
        tax          : tax payable for this slab
    """
    breakdown = []
    prev_ceiling = 0          # lower boundary of the current slab
    remaining    = taxable_income  # income not yet allocated to a slab

    for ceiling, rate in TAX_SLABS:
        if remaining <= 0:
            break  # all income has been allocated — no need to check further slabs

        # Width of this slab (infinite for the top slab)
        if ceiling is None:
            slab_width = remaining          # entire remaining income goes here
            slab_label = f"Above ₹{prev_ceiling // 1_00_000}L"
        else:
            slab_width = ceiling - prev_ceiling
            slab_label = (
                f"₹{prev_ceiling // 1_00_000}L – ₹{ceiling // 1_00_000}L"
                if prev_ceiling > 0
                else f"₹0 – ₹{ceiling // 1_00_000}L"
            )

        # Income that actually falls in this slab (can't exceed the slab width)
        income_in_slab = min(remaining, slab_width)
        tax_in_slab    = income_in_slab * rate

        breakdown.append({
            "slab_label":     slab_label,
            "income_in_slab": income_in_slab,
            "rate":           rate,
            "tax":            tax_in_slab,
        })

        remaining    -= income_in_slab   # move to the next slab
        prev_ceiling  = ceiling if ceiling else prev_ceiling

    return breakdown


def format_inr(amount: float) -> str:
    """Format a rupee amount with Indian-style comma grouping and ₹ prefix."""
    # Split into integer and decimal parts
    integer_part = int(amount)
    decimal_part = round(amount - integer_part, 2)

    s = str(integer_part)
    # Indian grouping: last 3 digits, then groups of 2
    if len(s) > 3:
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
    else:
        result = s

    if decimal_part:
        result += f".{int(decimal_part * 100):02d}"

    return f"₹{result}"


def print_report(gross_income: float) -> None:
    """Compute tax and print a full slab-wise breakdown report."""

    # Step 1: Apply standard deduction to get taxable income
    taxable_income = max(0, gross_income - STANDARD_DEDUCTION)

    # Step 2: Compute slab-wise tax
    breakdown = compute_tax(taxable_income)
    total_tax  = sum(row["tax"] for row in breakdown)

    # Step 3: Apply Section 87A rebate — wipes out tax if taxable income ≤ 7 L
    rebate_applied = taxable_income <= REBATE_87A_LIMIT
    if rebate_applied:
        tax_after_rebate = 0.0
        rebate_amount    = total_tax  # entire tax is rebated
    else:
        tax_after_rebate = total_tax
        rebate_amount    = 0.0

    # Step 4: Add 4% Health & Education Cess on tax after rebate
    cess = tax_after_rebate * 0.04
    final_tax = tax_after_rebate + cess

    # Effective rate is calculated on gross income (before standard deduction)
    effective_rate = (final_tax / gross_income * 100) if gross_income > 0 else 0

    # ── Report ────────────────────────────────────────────────────────────────
    W = 62   # total width of the report box
    print(f"\n{'═' * W}")
    print(f"{'INDIAN INCOME TAX CALCULATOR — NEW REGIME FY 2024-25':^{W}}")
    print(f"{'═' * W}")

    # Income summary
    print(f"  {'Gross Annual Income':<30}: {format_inr(gross_income):>20}")
    print(f"  {'Less: Standard Deduction':<30}: {format_inr(STANDARD_DEDUCTION):>20}")
    print(f"  {'Taxable Income':<30}: {format_inr(taxable_income):>20}")
    print(f"{'─' * W}")

    # Slab-wise breakdown header
    print(f"  {'SLAB':<18} {'INCOME IN SLAB':>14} {'RATE':>6}  {'TAX':>14}")
    print(f"  {'─'*18} {'─'*14} {'─'*6}  {'─'*14}")

    for row in breakdown:
        rate_str = f"{row['rate']*100:.0f}%"
        # Dim zero-tax slabs visually by showing a dash for ₹0 tax
        tax_str  = format_inr(row["tax"]) if row["tax"] > 0 else "—"
        print(
            f"  {row['slab_label']:<18} "
            f"{format_inr(row['income_in_slab']):>14} "
            f"{rate_str:>6}  "
            f"{tax_str:>14}"
        )

    print(f"{'─' * W}")
    print(f"  {'Tax Before Rebate':<30}: {format_inr(total_tax):>20}")

    # Show rebate line only when it actually applies
    if rebate_applied:
        print(f"  {'Rebate u/s 87A (income ≤ 7L)':<30}: -{format_inr(rebate_amount):>19}")
        print(f"  {'Tax After Rebate':<30}: {format_inr(tax_after_rebate):>20}")

    print(f"  {'Health & Education Cess (4%)':<30}: {format_inr(cess):>20}")
    print(f"{'═' * W}")
    print(f"  {'TOTAL TAX PAYABLE':<30}: {format_inr(final_tax):>20}")
    print(f"  {'Effective Tax Rate':<30}: {effective_rate:>19.2f}%")
    print(f"{'═' * W}\n")


def main() -> None:
    print("\n+----------------------------------------------------------+")
    print("|   INCOME TAX CALCULATOR — India New Regime FY 2024-25   |")
    print("+----------------------------------------------------------+")
    print("""  Slabs: 0%(0-3L)   |\n
         5%(3-7L)   |\n
         10%(7-10L) |\n
         15%(10-12L)|\n 
         20%(12-15L)|\n 
         30%(>15L)  |\n""")
    print("  Standard Deduction: ₹75,000  |  Rebate 87A: ≤ ₹7L\n")
    print("+----------------------------------------------------------+")

    # Allow the user to calculate tax for multiple income values in one run
    while True:
        try:
            gross_income = get_income_input()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye!")
            break

        print_report(gross_income)

        again = input("Calculate for another income? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("\nGoodbye!\n")
            break
        print()


if __name__ == "__main__":
    main()