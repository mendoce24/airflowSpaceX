from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.email import EmailOperator
from datetime import datetime
import pandas as pd

def myfunction():
    raise Exception

def _generate_platzi_data(**kwargs):
    
    data = pd.DataFrame({"student": ["Maria Cruz", "Daniel Crema",
        "Elon Musk", "Karol Castrejon", "Freddy Vega"],
        "timestamp": [kwargs['logical_date'],
        kwargs['logical_date'], kwargs['logical_date'], kwargs['logical_date'],
        kwargs['logical_date']]})
    data.to_csv(f"/tmp/platzi_data_{kwargs['ds_nodash']}.csv",
    header=True)


default_args = {}

with DAG(dag_id='01-SpaceX',
        description='Space X API',
        schedule_interval= "@daily",
        start_date= datetime(2023, 9, 1), 
        end_date= datetime(2023, 9, 3), 
        default_args= default_args,
        max_active_runs=1) as dag:

    NASAConfirmation = BashOperator(task_id='NASAConfirmation',
                  bash_command= 'sleep 20 && echo "OK" >/tmp/response_{{ds_nodash}}.txt',
                  trigger_rule= TriggerRule.ALL_SUCCESS,
                  retries= 2,
                  retry_delay= 5,
                  depends_on_past= False)
    
    ReadingNASAData = BashOperator(task_id = "ReadingNASAData",
                  bash_command='ls /tmp && head /tmp/response_{{ds_nodash}}.txt',
                  trigger_rule= TriggerRule.ALL_SUCCESS,
                  retries= 2,
                  retry_delay= 5,
                  depends_on_past= False)
    
    GetSpaceXData = BashOperator(task_id='GetSpaceXData',
                  bash_command= "curl -o /tmp/history.json -L 'https://api.spacexdata.com/v4/history'", 
                  retries= 2,
                  retry_delay= 5,
                  trigger_rule= TriggerRule.ALL_SUCCESS, 
                  depends_on_past= True)
    
    ReadingSpaceXData = BashOperator(task_id = "ReadingSpaceXData",
                  bash_command='ls /tmp && head /tmp/history.json',
                  trigger_rule= TriggerRule.ALL_SUCCESS,
                  retries= 2,
                  retry_delay= 5,
                  depends_on_past= False)
    
    SatelliteResponse = PythonOperator(task_id="SatelliteResponse",
                    python_callable=_generate_platzi_data)
    
    ReadSatelliteResponse = BashOperator(task_id = "ReadSatelliteResponse",
                  bash_command='ls /tmp && head /tmp/platzi_data_{{ds_nodash}}.csv',
                  trigger_rule= TriggerRule.ALL_SUCCESS,
                  retries= 2,
                  retry_delay= 5,
                  depends_on_past= False)
    
    ReportAnalysis = EmailOperator(task_id='ReportAnalysis',
                    to = "mendoce@gmail.com",
                    subject = "Notification Final data available",
                    html_content = "Notification to analysts. Final data is available",
                    dag = dag)  

    NASAConfirmation >> ReadingNASAData >> GetSpaceXData >> ReadingSpaceXData >> SatelliteResponse >> ReadSatelliteResponse >>ReportAnalysis

