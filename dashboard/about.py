import streamlit as st

def show():
    st.subheader("⚖️ About This Dashboard")

    st.markdown("""
        <div style='text-align: justify; text-indent: 2em; line-height: 1.6'>
            Welcome to the <strong>School of Law Analytics Dashboard</strong> — a platform designed to track, analyze, and visualize key academic metrics, including enrollment trends, graduation rates, cohort survival, and drop-out rates. Developed in <strong>2025</strong> by yours truly, <strong>Raymar M. Serondo</strong> and <strong>Yman Rey M. Fernandez</strong>, BS Computer Science - Data Science 3-A interns, as part of our summer internship at the University of Southeastern Philippines. Powered by <strong>Streamlit</strong>, <strong>Python</strong>, and our helpful assistant <strong>ChatGPT</strong>, the dashboard aims to support academic planning and data-driven decisions.
            <br><br>
            <hr>
            <strong>Version:</strong> 0.1st<br>
            <strong>Last Updated:</strong> July 2025
        </div>
    """, unsafe_allow_html=True)
