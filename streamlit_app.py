import streamlit as st

# Set page config
st.set_page_config(page_title="IST688_Labs", page_icon="✏️")

# Define pages
Lab_1 = st.Page("lab1.py", title="Lab 1")
Lab_2 = st.Page("lab2.py", title="Lab 2")

# Set up navigation
pages = [Lab_1, Lab_2]
page = st.navigation(pages)

# Check if a page is selected, otherwise set default
if page is None:
    page = Lab_2

# Run the selected page
page.run()
