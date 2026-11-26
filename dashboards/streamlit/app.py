"""Minimal read-only Streamlit demo for InsureIQ."""

from pathlib import Path

import streamlit as st

st.set_page_config(page_title="InsureIQ", layout="wide")
st.title("InsureIQ — Demo analítica")
st.caption("Datos sintéticos o públicos aprobados; no es un sistema de rechazo automático.")

forecast_path = Path("reports/forecast_metrics.json")
if forecast_path.exists():
    st.success("Pronóstico disponible")
    st.json(forecast_path.read_text(encoding="utf-8"))
else:
    st.info("Ejecuta `make forecast` para generar el reporte de pronóstico.")

st.header("Predicción de fraude")
st.warning("El modelo no está disponible hasta verificar y registrar un benchmark público.")
st.text_input("ID de siniestro", placeholder="DEMO-001")
st.button("Consultar modelo", disabled=True)
