# Rule-based fraud detection engine for a fintech startup.
# Evaluates each transaction against blocking, flagging, and category rules.

# These caps are defined per business policy; "other" and "travel" are uncapped at the category level (they still hit the global single-transaction limit).
BASE_LIMITS = {
    "food":        5_000,
    "electronics": 30_000,
    "travel":      None,   # no category-level cap for travel
    "other":       None,   # no category-level cap for other
}

# Global hard limits that apply regardless of category
SINGLE_TXN_LIMIT = 50_000
DAILY_LIMIT      = 1_00_000

# Transactions outside this hour window are automatically flagged as unusual
SAFE_HOUR_START = 6   # 06:00 — earliest "normal" hour
SAFE_HOUR_END   = 23  # 23:00 — latest "normal" hour (23:59 is still flagged)

def get_float_input(prompt: str, min_val: float = 0) -> float:
    # Keeps asking until the user types a valid number at or above min_val
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            print("  x Please enter a valid number.")
            continue
        if value < min_val:
            print(f"  x Value must be ≥ {min_val}.")
            continue
        return value


def get_category_input() -> str:
    # Loops until the user picks one of the four accepted category names
    valid = list(BASE_LIMITS.keys())
    while True:
        raw = input(f"Category ({'/'.join(valid)}): ").strip().lower()
        if raw in valid:
            return raw
        print(f"  x Invalid category. Choose from: {', '.join(valid)}.")


def get_hour_input() -> int:
    # Rejects non-integers and values outside 0-23
    while True:
        raw = input("Hour of transaction (0–23): ").strip()
        try:
            hour = int(raw)
        except ValueError:
            print("  x Please enter a whole number between 0 and 23.")
            continue
        if not (0 <= hour <= 23):
            print("  x Hour must be between 0 and 23.")
            continue
        return hour


def get_vip_input() -> bool:
    # Returns True for yes/y, False for no/n; anything else re-prompts
    while True:
        raw = input("Is this a VIP customer? (yes/no): ").strip().lower()
        if raw in ("yes", "y"):
            return True
        if raw in ("no", "n"):
            return False
        print("  x Please enter 'yes' or 'no'.")


def evaluate_transaction(
    amount: float,
    category: str,
    hour: int,
    daily_spent: float,
    is_vip: bool,
) -> tuple[str, str]:
    # Returns (status, reason): BLOCKED > FLAGGED > APPROVED in priority order

    # VIP customers get doubled limits on every threshold — ternary sets this
    # in a single readable line rather than duplicating all the if/else logic.
    multiplier      = 2 if is_vip else 1
    single_limit    = SINGLE_TXN_LIMIT * multiplier
    daily_cap       = DAILY_LIMIT      * multiplier

    # Resolve the category cap; None means no category-level limit applies
    base_cat_limit  = BASE_LIMITS.get(category)
    category_limit  = (base_cat_limit * multiplier) if base_cat_limit else None

    projected_daily = daily_spent + amount  # total spend if this txn goes through

    # Rule 1a: Single transaction exceeds the hard limit
    if amount > single_limit:
        return (
            "BLOCKED",
            f"exceeds single transaction limit "
            f"(Rs.{amount:,.0f} > Rs.{single_limit:,.0f})"
        )

    # Rule 1b: This transaction would push the daily total over the cap
    if projected_daily > daily_cap:
        return (
            "BLOCKED",
            f"would exceed daily spending limit "
            f"(Rs.{projected_daily:,.0f} > Rs.{daily_cap:,.0f})"
        )


    # Rule 3: Category-specific cap — only applies to food and electronics
    if category_limit is not None and amount > category_limit:
        return (
            "BLOCKED",
            f"exceeds {category} category limit "
            f"(Rs.{amount:,.0f} > Rs.{category_limit:,.0f})"
        )


    # Rule 2: Transactions before 6 AM or at/after 11 PM are unusual
    if hour < SAFE_HOUR_START or hour >= SAFE_HOUR_END:
        time_str = f"{hour:02d}:00"
        return (
            "FLAGGED",
            f"unusual transaction hour ({time_str} is outside 06:00–23:00)"
        )

    return ("APPROVED", "")



def print_result(
    amount: float,
    category: str,
    hour: int,
    daily_spent: float,
    is_vip: bool,
    status: str,
    reason: str,
) -> None:
    # Formats and prints the transaction details and its final verdict

    # Build the transaction description string
    vip_tag = " [VIP]" if is_vip else ""
    txn_desc = (
        f"Rs.{amount:,.0f} {category} transaction at {hour:02d}:00"
        f"{vip_tag}"
    )

    # Append reason for non-approved outcomes
    outcome = status if status == "APPROVED" else f"{status}: {reason}"

    print(f"\n  Transaction: {txn_desc}")
    print(f"  Result     : {outcome}\n")

def main() -> None:
    print("\n+----------------------------------------------------------+")
    print("|            FRAUD DETECTION - TRANSACTION CHECKER         |")
    print("+----------------------------------------------------------+")

    # Allow processing multiple transactions in one session
    while True:
        try:
            amount       = get_float_input("Transaction amount (Rs): ", min_val=1)
            category     = get_category_input()
            hour         = get_hour_input()
            daily_spent  = get_float_input("Amount already spent today (Rs): ", min_val=0)
            is_vip       = get_vip_input()
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting. Goodbye!")
            break

        status, reason = evaluate_transaction(amount, category, hour, daily_spent, is_vip)
        print_result(amount, category, hour, daily_spent, is_vip, status, reason)

        again = input("Check another transaction? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("\nSession ended. Goodbye!\n")
            break
        print()


if __name__ == "__main__":
    main()