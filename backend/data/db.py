import glob 
import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
)
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Must set DATABASE_URL environment variable")
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(engine)

table="activations"
MODEL="gemma-2-9b-it"
LAYER="20-gemmascope-res-131k"
save_dir  = f"{LAYER}/{MODEL}/activations"

dfs = []
for path in sorted(glob.glob(f"{save_dir}/*.jsonl")):
    dfs.append(pd.read_json(path, lines=True))

df = pd.concat(dfs,ignore_index=True)

with engine.begin() as conn:
    df.to_sql("activations", con=conn)