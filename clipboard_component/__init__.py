import os
import streamlit.components.v1 as components
import streamlit as st

# Get the directory path
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")

# Declare components
_paste_component_func = components.declare_component("paste_component", path=build_dir)
_copy_component_func = components.declare_component("copy_component", path=build_dir)

# Create a wrapper function for the component. This is an optional
# best practice - we could simply expose the component function returned by
# `declare_component` and call it done. The wrapper allows us to customize
# our component's API: we can pre-process its input args, post-process its
# output value, and add a docstring for users.
def paste_component(
    name: str,
    disabled: bool = False,
    styles: dict = None
) -> str:
    """Custom clipboard button with full styling control."""
    if 'clipboard_processed' not in st.session_state:
        st.session_state.clipboard_processed = 0

    component_value = _paste_component_func(
        name=name,
        disabled=disabled,
        styles=styles or {}
    )

    if not component_value or 'timestamp' not in component_value:
        return None

    if component_value['timestamp'] > st.session_state.clipboard_processed:
        st.session_state.clipboard_processed = component_value['timestamp']
        return component_value['text']

    return None



def copy_component(
    name: str,
    content: str,
    disabled: bool = False,
    styles: dict = None
) -> None:
    """Create a new instance of 'copy_component' for copying content to clipboard."""
    component_value = _copy_component_func(
        name=name,
        content=content,
        disabled=disabled,
        styles=styles or {}
    )
    return component_value