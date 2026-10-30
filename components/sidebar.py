
import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div class="brand-container">
                <div class="brand-icon">⚡</div>
                <div>
                    <div class="brand-name">FlowCraft AI</div>
                    <div class="brand-subtitle">SMART WORKFLOW STUDIO</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.markdown(
            '<p class="sidebar-heading">WORKSPACE</p>',
            unsafe_allow_html=True
        )

        selected = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Workflow History",
                "Templates",
                "About FlowCraft"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")

        st.markdown(
            """
            <div class="sidebar-info">
                <div class="status-dot"></div>
                <span>System Ready</span>
                <br><br>
                <small>AI Workflow Engine</small>
                <small>Version 1.0.0</small>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="sidebar-footer">
                Built with Python & AI<br>
                FlowCraft AI © 2026
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected
