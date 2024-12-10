import streamlit as st


def Navbar():
    """Creates a navigation bar for a Streamlit multipage application.

    This function creates a sidebar containing the application title, logo,
    and navigation links to other pages defined in the Streamlit app.

    Returns:
        None
    """
    with st.sidebar:
        st.sidebar.title("Radiographie Pulmonaire")
        st.sidebar.image("src/streamlit/resources/x-ray.png", use_container_width=True)
        st.page_link("app.py", label="Application", icon="🚀")  # 🚀🔥
        st.page_link("pages/context.py", label="Contexte", icon="🧩")  # 📚🖼️
        st.page_link(
            "pages/data_discovery.py", label="Découverte des données", icon="🔍"
        )
        st.page_link("pages/acp.py", label="ACP sur les données", icon="🎯")  # 🧮🔵
        st.page_link("pages/model.py", label="Modélisation", icon="📊")  # 🤖🛠️
