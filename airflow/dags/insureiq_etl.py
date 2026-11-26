"""Airflow orchestration definition for the InsureIQ ETL flow."""

from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except ImportError:  # Allows static checks without installing Airflow.
    DAG = None
    BashOperator = None


if DAG is not None:
    with DAG(
        dag_id="insureiq_etl",
        start_date=datetime(2025, 1, 1),
        schedule=None,
        catchup=False,
        tags=["insureiq", "etl"],
    ) as dag:
        generate = BashOperator(
            task_id="generate_synthetic",
            bash_command="make data-generate PROFILE=smoke",
        )
        transform = BashOperator(
            task_id="validate_transform",
            bash_command="make etl",
        )
        generate >> transform
