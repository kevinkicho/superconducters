import streamlit_dashboard


def test_dashboard_imports_without_optional_ui_dependencies():
    assert callable(streamlit_dashboard.main)
