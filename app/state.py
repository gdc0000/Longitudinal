import streamlit as st

_REQUIRED_KEYS: dict[str, object] = {
    "data_frames": [],
    "file_names": [],
    "wave_assignments": {},
    "merged_df": None,
    "merge_type": None,
}


def init_session_state() -> None:
    for key, default in _REQUIRED_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default
