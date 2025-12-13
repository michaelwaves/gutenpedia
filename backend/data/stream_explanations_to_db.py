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
LINK = "https://neuronpedia-datasets.s3.amazonaws.com/v1/{model}/{layer}/explanations/batch-{i}.jsonl.gz"
BATCH_SIZE = 5000
DATABASE_URL = os.getenv("DATABASE_URL")
BASE_DIR = f"{LAYER}/{MODEL}/explanations"
STREAM_FROM_DISK = False  # must download to BASE_DIR first

explanations_field_map = {
    "model_id":      {"source": "modelId"},
    "layer":         {"source": "layer"},
    "index":         {"source": "index"},
    "embedding":       {"source": "embedding"},
    "description":    {"source": "description"},
    "notes":       {"source": "notes"},
    "type_name":    {"source": "typeName"},
    "explanation_model": {"source": "explanationModel"}
}

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

explanations = Table(
    "explanations",
    metadata,
    autoload_with=engine
)

insertable_cols = {
    c.name
    for c in explanations.columns
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
                conn.execute(insert(explanations), rows)
                rows = []
    if rows:
        with engine.begin() as conn:
            conn.execute(insert(explanations), rows)


def stream_from_disk(base_dir):
    for path in sorted(Path(base_dir).glob("batch-*.jsonl")):
        print("Reading:", path)
        with open(path, "r") as f:
            for line in f:
                yield json.loads(line)


def stream_from_s3():
    for i in range(306, 616):
        url = LINK.format(model=MODEL, layer=LAYER, i=i)
        print("Downloading:", url)

        r = requests.get(url, stream=True)
        r.raise_for_status()

        with gzip.GzipFile(fileobj=r.raw, mode="rb") as gz:
            for line in gz:
                yield json.loads(line)


def transform_row(obj):
    out = {}
    for col, rules in explanations_field_map.items():
        if col not in insertable_cols:
            continue
        src = rules["source"]
        default = rules.get("default")
        out[col] = obj.get(src, default)
    return out


if __name__ == "__main__":
    stream_to_postgres()
