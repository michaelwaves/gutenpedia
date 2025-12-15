#!/usr/bin/env python3
"""
Extract SAE features from masterclass samples
"""

import argparse
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from sqlalchemy import create_engine, MetaData, Table, insert
from dotenv import load_dotenv
import os
load_dotenv()
DEFAULT_MODEL = "gemma-2-9b-it"
DEFAULT_SOURCE = "20-gemmascope-res-131k"

dataset = "hf-dataset"

DATABASE_URL = os.getenv("DATABASE_URL")
# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

datasets = Table(
    "datasets",
    metadata,
    autoload_with=engine
)
samples = Table(
    "samples",
    metadata,
    autoload_with=engine
)

activations = Table(
    "activations",
    metadata,
    autoload_with=engine
)


def create_dataset(dataset_name: str) -> None:
    with engine.begin() as conn:
        dataset_id = conn.execute(
            insert(datasets).returning(datasets.c.id),
            [
                {
                    "name": dataset_name,
                    "type": "huggingface"
                }
            ]
        )
    return dataset_id.scalar_one()


def create_samples(sample_data):
    with engine.begin() as conn:
        samples = conn.execute(
            insert(samples).returning(samples),
            sample_data
        )
    return dataset_id.scalar_one()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--samples", default="../data/datasets/masterclass/cv_80/samples.parquet")
    parser.add_argument(
        "--output", default="../data/runs/masterclass/cv_80/features/activations.parquet")
    parser.add_argument("--server-url", default="http://127.0.0.1:5002/")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--limit", type=int, help="Limit samples for testing")
    args = parser.parse_args()

    # Load samples
    samples_path = Path(args.samples)
    if not samples_path.is_absolute():
        samples_path = Path(__file__).parent / samples_path

    print(f"Loading samples from {samples_path}")
    if (samples_path.suffix == ".csv"):
        df = pd.read_csv(samples_path)
    else:
        df = pd.read_parquet(samples_path)

    if args.limit:
        df = df.head(args.limit)

    print(f"Processing {len(df)} samples")

    dataset_id = create_dataset(dataset)

    # Extract features
    all_activations = []
    all_features = set()

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Extracting"):
        sample_idx = row['sample_idx']
        text = row['text']

        # Send raw conversation text (no Gemma template conversion)
        result = extract_features(text, args.server_url, top_k=args.top_k)
        print(result)

        if result and 'results' in result:
            samples = []

            for token_data in result['results']:
                samples.append({
                    "tokens": token_data.get('tokens'),
                    "dataest_id": dataset_id
                })

            for token_data in result['results']:
                for feat in token_data.get('top_features'):
                    all_features.add(feat.get('feature_index'))

                token_pos = token_data.get('token_position', 0)
                token = token_data.get('token', '')
                for feat in token_data.get('top_features', []):
                    all_activations.append({
                        'sample_idx': int(sample_idx),
                        'pos': int(token_pos),
                        'feature_idx': int(feat['feature_index']),
                        'act_val': float(feat['activation_value']),
                        'token': token,
                        'model': DEFAULT_MODEL,
                        'source': DEFAULT_SOURCE
                    })

    # Save activations
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).parent / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    activations_df = pd.DataFrame(all_activations)
    if samples_path.suffix == ".csv":
        activations_df.to_csv(output_path, index=False)
    else:
        activations_df.to_parquet(output_path, index=False)

    print(f"\nSaved {len(activations_df)} activations to {output_path}")
    print(f"Unique features: {activations_df['feature_idx'].nunique()}")


def extract_features(text: str, server_url: str = "http://127.0.0.1:5002",
                     model: str = DEFAULT_MODEL, source: str = DEFAULT_SOURCE,
                     top_k: int = 100) -> dict:
    """Extract SAE features from text using inference server"""
    url = f"{server_url}/v1/activation/topk-by-token"

    response = requests.post(
        url,
        json={
            "prompt": text,
            "model": model,
            "source": source,
            "top_k": top_k,
            "ignore_bos": True,
            "clear_cache": True
        },
        timeout=120
    )

    if response.status_code != 200:
        message = f"Error: {response.status_code} - {response.text[:200]}"
        print(message)
        return {"error": message}

    return response.json()


if __name__ == "__main__":
    # main()
    res = create_dataset(dataset)
    print(res)
