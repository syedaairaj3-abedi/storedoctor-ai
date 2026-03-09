def clamp(value, low=35, high=98):
    return max(low, min(high, value))


def calculate_questionnaire_scores(ans):
    sales = 70
    staffing = 70
    inventory = 70
    customers = 70
    promotions = 70
    operations = 70

    if ans["sales_trend"] == "Growing":
        sales += 18
    elif ans["sales_trend"] == "Stable":
        sales += 5
    else:
        sales -= 18

    if ans["repeat_customers"] == "Very often":
        customers += 18
    elif ans["repeat_customers"] == "Sometimes":
        customers += 5
    else:
        customers -= 15

    if ans["customer_complaints"] == "None":
        customers += 10
        operations += 8
    elif ans["customer_complaints"] == "Long wait times":
        staffing -= 15
        operations -= 10
    elif ans["customer_complaints"] == "High prices":
        sales -= 8
    elif ans["customer_complaints"] == "Product availability":
        inventory -= 15
    elif ans["customer_complaints"] == "Poor service":
        customers -= 15
        operations -= 10
    else:
        customers -= 10
        operations -= 10

    if ans["staffing_busy_hours"] == "Understaffed":
        staffing -= 18
        operations -= 10
    elif ans["staffing_busy_hours"] == "Overstaffed":
        staffing -= 8

    if ans["staffing_slow_hours"] == "Overstaffed":
        staffing -= 12
        operations -= 6

    if ans["lines_busy_hours"] == "Often":
        staffing -= 12
        customers -= 8
    elif ans["lines_busy_hours"] == "Sometimes":
        staffing -= 5

    if ans["inventory_problem"] == "No issues":
        inventory += 15
    elif ans["inventory_problem"] == "Slow-moving items":
        inventory -= 12
    elif ans["inventory_problem"] == "Frequent stockouts":
        inventory -= 15
        sales -= 8
    else:
        inventory -= 20
        sales -= 10

    if ans["ordering_issue"] == "No issue":
        inventory += 8
    elif ans["ordering_issue"] == "Overordering":
        inventory -= 10
    elif ans["ordering_issue"] == "Underordering":
        inventory -= 10
        sales -= 6
    else:
        inventory -= 14

    if ans["promotions"] == "Frequently":
        promotions += 15
    elif ans["promotions"] == "Sometimes":
        promotions += 5
    else:
        promotions -= 15

    if ans["promotion_effectiveness"] == "Very effective":
        promotions += 12
        sales += 8
    elif ans["promotion_effectiveness"] == "Somewhat effective":
        promotions += 5
    elif ans["promotion_effectiveness"] == "Not effective":
        promotions -= 12
    else:
        promotions -= 5

    if ans["loyalty_program"] == "Yes":
        customers += 8
        promotions += 5
    else:
        customers -= 6

    scores = {
        "Sales": clamp(sales),
        "Staffing": clamp(staffing),
        "Inventory": clamp(inventory),
        "Customers": clamp(customers),
        "Promotions": clamp(promotions),
        "Operations": clamp(operations),
    }
    return scores


def calculate_file_scores(df):
    scores = {
        "Sales": 70,
        "Staffing": 65,
        "Inventory": 65,
        "Customers": 65,
        "Promotions": 60,
        "Operations": 68,
    }

    if df is None or df.empty:
        return scores

    if "Revenue" in df.columns:
        revenue = df["Revenue"].fillna(0)
        if revenue.mean() > 0:
            scores["Sales"] += 10
        if revenue.std() > 0:
            scores["Operations"] -= 3

    if "Discount" in df.columns:
        avg_discount = df["Discount"].fillna(0).mean()
        if avg_discount > 0:
            scores["Promotions"] += 8

    if "Employee Count" in df.columns and "Revenue" in df.columns:
        emp_avg = df["Employee Count"].fillna(0).mean()
        rev_avg = df["Revenue"].fillna(0).mean()
        if emp_avg > 0 and rev_avg > 0:
            scores["Staffing"] += 5

    for key in scores:
        scores[key] = clamp(scores[key])

    return scores


def merge_scores(question_scores=None, file_scores=None, mode="diagnose"):
    if mode == "upload" and file_scores:
        return file_scores

    if mode == "hybrid" and question_scores and file_scores:
        merged = {}
        for key in question_scores:
            merged[key] = round((question_scores[key] * 0.6) + (file_scores.get(key, question_scores[key]) * 0.4))
        return merged

    return question_scores or file_scores or {
        "Sales": 70,
        "Staffing": 70,
        "Inventory": 70,
        "Customers": 70,
        "Promotions": 70,
        "Operations": 70,
    }


def get_maturity_level(scores):
    avg = sum(scores.values()) / len(scores)
    if avg >= 84:
        return "Growth Ready"
    if avg >= 75:
        return "Stable"
    if avg >= 66:
        return "High Potential but Under-Optimized"
    if avg >= 55:
        return "Operationally Inefficient"
    return "Early Stage"


def get_problem_summary(scores):
    issues = []
    if scores["Sales"] < 65:
        issues.append("Weak sales performance")
    if scores["Staffing"] < 65:
        issues.append("Staffing mismatch")
    if scores["Inventory"] < 65:
        issues.append("Inventory inefficiency")
    if scores["Customers"] < 65:
        issues.append("Customer retention or service issues")
    if scores["Promotions"] < 65:
        issues.append("Weak promotion strategy")
    if scores["Operations"] < 65:
        issues.append("Operational inefficiency")

    if not issues:
        issues.append("Store is performing relatively well, with optimization opportunities")

    return issues[:3]