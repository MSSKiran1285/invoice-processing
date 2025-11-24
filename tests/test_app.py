import importlib


def test_app_imports():
    """
    Smoke test: Streamlit app module should import without errors.

    We *don’t* run Streamlit here, we just make sure that importing the
    module does not explode (missing imports, syntax errors, etc.).
    """
    mod = importlib.import_module("app")
    assert mod is not None
