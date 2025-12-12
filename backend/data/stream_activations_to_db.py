import requests
import gzip
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import execute_values
load_dotenv()


MODEL = "gemma-2-9b-it"
LAYER = "20-gemmascope-res-131k"
LINK = "https://neuronpedia-datasets.s3.amazonaws.com/v1/{model}/{layer}/features/batch-{i}.jsonl.gz"

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("Must set DATABASE_URL environment variable")
ACTIVATION_MAP = {
    "modelId": "model_id",
    "layer": "layer",
    "index": "index",
    "id": "sample_id",
    "tokens": "tokens",
    "values": "values",
    "maxValue": "max_value",
    "maxValueTokenIndex": "max_value_token_index",
    "minValue": "min_value"
}


def stream_from_s3():
    for i in range(127, 617):
        url = LINK


def stream_to_postgres():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for item in stream_from_s3():
