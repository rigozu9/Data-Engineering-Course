import os
from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

HOST_PROJECT_DIR = os.environ["HOST_PROJECT_DIR"]
HOST_HOME = os.environ["HOST_HOME"]

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

def run_elt_script():
    script_path = "/opt/airflow/elt/elt_script.py"
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Script failed with error: {result.stderr}")
    else:
        print(result.stdout)

dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='An ELT workflow with dbt',
    start_date=datetime(2026, 1, 7),
    catchup=False,
)

t1 = PythonOperator(
    task_id="run_elt_script",
    python_callable=run_elt_script,
    dag=dag,
)

t2 = DockerOperator(
    task_id="dbt_run",
    image="ghcr.io/dbt-labs/dbt-postgres:1.4.7",
    command=[
        "run",
        "--profiles-dir", "/root/.dbt",
        "--project-dir", "/opt/dbt",
        "--profile", "custom_postgres",
        "--target", "dev",
    ],
    auto_remove="success",
    docker_url="unix://var/run/docker.sock",

    # IMPORTANT: use the same network your compose created (see note below)
    network_mode="elt_elt_network",

    mounts=[
        Mount(source=f"{HOST_PROJECT_DIR}/custom_postgres", target="/opt/dbt", type="bind"),
        Mount(source=f"{HOST_HOME}/.dbt", target="/root/.dbt", type="bind"),
    ],
    dag=dag,
)

t1 >> t2