import requests
import gzip
import json
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
load_dotenv()

MODEL = "gemma-2-9b-it"
LAYER = "20-gemmascope-res-131k"
LINK = "https://neuronpedia-datasets.s3.amazonaws.com/v1/{model}/{layer}/features/batch-{i}.jsonl.gz"

DATABASE_URL = os.getenv("DATABASE_URL")

FIELD_MAP = {
    "model_id":      {"source": "modelId"},
    "layer":         {"source": "layer"},
    "index":         {"source": "index"},
    "source_set_name": {"source": "sourceSetName", "default": ""},
    "neg_str":       {"source": "neg_str"},
    "neg_values":    {"source": "neg_values"},
    "pos_str":       {"source": "pos_str"},
    "pos_values":    {"source": "pos_values"},
    "frac_nonzero":  {"source": "frac_nonzero", "default": 0.0},
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
    out = []
    for col, rules in FIELD_MAP.items():
        src = rules["source"]
        default = rules.get("default")
        value = obj.get(src, default)
        out.append(value)
    return tuple(out)

def stream_to_postgres():
    rows = []
    BATCH = 5000

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for item in stream_from_s3():
                rows.append(transform_row(item))

                if len(rows) >= BATCH:
                    execute_values(
                        cur,
                        """
                        INSERT INTO features (
                            model_id, layer, index, source_set_name,
                            neg_str, neg_values, pos_str, pos_values,
                            frac_nonzero
                        ) VALUES %s
                        """,
                        rows
                    )
                    rows = []

            # final remainder
            if rows:
                execute_values(
                    cur,
                    """
                    INSERT INTO features (
                        model_id, layer, index, source_set_name,
                        neg_str, neg_values, pos_str, pos_values,
                        frac_nonzero
                    ) VALUES %s
                    """,
                    rows
                )

        conn.commit()

if __name__ == "__main__":
    stream_to_postgres()
