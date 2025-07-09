import streamlit as st

def apply_styles():
    """Apply custom CSS styles and branding to the Streamlit app."""

    # ---------------------------------------
    # General placeholder for additional CSS
    # ---------------------------------------
    st.markdown("""<style>/* all your CSS goes here */</style>""", unsafe_allow_html=True)

    # ---------------------------------------
    # Header Banner (Top Branding Bar)
    # ---------------------------------------

    def apply_styles():
        with open("banner.svg", "r", encoding="utf-8") as f:
            svg_content = f.read()

        st.markdown(
            f"""
            <style>
            .full-width-svg-container svg {{
                width: 100% !important;
                height: auto !important;
            }} 
            </style>
            <div class="full-width-svg-container" style="margin-bottom: 0.5rem;">
                {svg_content}
            </div>
            """,
            unsafe_allow_html=True
        )

    apply_styles()


    # ---------------------------------------
    # KPI Metric Card Styles
    # ---------------------------------------
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
            margin-bottom: 10px;
        }
        .metric-title {
            font-size: 18px;
            color: #888;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #551012;
        }
        .metric-change {
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------
    # Sidebar Styling and Custom Tabs
    # ---------------------------------------
    st.markdown("""
        <style>
        /* Sidebar container background */
        section[data-testid="stSidebar"] {
            background-color: #551012 !important;
        }

        /* Remove padding from sidebar inner container */
        section[data-testid="stSidebar"] > div:first-child {
            padding: 2rem 1rem;
        }

        /* Sidebar title */
        .menu-title {
            color: white;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        /* Base tab/button style */
        .menu-tab {
            background-color: #6c1a1a;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-weight: 500;
            cursor: pointer;
            display: block;
            text-align: left;
            border: none;
            transition: background-color 0.2s ease;
        }

        /* Hover effect */
        .menu-tab:hover {
            background-color: #822020;
        }

        /* Active tab styling */
        .menu-tab-active {
            background-color: #992525 !important;
            border-left: 5px solid #ffcccb;
        }

        /* Press/click effect */
        .menu-tab:active {
            background-color: #a12d2d;
        }
        </style>
    """, unsafe_allow_html=True)
