"""Minimal read-only Streamlit demo for InsureIQ."""

from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="InsureIQ", layout="wide")
st.title("InsureIQ — Demo analítica")
st.caption("Datos sintéticos o públicos aprobados; no es un sistema de rechazo automático.")

source = st.selectbox("Fuente del dashboard", ["Sintética InsureIQ", "Accidentes públicos de Iowa"])
if source == "Accidentes públicos de Iowa":
    summary_path = Path("data/processed/public_iowa_crashes_summary.csv")
    metadata_path = Path("data/processed/public_iowa_crashes_metadata.json")
    if not summary_path.exists():
        st.warning("Ejecute `make public-data` para descargar la fuente pública aprobada.")
    else:
        summary = pd.read_csv(summary_path)
        st.subheader("Accidentes públicos de Iowa")
        st.caption("Fuente gubernamental CC BY 4.0; accidentes viales, no claims de seguros.")
        total = int(summary.loc[summary["dimension"] == "severity", "crashes"].sum())
        counties = int((summary["dimension"] == "county").sum())
        first, second = st.columns(2)
        first.metric("Accidentes descargados", f"{total:,}")
        second.metric("Condados con registros", f"{counties:,}")
        st.bar_chart(summary[summary["dimension"] == "severity"].set_index("category")["crashes"])
        st.dataframe(summary, use_container_width=True)

forecast_path = Path("reports/forecast_metrics.json")
if forecast_path.exists():
    st.success("Pronóstico disponible")
    st.json(forecast_path.read_text(encoding="utf-8"))
else:
    st.info("Ejecuta `make forecast` para generar el reporte de pronóstico.")

st.header("Resultados ML de fraude")
fraud_metrics_path = Path("dashboards/exports/ml_fraud_metrics.csv")
if fraud_metrics_path.exists():
    ml_metrics = pd.read_csv(fraud_metrics_path)
    st.success("Modelo ML disponible: benchmark público Zenodo 13381118")
    st.dataframe(ml_metrics, use_container_width=True)
    queue_path = Path("dashboards/exports/fraud_review_queue.csv")
    if queue_path.exists():
        queue = pd.read_csv(queue_path)
        st.metric("Casos priorizados para revisión manual", len(queue))
        st.dataframe(queue, use_container_width=True)
    st.caption(
        "Las métricas son del benchmark publicado; no son validación "
        "ecuatoriana ni producción."
    )
else:
    st.warning("Ejecute `make fraud-train` y `make bi-data` para exportar las métricas ML.")
st.text_input("ID de siniestro", placeholder="DEMO-001")
st.button("Consultar modelo", disabled=True)
