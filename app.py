import pandas as pd
import streamlit as st
from google import genai

st.set_page_config(page_title="AI-Supported Fairness in Workplace Recognition", layout="wide")
st.markdown("""
# ✨ People & Recognition Analytics

Understand employee contributions. Explore recognition patterns.
Build a fairer workplace.
""")

st.caption(
    "AI-Supported Fairness in Workplace Recognition"
)
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
