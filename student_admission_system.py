# University Student Admission Decision System
# Evaluates student eligibility based on academic and non-academic criteria.

# Minimum entrance scores differ by category to account for reserved quotas
CATEGORY_CUTOFFS = {
    "general": 75,  # highest bar — no quota benefit
    "obc":     65,  # 10-point relaxation for Other Backward Classes
    "sc_st":   55,  # 20-point relaxation for SC/ST students
}

# Every student must clear this GPA floor regardless of category
MIN_GPA = 7.0

# Students who score this high get an automatic scholarship — no other checks needed
SCHOLARSHIP_THRESHOLD = 95

# Bonus points added to entrance score before comparing against the cutoff
BONUS_RECOMMENDATION  = 5   # reward for having a faculty/employer endorsement
BONUS_EXTRACURRICULAR = 3   # reward for strong extracurricular involvement

# The extracurricular score must be strictly above this to earn the bonus
EXTRACURRICULAR_BONUS_THRESHOLD = 8


def get_float_input(prompt: str, min_val: float, max_val: float) -> float:
    # Keep asking until the user enters a valid number within the allowed range
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            # Non-numeric input — tell the user exactly what's expected
            print(f"  x Invalid input. Please enter a number between {min_val} and {max_val}.")
            continue
        if not (min_val <= value <= max_val):
            # Numeric but out of the valid range
            print(f"  x Value out of range. Must be between {min_val} and {max_val}.")
            continue
        return value


def get_yes_no_input(prompt: str) -> bool:
    # Accept both full words and single-letter shortcuts for convenience
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("yes", "y"):
            return True
        if raw in ("no", "n"):
            return False
        print("  x Please enter 'yes' or 'no'.")


def get_category_input(prompt: str) -> str:
    valid = list(CATEGORY_CUTOFFS.keys())
    while True:
        raw = input(prompt).strip().lower()
        # Normalise "sc/st" (with slash) to the internal key "sc_st"
        if raw == "sc/st":
            raw = "sc_st"
        if raw in valid:
            return raw
        print(f"  x Invalid category. Choose from: {', '.join(valid)}.")


def evaluate_admission(
    entrance_score: float,
    gpa: float,
    has_recommendation: bool,
    category: str,
    extracurricular_score: float,
) -> dict:
    bonus_parts: list[str] = []
    effective_score = entrance_score  # will be increased if bonuses apply

    # Scholarship rule takes highest priority — skip every other check
    if entrance_score >= SCHOLARSHIP_THRESHOLD:
        return {
            "result": "ADMITTED (Scholarship)",
            "bonus": "None (scholarship threshold met — bonuses not required)",
            "effective_score": entrance_score,
            "reason": (
                f"Entrance score {entrance_score} >= {SCHOLARSHIP_THRESHOLD}. "
                "Auto-admitted with scholarship regardless of other criteria."
            ),
        }

    # Add recommendation bonus if the student submitted a letter
    if has_recommendation:
        effective_score += BONUS_RECOMMENDATION
        bonus_parts.append(f"+{BONUS_RECOMMENDATION} (recommendation)")

    # Extracurricular bonus only kicks in for scores strictly above 8
    if extracurricular_score > EXTRACURRICULAR_BONUS_THRESHOLD:
        effective_score += BONUS_EXTRACURRICULAR
        bonus_parts.append(f"+{BONUS_EXTRACURRICULAR} (extracurricular)")

    # Summarise bonuses for the report; show "None" when no bonus was earned
    bonus_str = "  ".join(bonus_parts) if bonus_parts else "None"

    # Look up this student's category-specific entrance score cutoff
    cutoff = CATEGORY_CUTOFFS[category]
    category_label = category.upper().replace("_", "/")  # e.g. "SC_ST" -> "SC/ST"

    # Determine whether each criterion is individually satisfied
    gpa_ok   = gpa >= MIN_GPA               # must be True for admission or waitlist
    score_ok = effective_score >= cutoff    # effective score (after bonuses) vs cutoff

    # Decision matrix: combine both flags to pick the correct outcome
    if score_ok and gpa_ok:
        # Both criteria met — straightforward admission
        result = "ADMITTED (Regular)"
        reason = (
            f"Meets {category_label} cutoff ({effective_score:.1f} >= {cutoff}) "
            f"and GPA requirement ({gpa} >= {MIN_GPA})"
        )
    elif score_ok and not gpa_ok:
        # Good score but weak GPA — keep on waitlist in case seats open
        result = "WAITLISTED"
        reason = (
            f"Effective score {effective_score:.1f} meets the {category_label} "
            f"cutoff ({cutoff}), but GPA {gpa} is below the minimum of {MIN_GPA}."
        )
    elif not score_ok and gpa_ok:
        # GPA is fine but score falls short even after bonuses
        result = "REJECTED"
        reason = (
            f"Effective score {effective_score:.1f} is below the {category_label} "
            f"cutoff of {cutoff} (original score {entrance_score}, bonus {effective_score - entrance_score:+.0f})."
        )
    else:
        # Both criteria fail — definitive rejection with dual reason
        result = "REJECTED"
        reason = (
            f"Effective score {effective_score:.1f} is below the {category_label} "
            f"cutoff of {cutoff}, AND GPA {gpa} is below the minimum of {MIN_GPA}."
        )

    return {
        "result": result,
        "bonus": bonus_str,
        "effective_score": effective_score,
        "reason": reason,
    }


# Separator line reused in print_report to avoid repeating the magic number 52
DIVIDER = "-" * 52

def print_report(
    entrance_score, gpa, has_recommendation,
    category, extracurricular_score, decision: dict
) -> None:
    # Header block — student's raw inputs for quick reference
    print(f"\n{'=' * 52}")
    print("       UNIVERSITY ADMISSION DECISION REPORT")
    print(f"{'=' * 52}")
    print(f"  Entrance Score       : {entrance_score}")
    print(f"  GPA                  : {gpa}")
    print(f"  Recommendation       : {'Yes' if has_recommendation else 'No'}")
    print(f"  Category             : {category.upper().replace('_','/')}")
    print(f"  Extracurricular Score: {extracurricular_score}")
    print(DIVIDER)

    # Bonus and effective score section
    print(f"  Bonus Applied        : {decision['bonus']}")
    print(f"  Effective Score      : {decision['effective_score']:.1f}")
    print(DIVIDER)

    # Final verdict with the human-readable reason
    print(f"  Result  =>  {decision['result']}")
    print(f"  Reason  : {decision['reason']}")
    print(f"{'=' * 52}\n")


def main() -> None:
    print("\n+----------------------------------------------+")
    print("|   UNIVERSITY ADMISSION SCREENING TOOL        |")
    print("+----------------------------------------------+\n")
    print("Enter student details below.\n")

    # Loop so the operator can process multiple students in one session
    while True:
        try:
            # Collect and validate all five inputs before running any logic
            entrance_score        = get_float_input("Entrance Score (0-100)      : ", 0, 100)
            gpa                   = get_float_input("GPA (0-10)                  : ", 0, 10)
            has_recommendation    = get_yes_no_input("Recommendation Letter (yes/no): ")
            category              = get_category_input("Category (general/obc/sc_st): ")
            extracurricular_score = get_float_input("Extracurricular Score (0-10): ", 0, 10)
        except (EOFError, KeyboardInterrupt):
            # Graceful exit on Ctrl+C or piped input ending
            print("\n\nExiting. Goodbye!")
            break

        # Run the decision engine and display the formatted report
        decision = evaluate_admission(
            entrance_score, gpa, has_recommendation,
            category, extracurricular_score
        )
        print_report(
            entrance_score, gpa, has_recommendation,
            category, extracurricular_score, decision
        )

        # Ask whether to continue before looping back for the next student
        again = input("Evaluate another student? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("\nThank you for using the Admission Screening Tool. Goodbye!\n")
            break
        print()


if __name__ == "__main__":
    main()