import pandas as pd
import streamlit as st
from google import genai

st.set_page_config(page_title="AI-Supported Fairness in Workplace Recognition", layout="wide")
st.markdown("""
<style>
div[data-testid="stTabs"] button { font-size: 16px; }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.hero-wrap {
    position: relative;
    overflow: hidden;
    padding: 3rem 2.2rem;
    margin: 0.5rem 0 2rem 0;
    border: 1px solid rgba(169, 112, 255, 0.32);
    border-radius: 24px;
    background:
        radial-gradient(circle at 85% 15%, rgba(169,112,255,.25), transparent 32%),
        radial-gradient(circle at 10% 100%, rgba(97,54,170,.25), transparent 38%),
        linear-gradient(135deg, #171123 0%, #0B0812 75%);
    box-shadow: 0 12px 42px rgba(97,54,170,.16);
    animation: heroFadeIn .9s ease-out both;
}
.hero-wrap::before {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    right: -50px;
    top: -90px;
    border-radius: 50%;
    background: rgba(169,112,255,.2);
    filter: blur(40px);
    animation: heroGlow 7s ease-in-out infinite alternate;
}
.hero-eyebrow {
    position: relative;
    color: #C9A9FF;
    text-transform: uppercase;
    letter-spacing: .14em;
    font-size: .76rem;
    font-weight: 700;
}
.hero-title {
    position: relative;
    color: #F5F0FF;
    font-size: clamp(2rem, 5vw, 3.5rem);
    line-height: 1.1;
    font-weight: 800;
    margin: .8rem 0;
}
.hero-copy {
    position: relative;
    max-width: 620px;
    color: #C8BEDA;
    font-size: 1rem;
    line-height: 1.7;
}
.hero-cta {
    position: relative;
    display: inline-block;
    margin-top: 1.1rem;
    padding: .75rem 1.05rem;
    border-radius: 12px;
    border: 1px solid rgba(200,170,255,.45);
    background: linear-gradient(135deg, #A970FF, #7341CF);
    color: #FFFFFF !important;
    text-decoration: none !important;
    font-weight: 700;
    box-shadow: 0 0 24px rgba(169,112,255,.22);
    transition: transform .2s ease, box-shadow .2s ease;
}
.hero-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 32px rgba(169,112,255,.4);
}
@keyframes heroFadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes heroGlow {
    from { transform: translate(0, 0) scale(1); }
    to { transform: translate(-25px, 20px) scale(1.15); }
}
@media (prefers-reduced-motion: reduce) {
    .hero-wrap, .hero-wrap::before { animation: none; }
    .hero-cta { transition: none; }
}

/* Neon glow for metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        rgba(169, 112, 255, 0.10),
        rgba(23, 17, 35, 0.72)
    );
    border: 1px solid rgba(169, 112, 255, 0.22);
    border-radius: 16px;
    padding: 18px 20px;
    transition: border-color 0.25s ease, box-shadow 0.25s ease,
                transform 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(169, 112, 255, 0.7);
    box-shadow: 0 0 22px rgba(169, 112, 255, 0.16);
    transform: translateY(-3px);
}

div[data-testid="stMetric"] label {
    color: #C8BEDA !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #D8BDFF !important;
    font-weight: 750;
}

</style>

<div class="hero-wrap">
    <div class="hero-eyebrow">AI-SUPPORTED FAIRNESS · PEOPLE ANALYTICS</div>
    <div class="hero-title">Recognition that sees<br>every contribution.</div>
    <div class="hero-copy">
        Explore employee contributions, compare recognition patterns,
        and use AI-supported insights to ask better questions about
        workplace fairness.
    </div>
    <a class="hero-cta" href="#dashboard">Explore the dashboard ↓</a>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="dashboard"></div>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "👥 Employee Explorer",
    "📊 Recognition Insights",
    "🤖 AI Fairness Lab",
    "📁 Data & Reports"
])
st.caption("Prototype with sample data. AI suggests, the manager decides.")

# ---- API key (paste in sidebar, or set GEMINI_API_KEY in Streamlit secrets when deployed)
api_key = st.sidebar.text_input("Gemini API key", type="password")
if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# ---- Visible criteria (this is what builds perceived fairness)
CRITERIA = [
    "Tasks completed on time",
    "Quality of work (as noted in project logs)",
    "Helping teammates / collaboration",
    "Peer nominations",
]
st.sidebar.subheader("Recognition criteria (visible to all)")
for c in CRITERIA:
    st.sidebar.write("•", c)

# ---- Sample data (fake, no real employee info)
sample = pd.DataFrame(
    {
        "Employee": ["Asha", "Ravi", "Meera", "Karan", "Sana"],
        "Tasks completed": [12, 11, 12, 10, 13],
        "Peer nominations": [1, 4, 0, 3, 1],
        "Recognitions last 6 months": [0, 3, 0, 2, 1],
        "Contribution notes": [
            "Handled client escalations quietly, trained two new joiners",
            "Led the Q2 presentation, very visible to leadership",
            "Fixed recurring reporting errors, mostly behind the scenes",
            "Good teamwork, regularly speaks up in meetings",
            "Delivered most tasks early, helped Asha with a deadline",
        ],
    }
)

with tab5:
    st.markdown("## 📋 Employee Contribution Overview")
    st.caption(
        "Review employee activity and update the sample data "
        "to explore recognition patterns."
    )
    st.dataframe(sample, use_container_width=True)

    csv_data = sample.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Employee Data (CSV)",
        data=csv_data,
        file_name="employee_recognition_data.csv",
        mime="text/csv",
    )

st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: rgba(139, 112, 232, 0.14) !important;
    border: 1px solid rgba(139, 112, 232, 0.55) !important;
    border-radius: 16px !important;
    padding: 18px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("### ✨ Recognition at a glance")

data = sample.copy()

total_employees = len(data)
total_tasks = int(data["Tasks completed"].sum())
total_nominations = int(data["Peer nominations"].sum())
recognized_employees = int(
    (data["Recognitions last 6 months"] > 0).sum()
)
recognition_coverage = (
    recognized_employees / total_employees * 100
    if total_employees > 0
    else 0
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("👥 Employees", total_employees, border=True)

with c2:
    st.metric("✅ Tasks completed", total_tasks, border=True)

with c3:
    st.metric("🌟 Peer nominations", total_nominations, border=True)

c4, c5 = st.columns(2)

with c4:
    st.metric("🏆 Employees recognized", recognized_employees, border=True)

with c5:
    st.metric(
        "📈 Recognition coverage",
        f"{recognition_coverage:.0f}%",
        border=True,
        help="Percentage of employees who received at least one recognition in the last six months."
    )



st.markdown("## 📊 Recognition & Contribution Patterns")
st.caption(
    "Compare completed tasks with recognition received "
    "over the last six months."
)

chart_data = data.set_index("Employee")[
    ["Tasks completed", "Recognitions last 6 months"]
]

st.bar_chart(
    chart_data,
    color=["#8B70E8", "#49BFB0"],
    use_container_width=True,
)
st.caption(
    "💡 Tip: Compare completed tasks with recognition received. "
    "High contribution with low recognition may be worth reviewing "
    "before drawing conclusions about fairness."
)
st.markdown("### 🔎 Contribution vs. Recognition")

st.caption(
    "Explore whether employees with more completed tasks "
    "also tend to receive more recognition."
)

st.scatter_chart(
    data,
    x="Tasks completed",
    y="Recognitions last 6 months",
    use_container_width=True,
)

st.caption(
    "💡 Employees with high contributions but lower recognition "
    "may warrant further review. This pattern alone does not prove bias."
)

# ---- AI step
st.subheader("3. AI summary for the manager")
if st.button("Generate summary"):
    if not api_key:
        st.warning("Add your Gemini API key in the sidebar first.")
    else:
        prompt = f"""
You support a manager in a fair employee recognition process. You do NOT make decisions.

Criteria: {", ".join(CRITERIA)}

Employee data:
{data.to_csv(index=False)}

Do the following, in simple language:
1. Give each employee a 1-2 line evidence summary based only on the data.
2. Flag anyone whose contribution looks similar to others but who got less recognition.
3. Point out possible bias (e.g. visibility, peer nominations favouring louder people).
4. List what the data cannot show that the manager should consider.
End by saying the final decision belongs to the manager.
"""
            
try:
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an organisational behaviour analyst helping assess
fairness in workplace recognition.

Analyse the following employee contribution data:

{data.to_string(index=False)}

Write a concise, professional report with these sections:

1. Overall observations: Summarise contribution and recognition patterns.
2. Potential gaps: Identify employees or patterns that may deserve
   a closer review, comparing completed tasks and recognitions.
3. Fairness considerations: Explain why differences alone do not
   prove bias or unfair treatment.
4. Recommendations: Suggest practical ways to make recognition
   more transparent, consistent, and fair.

Use only the data provided. Do not invent employee details,
assume motivations, or make definitive claims about bias.
"""
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    if response.text:
        st.session_state["summary"] = response.text
        st.session_state.pop("summary_error", None)
    else:
        st.session_state["summary_error"] = (
            "The AI returned an empty response. Please try again."
        )

except Exception as e:
    st.session_state["summary_error"] = (
        "The AI service is temporarily unavailable. "
        "Please wait a minute and try again."
    )
    st.session_state.pop("summary", None)
    print(f"Gemini API error: {e}")

if "summary_error" in st.session_state:
    st.warning(st.session_state["summary_error"])

if "summary" in st.session_state:
    st.markdown(st.session_state["summary"])


# ---- Human decision
st.subheader("4. Manager decision (human judgment)")
choice = st.selectbox("Who gets recognised this cycle?", data["Employee"].tolist())
reason = st.text_area("Reason (shared with the team so the decision is transparent)")
if st.button("Confirm recognition"):
    if reason.strip():
        st.success(f"{choice} recognised. Reason shared: {reason}")
    else:
        st.warning("Add a reason so the decision is transparent.")

st.caption("Employees can appeal a decision by contacting HR. AI output is audited regularly for bias.")
