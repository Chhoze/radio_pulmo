import streamlit as st


def Navbar():
    with st.sidebar:
        st.sidebar.title("Radiographie Pulmonaire")
        st.sidebar.image("resources/x-ray.png", use_container_width=True)
        st.page_link('app.py', label='Application', icon='🚀') # 🚀🔥
        st.page_link('pages/context.py', label='Contexte', icon='🧩') # 📚🖼️
        st.page_link('pages/data_discovery.py', label='Découverte des données', icon='🔍')
        st.page_link('pages/model.py', label='Modélisation', icon='📊') #🤖🛠️