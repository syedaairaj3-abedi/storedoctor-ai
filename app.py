import time
import pandas as pd
import streamlit as st

from questions import questions
from scoring import (
    calculate_questionnaire_scores,
    calculate_file_scores,
    merge_scores,
    get_maturity_level,
    get_problem_summary,
)
from recommendations import (
    get_opportunities,
    get_recommendations,
    build_priority_data,
    chat_reply,
    build_report_text,
)
from charts import (
    make_radar_chart,
    make_issue_severity_chart,
    make_priority_map,
    make_sales_trend_chart,
    make_top_products_chart,
)

st.set_page_config(
    page_title="StoreDoctor AI",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f8f3ff 0%, #f3ebff 45%, #efe5ff 100%);
}
.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero-card {
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(140, 105, 255, 0.18);
    padding: 1.6rem;
    border-radius: 28px;
    box-shadow: 0 14px 40px rgba(126, 87, 255, 0.08);
    margin-bottom: 1rem;
}
.soft-card {
    background: rgba(255,255,255,0.86);
    border: 1px solid rgba(140, 105, 255, 0.16);
    padding: 1.2rem;
    border-radius: 22px;
    box-shadow: 0 10px 28px rgba(126, 87, 255, 0.06);
    margin-bottom: 1rem;
}
.score-box {
    background: white;
    border-radius: 18px;
    padding: 1rem;
    border: 1px solid rgba(140, 105, 255, 0.12);
    box-shadow: 0 8px 20px rgba(126, 87, 255, 0.06);
    text-align: center;
}
.mastot-box {
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(245,236,255,0.95));
    border: 1px solid rgba(140, 105, 255, 0.18);
    border-radius: 22px;
    padding: 1rem;
    box-shadow: 0 10px 25px rgba(126, 87, 255, 0.07);
}
.opportunity-card {
    background: white;
    border-left: 5px solid #8b5cf6;
    padding: 1rem;
    border-radius: 16px;
    box-shadow: 0 8px 18px rgba(126, 87, 255, 0.06);
    margin-bottom: 0.8rem;
}
.plan-card {
    background: white;
    border: 1px solid rgba(140, 105, 255, 0.14);
    padding: 1rem;
    border-radius: 16px;
    box-shadow: 0 8px 18px rgba(126, 87, 255, 0.06);
}
.main-title {
    font-size: 3rem;
    font-weight: 800;
    color: #4c1d95;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 1.1rem;
    color: #6d5ea8;
    margin-bottom: 0.7rem;
}
</style>
""", unsafe_allow_html=True)


def parse_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None, None

    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        original_columns = list(df.columns)
        rename_map = {}
        for col in df.columns:
            c = col.strip().lower()
            if c in ["date", "day"]:
                rename_map[col] = "Date"
            elif c in ["time", "hour"]:
                rename_map[col] = "Time"
            elif c in ["product", "item"]:
                rename_map[col] = "Product"
            elif c in ["category"]:
                rename_map[col] = "Category"
            elif c in ["quantity", "qty", "units"]:
                rename_map[col] = "Quantity"
            elif c in ["revenue", "sales", "amount"]:
                rename_map[col] = "Revenue"
            elif c in ["discount", "discount_percent", "promo"]:
                rename_map[col] = "Discount"
            elif c in ["employee count", "employees", "staff_count", "staff"]:
                rename_map[col] = "Employee Count"

        df = df.rename(columns=rename_map)

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        return df, original_columns
    except Exception as e:
        return None, str(e)


def run_analysis_animation():
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("🤖 MASTOT is analyzing your store...")
    progress = st.progress(0)
    status = st.empty()

    steps = [
        "Reviewing store profile...",
        "Checking sales and traffic patterns...",
        "Evaluating staffing condition...",
        "Inspecting customer signals...",
        "Analyzing inventory and promotions...",
        "Detecting growth opportunities..."
    ]

    for i, msg in enumerate(steps, start=1):
        status.info(msg)
        progress.progress(min(i * 16, 100))
        time.sleep(0.22)

    status.success("Diagnosis complete.")
    st.markdown('</div>', unsafe_allow_html=True)


left, right = st.columns([2.4, 1])

with left:
    st.markdown("""
    <div class="hero-card">
        <div class="main-title">🩺 StoreDoctor AI</div>
        <div class="sub-title">Diagnose your store like a business doctor.</div>
        <p>
        Meet <b>MASTOT</b> — your AI store doctor robot. It reviews store conditions,
        detects pain points, highlights hidden opportunities, and suggests business treatments
        for sales, staffing, inventory, customers, promotions, and operations.
        </p>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="mastot-box">
        <h2 style="margin-top:0;">🤖 MASTOT</h2>
        <p><b>Role:</b> AI Store Doctor</p>
        <p>I help diagnose what’s hurting a store, what’s working, and what to improve next.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="soft-card">', unsafe_allow_html=True)
st.subheader("Choose Analysis Mode")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🔍 Diagnose My Store", use_container_width=True, help="Answer detailed operational questions and get a structured diagnosis."):
        st.session_state.mode = "diagnose"

with c2:
    if st.button("📂 Upload Sales Data", use_container_width=True, help="Upload CSV or Excel data for trend and performance analysis."):
        st.session_state.mode = "upload"

with c3:
    if st.button("⚡ Hybrid Analysis", use_container_width=True, help="Use both the diagnosis form and uploaded data for stronger insights."):
        st.session_state.mode = "hybrid"
st.markdown('</div>', unsafe_allow_html=True)

mode = st.session_state.get("mode", "diagnose")

st.markdown('<div class="soft-card">', unsafe_allow_html=True)
st.subheader("Optional Sales File Upload")
uploaded_file = st.file_uploader(
    "Upload CSV or Excel sales file",
    type=["csv", "xlsx", "xls"],
    help="Optional in Diagnose mode. Recommended in Upload and Hybrid mode."
)
df = None
original_columns = None
if uploaded_file is not None:
    df, original_columns = parse_uploaded_file(uploaded_file)
    if df is not None:
        st.success("Sales file loaded successfully.")
        st.caption(f"Detected columns: {', '.join(df.columns.astype(str))}")
    else:
        st.error(f"File could not be read. Details: {original_columns}")
st.markdown('</div>', unsafe_allow_html=True)

answers = None

if mode in ["diagnose", "hybrid"]:
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("Business Diagnosis")

    with st.expander("🏪 Store Profile", expanded=True):
        store_type = st.selectbox("What type of store do you run?", questions["store_type"])
        store_size = st.selectbox("Store size", questions["store_size"])
        locations = st.selectbox("How many store locations?", questions["locations"])
        years_operating = st.selectbox("How long has it been operating?", questions["years_operating"])

    with st.expander("📈 Sales & Traffic", expanded=True):
        sales_trend = st.selectbox("Are sales growing, stable, or declining?", questions["sales_trend"])
        busiest_time = st.selectbox("When is your busiest time?", questions["busiest_time"])
        slowest_time = st.selectbox("When is your slowest time?", questions["slowest_time"])
        slow_day = st.selectbox("What is your slowest day?", questions["slow_day"])

    with st.expander("👥 Customers", expanded=False):
        repeat_customers = st.selectbox("Do customers return often?", questions["repeat_customers"])
        customer_complaints = st.selectbox("Most common customer complaint?", questions["customer_complaints"])
        lines_busy_hours = st.selectbox("How often are there lines during busy hours?", questions["lines_busy_hours"])

    with st.expander("🧑‍💼 Staffing", expanded=False):
        employees_per_shift = st.selectbox("How many employees usually work per shift?", questions["employees_per_shift"])
        staffing_busy_hours = st.selectbox("During busy hours, staffing feels...", questions["staffing_busy_hours"])
        staffing_slow_hours = st.selectbox("During slow hours, staffing feels...", questions["staffing_slow_hours"])

    with st.expander("📦 Inventory & Ordering", expanded=False):
        inventory_problem = st.selectbox("Inventory situation?", questions["inventory_problem"])
        ordering_issue = st.selectbox("Ordering pattern issue?", questions["ordering_issue"])

    with st.expander("📣 Promotions & Retention", expanded=False):
        promotions = st.selectbox("How often do you run promotions?", questions["promotions"])
        promotion_effectiveness = st.selectbox("How effective are promotions?", questions["promotion_effectiveness"])
        loyalty_program = st.selectbox("Do you have a loyalty or repeat-visit program?", questions["loyalty_program"])

    with st.expander("🩹 Problem Solver Mode", expanded=True):
        main_problem = st.selectbox("What is your biggest problem right now?", questions["main_problem"])

    answers = {
        "store_type": store_type,
        "store_size": store_size,
        "locations": locations,
        "years_operating": years_operating,
        "sales_trend": sales_trend,
        "busiest_time": busiest_time,
        "slowest_time": slowest_time,
        "slow_day": slow_day,
        "repeat_customers": repeat_customers,
        "customer_complaints": customer_complaints,
        "lines_busy_hours": lines_busy_hours,
        "employees_per_shift": employees_per_shift,
        "staffing_busy_hours": staffing_busy_hours,
        "staffing_slow_hours": staffing_slow_hours,
        "inventory_problem": inventory_problem,
        "ordering_issue": ordering_issue,
        "promotions": promotions,
        "promotion_effectiveness": promotion_effectiveness,
        "loyalty_program": loyalty_program,
        "main_problem": main_problem,
    }
    st.markdown('</div>', unsafe_allow_html=True)

analyze_label = {
    "diagnose": "🩺 Diagnose My Store",
    "upload": "📂 Analyze Uploaded Data",
    "hybrid": "⚡ Run Hybrid Analysis"
}[mode]

if st.button(analyze_label, type="primary", use_container_width=True):
    if mode == "upload" and df is None:
        st.error("Please upload a sales file first for Upload mode.")
    elif mode == "hybrid" and df is None:
        st.error("Please upload a sales file for Hybrid mode.")
    else:
        run_analysis_animation()

        q_scores = calculate_questionnaire_scores(answers) if answers else None
        f_scores = calculate_file_scores(df) if df is not None else None
        scores = merge_scores(q_scores, f_scores, mode=mode)

        st.session_state.answers = answers or {}
        st.session_state.scores = scores
        st.session_state.mode = mode
        st.session_state.df = df

if "scores" in st.session_state:
    scores = st.session_state.scores
    answers = st.session_state.get("answers", {})
    df = st.session_state.get("df", None)
    mode = st.session_state.get("mode", "diagnose")

    maturity = get_maturity_level(scores)
    problems = get_problem_summary(scores)
    opportunities = get_opportunities(answers, scores)
    immediate, roots, growth, risks, track = get_recommendations(answers, scores)
    priority_data = build_priority_data(opportunities)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("Results Dashboard")
    st.caption("A structured diagnosis based on questionnaire answers, uploaded data, or both.")
    st.markdown('</div>', unsafe_allow_html=True)

    cols = st.columns(6)
    for col, (label, val) in zip(cols, scores.items()):
        with col:
            st.markdown(
                f"""
                <div class="score-box">
                    <div style="font-size:0.95rem; color:#6d5ea8;">{label}</div>
                    <div style="font-size:2rem; font-weight:800; color:#4c1d95;">{val}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("🏷️ Store Maturity Level")
        st.success(maturity)
        st.write("This label summarizes your current business condition based on score patterns and operational signals.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("🚨 Key Problems Detected")
        for p in problems:
            st.write(f"• {p}")
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("🕸️ Store Health Radar")
        st.plotly_chart(make_radar_chart(scores), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.subheader("📊 Issue Severity View")
        st.plotly_chart(make_issue_severity_chart(scores), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if df is not None:
        fc1, fc2 = st.columns(2)
        sales_fig = make_sales_trend_chart(df)
        top_products_fig = make_top_products_chart(df)

        if sales_fig:
            with fc1:
                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.subheader("📈 Sales Trend")
                st.plotly_chart(sales_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        if top_products_fig:
            with fc2:
                st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                st.subheader("🏆 Top Products")
                st.plotly_chart(top_products_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("💡 Growth Opportunity Engine")
    for card in opportunities:
        st.markdown(
            f"""
            <div class="opportunity-card">
                <h4 style="margin:0 0 0.3rem 0;">{card['title']}</h4>
                <p style="margin:0.2rem 0;"><b>What we noticed:</b> {card['note']}</p>
                <p style="margin:0.2rem 0;"><b>Suggested action:</b> {card['action']}</p>
                <p style="margin:0.2rem 0;"><b>Expected impact:</b> {card['impact']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("⭐ Opportunity Priority Map")
    st.plotly_chart(make_priority_map(priority_data), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "Immediate Actions",
        "Root Causes",
        "Growth Strategies",
        "Risk Alerts",
        "What to Track Next"
    ])

    with tabs[0]:
        for item in immediate:
            st.info(item)

    with tabs[1]:
        for item in roots:
            st.warning(item)

    with tabs[2]:
        for item in growth:
            st.success(item)

    with tabs[3]:
        for item in risks:
            st.error(item)

    with tabs[4]:
        for item in track:
            st.write(f"• {item}")

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("🔮 Scenario Simulator")
    st.caption("Try simple what-if decisions before making changes in the store.")
    ss1, ss2, ss3 = st.columns(3)

    with ss1:
        extra_staff = st.slider("Add extra staff in peak hours", 0, 3, 1)
    with ss2:
        promo_discount = st.slider("Promotion discount %", 0, 30, 10)
    with ss3:
        reduce_dead_stock = st.slider("Reduce slow inventory %", 0, 50, 15)

    est_service = min(20, extra_staff * 6)
    est_traffic = min(18, promo_discount // 2)
    est_turnover = min(20, reduce_dead_stock // 2)

    st.write(f"Estimated service speed improvement: **+{est_service}%**")
    st.write(f"Estimated traffic lift from promotion: **+{est_traffic}%**")
    st.write(f"Estimated inventory turnover improvement: **+{est_turnover}%**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Consultant Chat")
    user_q = st.text_input(
        "Ask MASTOT something about your store",
        placeholder="How do I improve weekday sales?"
    )
    if st.button("Ask MASTOT"):
        if user_q.strip():
            st.chat_message("user").write(user_q)
            st.chat_message("assistant").write(chat_reply(user_q, answers, scores))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.subheader("📅 Personalized 30-Day Action Plan")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown("""
        <div class="plan-card">
            <h4>Week 1</h4>
            <p>Track peak hours, wait times, and staffing mismatch.</p>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        slow_day = answers.get("slow_day", "your weaker day")
        st.markdown(f"""
        <div class="plan-card">
            <h4>Week 2</h4>
            <p>Test one focused promotion on <b>{slow_day}</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown("""
        <div class="plan-card">
            <h4>Week 3</h4>
            <p>Bundle slow-moving items with stronger products and improve shelf visibility.</p>
        </div>
        """, unsafe_allow_html=True)

    with p4:
        st.markdown("""
        <div class="plan-card">
            <h4>Week 4</h4>
            <p>Review changes in traffic, product movement, and service speed, then adjust strategy.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    report_text = build_report_text(
        mode=mode,
        ans=answers,
        scores=scores,
        maturity=maturity,
        problems=problems,
        opportunities=opportunities,
        immediate=immediate,
        roots=roots,
        growth=growth,
        risks=risks,
        track=track,
    )

    st.download_button(
        label="📄 Download Strategy Report",
        data=report_text,
        file_name="storedoctor_ai_strategy_report.txt",
        mime="text/plain",
        use_container_width=True
    )