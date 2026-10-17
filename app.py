import pandas as pd
import streamlit as st
from google import genai

st.set_page_config(page_title="AI-Supported Fairness in Workplace Recognition", layout="wide")
st.title("AI-Supported Fairness in Workplace Recognition")
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

st.subheader("1. Contribution data")
data = st.data_editor(sample, num_rows="dynamic", use_container_width=True)


st.subheader("2. Recognition spread")

chart_data = data.set_index("Employee")[
    ["Tasks completed", "Recognitions last 6 months"]
]

st.bar_chart(
    chart_data,
    color=["#8B70E8", "#49BFB0"],
    use_container_width=True,
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
