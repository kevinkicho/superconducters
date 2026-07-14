#!/usr/bin/env python3
"""Streamlit dashboard for the supported candidate-screening services."""

from __future__ import annotations

from superconductors.config import Settings
from superconductors.dashboard import build_snapshot, estimate_formula
from superconductors.repository import CandidateRepository


def main() -> None:
    try:
        import pandas as pd
        import plotly.express as px
        import streamlit as st
    except ImportError as exc:
        raise SystemExit('Install dashboard dependencies with: pip install -e ".[ui]"') from exc

    st.set_page_config(
        page_title="Superconductor Candidate Toolkit",
        page_icon="⚛️",
        layout="wide",
    )
    st.title("Superconductor Candidate Toolkit")
    st.caption(
        "Measured database values and transparent screening heuristics. "
        "Predictions are not experimental confirmation."
    )

    settings = Settings.from_env()
    repository = CandidateRepository(settings.database_path)
    page = st.sidebar.radio("View", ["Overview", "Candidates", "Tc estimate", "About"])

    if page == "Overview":
        _overview(st, pd, px, repository)
    elif page == "Candidates":
        _candidates(st, pd, repository)
    elif page == "Tc estimate":
        _prediction(st)
    else:
        _about(st)


def _overview(st, pd, px, repository: CandidateRepository) -> None:
    try:
        snapshot = build_snapshot(repository, limit=20)
    except (OSError, ValueError) as exc:
        st.error(f"Candidate database is unavailable: {exc}")
        return

    first, second, third = st.columns(3)
    first.metric("Database candidates", snapshot.result.candidates_loaded)
    second.metric("Top candidates shown", snapshot.result.candidates_selected)
    third.metric("Near-ambient in top set", len(snapshot.near_ambient))

    if not snapshot.measured:
        st.info("No candidates with measured Tc values are available.")
        return

    frame = pd.DataFrame([candidate.to_dict() for candidate in snapshot.measured])
    st.plotly_chart(
        px.scatter(
            frame,
            x="pressure",
            y="tc",
            hover_name="formula",
            color="source",
            labels={"pressure": "Pressure (GPa)", "tc": "Tc (K)"},
            title="Critical temperature versus pressure",
        ),
        use_container_width=True,
    )


def _candidates(st, pd, repository: CandidateRepository) -> None:
    left, middle, right = st.columns(3)
    min_tc = left.number_input("Minimum Tc (K)", min_value=0.0, value=0.0)
    use_pressure_limit = middle.checkbox("Limit pressure", value=False)
    max_pressure = right.number_input(
        "Maximum pressure (GPa)", min_value=0.0, value=200.0, disabled=not use_pressure_limit
    )
    limit = st.slider("Maximum rows", min_value=5, max_value=100, value=25, step=5)

    try:
        snapshot = build_snapshot(
            repository,
            min_tc=min_tc,
            max_pressure=max_pressure if use_pressure_limit else None,
            limit=limit,
        )
    except (OSError, ValueError) as exc:
        st.error(f"Candidate database is unavailable: {exc}")
        return
    if not snapshot.result.candidates:
        st.warning("No candidates match the selected criteria.")
        return
    frame = pd.DataFrame(snapshot.rows)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button(
        "Export filtered CSV",
        data=frame.to_csv(index=False),
        file_name="superconductor_candidates.csv",
        mime="text/csv",
    )


def _prediction(st) -> None:
    st.subheader("Transparent Tc screening estimate")
    formula = st.text_input("Chemical formula", value="H3S")
    if not st.button("Estimate"):
        return
    try:
        result = estimate_formula(formula)
    except ValueError as exc:
        st.error(str(exc))
        return
    first, second = st.columns(2)
    first.metric("Estimated Tc", f"{result.tc:.2f} K")
    second.metric("Heuristic uncertainty", f"± {result.uncertainty:.2f} K")
    st.info(
        f"Method: {result.method}. This formula-based estimate does not include crystal structure, "
        "pressure-dependent phases, or first-principles validation."
    )


def _about(st) -> None:
    st.subheader("Data and provenance")
    st.markdown(
        """
        - Candidate records are loaded from `data/superconductor_database.json`.
        - Database Tc and pressure fields are displayed as supplied by their records.
        - Formula estimates use a simplified Allen–Dynes-style heuristic.
        - Simulated or predicted results should never be presented as measured discoveries.
        """
    )


if __name__ == "__main__":
    main()
