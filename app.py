import streamlit as st

from auth import check_password


if check_password():
    st.write("Here goes your normal Streamlit app...")
    st.button("Click me")

    st.write("# Welcome to Streamlit! 👋")

    st.sidebar.success("Select a demo above.")
