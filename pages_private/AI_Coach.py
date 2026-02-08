# pages_private/AI_Coach.py

import streamlit as st
from utils.ai_coach import get_fake_ai_report

def run():
    report = get_fake_ai_report()

    st.subheader("🧠 Insight Report")
    st.write(report["insights"])

    st.subheader("🏆 Weekly Personal Plan")
    st.write(report["weekly_plan"])

    st.subheader("🎯 Smart Suggestions")
    for s in report["suggestions"]:
        st.write(f"- {s}")

    st.subheader("🔥 Progress Analysis")
    st.write(report["progress"])

    st.subheader("📈 Projections & Alerts")
    st.write(f"**Proyección:** {report['projections_and_alerts']['projection']}")

    st.write("**Alertas:**")
    for a in report["projections_and_alerts"]["alerts"]:
        st.write(f"- {a}")
