from scoring import get_maturity_level


def get_opportunities(ans, scores):
    cards = []

    if ans and ans.get("slow_day") in ["Monday", "Tuesday", "Wednesday"]:
        cards.append({
            "title": "Midweek Recovery Opportunity",
            "note": f"Weak traffic is likely on {ans['slow_day']}.",
            "action": f"Launch a limited-time offer on {ans['slow_day']} to lift weak-day sales.",
            "impact": "Potential improvement in low-traffic day performance."
        })

    if ans and ans.get("inventory_problem") in ["Slow-moving items", "Both slow items and stockouts"]:
        cards.append({
            "title": "Product Bundling Opportunity",
            "note": "Slow-moving items may be taking shelf space without driving enough revenue.",
            "action": "Bundle slow items with best-sellers or move them near checkout.",
            "impact": "Improved stock turnover and better shelf efficiency."
        })

    if ans and ans.get("staffing_busy_hours") == "Understaffed":
        cards.append({
            "title": "Peak Hour Staffing Opportunity",
            "note": f"Your busiest period is {ans['busiest_time']}, but staffing appears weak then.",
            "action": f"Add or reassign staff during {ans['busiest_time']} shifts.",
            "impact": "Better service speed and lower customer drop-off."
        })

    if ans and (ans.get("promotions") == "Never" or ans.get("promotion_effectiveness") in ["Not effective", "Not sure"]):
        cards.append({
            "title": "Promotion Strategy Opportunity",
            "note": "Promotional activity is limited or unclear in effectiveness.",
            "action": "Test one focused weekly promotion instead of broad random discounts.",
            "impact": "Stronger promotional learning and better traffic response."
        })

    if ans and ans.get("loyalty_program") == "No":
        cards.append({
            "title": "Repeat Customer Opportunity",
            "note": "No loyalty program is currently helping bring customers back.",
            "action": "Introduce a simple loyalty reward or repeat-visit offer.",
            "impact": "Higher repeat customer rate over time."
        })

    if not cards:
        cards.append({
            "title": "Optimization Opportunity",
            "note": "Your store looks fairly stable overall.",
            "action": "Focus on small experiments in pricing, staffing, or promotions.",
            "impact": "Incremental growth and smarter operations."
        })

    return cards[:4]


def get_recommendations(ans, scores):
    immediate = []
    roots = []
    growth = []
    risks = []
    track = []

    if ans:
        if ans.get("staffing_busy_hours") == "Understaffed":
            immediate.append(f"Add one more employee or shift coverage during {ans['busiest_time']} hours.")
            roots.append("Busy-hour staffing appears lower than customer demand.")
            risks.append("Long wait times may reduce completed purchases.")

        if ans.get("inventory_problem") in ["Slow-moving items", "Both slow items and stockouts"]:
            immediate.append("Move slow products to visible zones or pair them with best-sellers.")
            roots.append("Some inventory may not match actual customer demand.")
            risks.append("Dead stock may tie up cash and shelf space.")

        if ans.get("inventory_problem") in ["Frequent stockouts", "Both slow items and stockouts"]:
            immediate.append("Review reordering rules for fast-moving products.")
            roots.append("Ordering may not align with actual demand spikes.")
            risks.append("Stockouts can directly reduce sales and customer trust.")

        if ans.get("promotions") == "Never":
            immediate.append(f"Run one test promotion on {ans['slow_day']}.")
            roots.append("Weak low-day traffic may be linked to no targeted promotion strategy.")
            growth.append("Build a weekly targeted offer calendar instead of random discounts.")

        if ans.get("repeat_customers") == "Rarely":
            immediate.append("Introduce a repeat-visit or loyalty offer.")
            roots.append("The store may be relying too much on one-time traffic.")
            growth.append("Use loyalty incentives to increase repeat purchases.")

    growth.append("Track which products perform best by time of day.")
    growth.append("Test bundles that combine fast and slow-moving products.")
    growth.append("Build staffing schedules around peak traffic periods.")

    track.extend([
        "Repeat customer rate",
        "Average order value",
        "Stockout frequency",
        "Sales by day and hour",
        "Conversion rate during peak hours"
    ])

    if not immediate:
        immediate.append("Maintain current performance while testing one improvement per week.")
    if not roots:
        roots.append("Current answers suggest the store is stable but still under-optimized.")
    if not risks:
        risks.append("Without regular tracking, small inefficiencies can grow over time.")

    return immediate[:4], roots[:3], growth[:4], risks[:3], track[:5]


def build_priority_data(opportunities):
    data = []
    for card in opportunities:
        title = card["title"]
        if "Staffing" in title or "Midweek" in title:
            impact, effort = 9, 5
        elif "Promotion" in title:
            impact, effort = 8, 4
        elif "Product" in title:
            impact, effort = 7, 4
        else:
            impact, effort = 6, 3
        data.append({"Opportunity": title, "Impact": impact, "Effort": effort})
    return data


def chat_reply(question, ans, scores):
    q = question.lower()

    if "weekday" in q or "slow day" in q or "sales" in q:
        slow_day = ans.get("slow_day", "your weakest day")
        return f"Your weakest day appears to be {slow_day}. I’d test a targeted offer on that day, improve product visibility, and monitor traffic before and after the offer."

    if "hire" in q or "employee" in q or "staff" in q:
        if ans and ans.get("staffing_busy_hours") == "Understaffed":
            return f"Yes — your answers suggest understaffing during {ans['busiest_time']}. Start by adding one extra person in peak hours before increasing headcount everywhere."
        return "Your store does not strongly signal a major hiring need yet. First optimize shift timing before adding more staff."

    if "slow product" in q or "inventory" in q:
        return "Bundle slow products with popular items, place them in higher-visibility areas, and consider reducing reorder quantity until movement improves."

    if "promotion" in q or "discount" in q:
        if ans:
            return f"A good test would be a small promotion on {ans.get('slow_day', 'your weaker day')}, especially during your slower period of {ans.get('slowest_time', 'off-peak hours')}."
        return "Start with one narrow weekly promotion and compare before-and-after traffic."

    return f"Based on your current diagnosis, your store maturity level is {get_maturity_level(scores)}. I’d prioritize staffing alignment, targeted promotions, and tracking repeat customers first."


def build_report_text(mode, ans, scores, maturity, problems, opportunities, immediate, roots, growth, risks, track):
    lines = []
    lines.append("STOREDOCTOR AI - STRATEGY REPORT")
    lines.append("=" * 40)
    lines.append(f"Analysis Mode: {mode.title()}")
    lines.append(f"Store Maturity Level: {maturity}")
    lines.append("")
    lines.append("BUSINESS HEALTH SCORES")
    for k, v in scores.items():
        lines.append(f"- {k}: {v}/100")
    lines.append("")
    lines.append("KEY PROBLEMS")
    for item in problems:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("GROWTH OPPORTUNITIES")
    for card in opportunities:
        lines.append(f"- {card['title']}: {card['action']}")
    lines.append("")
    lines.append("IMMEDIATE ACTIONS")
    for item in immediate:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("ROOT CAUSE INSIGHTS")
    for item in roots:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("GROWTH STRATEGIES")
    for item in growth:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("RISK ALERTS")
    for item in risks:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("WHAT TO TRACK NEXT")
    for item in track:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("30-DAY PLAN")
    lines.append("- Week 1: Track peak hours, wait times, and staffing mismatch.")
    lines.append("- Week 2: Launch one focused promotion on a weaker day.")
    lines.append("- Week 3: Bundle slow-moving products with stronger items.")
    lines.append("- Week 4: Review results and refine pricing, staffing, and inventory.")
    return "\n".join(lines)