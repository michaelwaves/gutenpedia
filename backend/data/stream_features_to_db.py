import requests
import gzip
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table,  MetaData

load_dotenv()

MODEL = "gemma-2-9b-it"
LAYER = "20-gemmascope-res-131k"
LINK = "https://neuronpedia-datasets.s3.amazonaws.com/v1/{model}/{layer}/features/batch-{i}.jsonl.gz"
BATCH_SIZE = 5000
DATABASE_URL = os.getenv("DATABASE_URL")

features_field_map = {
    "model_id":      {"source": "modelId"},
    "layer":         {"source": "layer"},
    "feature_index":  {"source": "index"},
    "source_set_name": {"source": "sourceSetName", "default": ""},
    "neg_str":       {"source": "neg_str"},
    "neg_values":    {"source": "neg_values"},
    "pos_str":       {"source": "pos_str"},
    "pos_values":    {"source": "pos_values"},
    "frac_nonzero":  {"source": "frac_nonzero", "default": 0.0},
}

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

features = Table(
    "features",
    metadata,
    autoload_with=engine
)

insertable_cols = {
    c.name
    for c in features.columns
    if not c.primary_key and c.server_default is None
}


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
    for col, rules in features_field_map.items():
        if col not in insertable_cols:
            continue
        src = rules["source"]
        default = rules.get("default")
        out[col] = obj.get(src, default)
    return out


def stream_to_postgres():
    rows = []

    with engine.begin() as conn:
        for item in stream_from_s3():
            rows.append(transform_row(item))

            if len(rows) >= BATCH_SIZE:
                conn.execute(features.insert(), rows)
                rows = []
        if rows:
            conn.execute(features.insert(), rows)


if __name__ == "__main__":
    stream_to_postgres()
