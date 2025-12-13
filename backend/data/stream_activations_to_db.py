import requests
import gzip
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table,  MetaData, insert
from pathlib import Path
load_dotenv()

MODEL = "gemma-2-9b-it"
LAYER = "20-gemmascope-res-131k"
LINK = "https://neuronpedia-datasets.s3.amazonaws.com/v1/{model}/{layer}/activations/batch-{i}.jsonl.gz"
BATCH_SIZE = 5000
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_DIR = f"{LAYER}/{MODEL}/activations"
STREAM_FROM_DISK = True  # must download to BASE_DIR first

activations_field_map = {
    "model_id":      {"source": "modelId"},
    "layer":         {"source": "layer"},
    "index":         {"source": "index"},
    "sample_id":       {"source": "id"},
    "values":    {"source": "values"},
    "tokens":       {"source": "tokens"},
    "max_value":    {"source": "maxValue"},
    "max_value_token_index": {"source": "maxValueTokenIndex"},
    "min_value":  {"source": "minValue"},
    "dataset_id": {"source": "NONE", "default": "neuronpedia"}
}

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

activations = Table(
    "activations",
    metadata,
    autoload_with=engine
)

insertable_cols = {
    c.name
    for c in activations.columns
    if not c.primary_key and c.server_default is None
}


def stream_to_postgres():
    rows = []
    if STREAM_FROM_DISK:
        stream = stream_from_disk(BASE_DIR)
    else:
        stream = stream_from_s3()

    for item in stream:
        rows.append(transform_row(item))

        if len(rows) >= BATCH_SIZE:
            with engine.begin() as conn:
                conn.execute(insert(activations), rows)
                rows = []
    if rows:
        with engine.begin() as conn:
            conn.execute(insert(activations), rows)


def stream_from_disk(base_dir):
    for path in sorted(Path(base_dir).glob("batch-*.jsonl")):
        print("Reading:", path)
        with open(path, "r") as f:
            for line in f:
                yield json.loads(line)


def stream_from_s3():
    for i in range(127):
        url = LINK.format(model=MODEL, layer=LAYER, i=i)
        print("Downloading:", url)

        r = requests.get(url, stream=True)
        r.raise_for_status()

        with gzip.GzipFile(fileobj=r.raw, mode="rb") as gz:
            for line in gz:
                yield json.loads(line)


def transform_row(obj):
    out = {}
    for col, rules in activations_field_map.items():
        if col not in insertable_cols:
            continue
        src = rules["source"]
        default = rules.get("default")
        out[col] = obj.get(src, default)
    return out


if __name__ == "__main__":
    stream_to_postgres()
