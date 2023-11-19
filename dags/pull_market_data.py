"""
pull_market_data
DAG auto-generated by Astro Cloud IDE.
"""

from airflow.decorators import dag
from airflow.models import Variable
from airflow.providers.postgres.operators.postgres import PostgresOperator
from astro import sql as aql
from astro.table import Table, Metadata
import pandas as pd
import pendulum
import textwrap

from typing import List, Dict, Any
import requests
from airflow.hooks.base import BaseHook
from airflow.models import Connection

"""
First time using the Astro Cloud IDE! Looking forward to building data pipelines in a new and different way!

I'm going to be using the Astro Cloud IDE and the Polygon API to daily stock aggregates, before loading them into a Postgres database.
Then, these values will be transformed, and stored in the Postgres table, read to be used for downstream visualization or analytics.
"""

@aql.dataframe(task_id="extract_stock_data")
def extract_stock_data_func():
    # Create a list of stock tickers to loop through
    stock_tickers: List[str] = [
        "AAPL",
        "AMZN",
        "CHPT"
    ]
    
    # Set variables
    POLYGON_API_KEY: str = Variable.get("POLYGON_API_KEY")
    DS: str = Variable.get("DS")  # TODO: Fix this
    
    # Create a list to append the response data to
    raw_open_close: List[Dict[str, Any]] = []
    
    # Loop through each ticker
    for stock_ticker in stock_tickers:
        # Build the URL, and make a request to the API
        url: str = f"https://api.polygon.io/v1/open-close/{stock_ticker}/{DS}?adjusted=true&apiKey={POLYGON_API_KEY}"
        response: requests.Response = requests.get(url)
        raw_open_close.append(response.json())
    
    return pd.DataFrame.from_dict(raw_open_close, orient="columns")
        

@aql.transform(conn_id="jroachgolf84-sandbox-postgres", task_id="load_stock_data")
def load_stock_data_func(extract_stock_data: Table):
    return """
    -- Insert all data with a basic select statement
    SELECT * FROM {{extract_stock_data}}
    WHERE status = 'OK'
    ;
    """

default_args={
    "retries": 3,
    "retry_delay": pendulum.duration(seconds=60).as_timedelta(),
    "execution_timeout": pendulum.duration(seconds=120).as_timedelta(),
    "owner": "jroachgolf84@outlook.com,Open in Cloud IDE",
}

@dag(
    default_args=default_args,
    schedule="0 19 * * *",
    start_date=pendulum.from_format("2023-11-01", "YYYY-MM-DD").in_tz("UTC"),
    catchup=True,
    concurrency=1,
    max_active_tasks=1,
    max_active_runs=1,
    dagrun_timeout=pendulum.duration(seconds=60).as_timedelta(),
    owner_links={
        "jroachgolf84@outlook.com": "mailto:jroachgolf84@outlook.com",
        "Open in Cloud IDE": "https://cloud.astronomer.io/clp4adpm600ai01nseg4x93h5/cloud-ide/clp4b3v0h00ak01nsepkkan70/clp4b88p7009301oyz8mony5d",
    },
)
def pull_market_data():
    extract_stock_data = extract_stock_data_func()

    load_stock_data = load_stock_data_func(
        extract_stock_data,
        output_table=Table(
            name="raw_open_close",
            metadata=Metadata(
                schema="public",
                database="postgres",
            ),
        ),
    )

    curate_stock_data = PostgresOperator(
        database="postgres",
        sql=textwrap.dedent("""\
            -- Curate the results from the raw table
            DELETE FROM curated_stock_data
            WHERE (stock_ticker, market_date) IN (
                SELECT symbol, '{{var.value.DS}}' FROM raw_open_close
            );
            
            INSERT INTO curated_stock_data
                SELECT
                    symbol,
                    "from",
                    "open",
                    "close",
                    low,
                    high
                FROM raw_open_close
                WHERE "from" = '{{var.value.DS}}'
            ;"""),
        postgres_conn_id="jroachgolf84-sandbox-postgres",
        task_id="curate_stock_data",
    )

    curate_stock_data << load_stock_data

dag_obj = pull_market_data()
