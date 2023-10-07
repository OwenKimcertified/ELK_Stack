from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import datetime
from elasticsearch import Elasticsearch
from google.cloud import bigquery


default_args = {
    'start_date': datetime.datetime(2023, 10, 10, 6, 0, 0),
    'retries': 1,
    'retry_delay': timedelta(minutes = 5),
}

dag = DAG(
    'elasticsearch_to_bigquery',
    default_args = default_args,
    description = 'Elasticsearch to BigQuery daily data transfer',
    schedule_interval = timedelta(days = 1),  
    catchup = False,
)


def ES_to_BQ():
    client = bigquery.Client(project='decoded-oxide-401216')
    dset = 'django_account_logs'
    table_id = 'ES_logs'
    table_ref = client.dataset(dset).table(table_id)

    schema = [
        bigquery.SchemaField('log_level', 'STRING'),
        bigquery.SchemaField('category', 'STRING'),
        bigquery.SchemaField('time', 'TIMESTAMP'),
        bigquery.SchemaField('method', 'STRING'),
        bigquery.SchemaField('username', 'STRING'),
        bigquery.SchemaField('email', 'STRING'),
        bigquery.SchemaField('status', 'STRING')
    ]

    table = bigquery.Table(table_ref, schema = schema)

    es = Elasticsearch(['http://localhost:9200'], basic_auth = ('elastic', 'elastic'))
    elasticsearch_index = 'django-server-account'

    es_data = es.search(index = elasticsearch_index)

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    rows_to_insert = []

    for hit in es_data['hits']['hits']:
        source = hit['_source']['parsed_message']
        message_date = source.get('time', None).split(' ')[0]

        if today == message_date:
            row = (
                source.get('log_level', None),
                source.get('category', None),
                source.get('time', None),
                source.get('method', None),
                source.get('username', None),
                source.get('email', None),
                source.get('status', None)
            )
            rows_to_insert.append(row)

    if rows_to_insert:
        errors = client.insert_rows(table, rows_to_insert)
        if not errors:
            print('ES -> bigquery.django_account_logs.ES_logs Success.')
        else:
            print(f'ERROR: {errors}')
    else:
        print('there`s no data to stack.')


Es_data_to_BQ = PythonOperator(
    task_id = 'ES_to_BQ',
    python_callable = ES_to_BQ,
    dag = dag,
)

Es_data_to_BQ
