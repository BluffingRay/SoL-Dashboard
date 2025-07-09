import streamlit as st
from styles import apply_styles
from auth import init_auth
from dashboard import dashboard, upload, about

# -------------------------------
# Streamlit App Configuration
# -------------------------------
st.set_page_config(
    page_title="USEP School of Law Dashboard",
    layout="wide"
)

# -------------------------------
# Initialize Authentication and Apply Custom Styles
# -------------------------------
# init_auth()
apply_styles()

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.markdown(
    "<div class='menu-title'>📚 Dashy</div>", 
    unsafe_allow_html=True
)

tabs = {
    "🏠 Dashboard": dashboard.show,   
    "📤 Upload Data": upload.show,
    "ℹ️ About": about.show   
}

# Handle sidebar navigation button clicks
for label, page_func in tabs.items():
    if st.sidebar.button(label, use_container_width=True, key=label):
        st.session_state.page = label 

# Set default page on initial load
if "page" not in st.session_state:
    st.session_state.page = list(tabs.keys())[0]

# -------------------------------
# Render Selected Page
# -------------------------------
tabs[st.session_state.page]()

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
  