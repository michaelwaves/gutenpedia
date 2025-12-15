#!/usr/bin/env python3
"""
Extract SAE features from samples and store in database
"""

import argparse
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from sqlalchemy import create_engine, MetaData, Table, insert, select
from dotenv import load_dotenv
import os
from typing import List, Dict, Tuple

load_dotenv()

DEFAULT_MODEL = "gemma-2-9b-it"
DEFAULT_SOURCE = "20-gemmascope-res-131k"
DEFAULT_LAYER = "20-gemmascope-res-131k"

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Load table schemas
datasets_table = Table("datasets", metadata, autoload_with=engine)
samples_table = Table("samples", metadata, autoload_with=engine)
activations_table = Table("activations", metadata, autoload_with=engine)
features_table = Table("features", metadata, autoload_with=engine)


def create_dataset(dataset_name: str, dataset_type: str = "huggingface") -> str:
    """Create a dataset record and return its UUID"""
    with engine.begin() as conn:
        result = conn.execute(
            insert(datasets_table).returning(datasets_table.c.id),
            [{"name": dataset_name, "type": dataset_type}]
        )
        return result.scalar_one()


def create_samples_batch(samples_data: list) -> list:
    """
    Create multiple sample records in one query.
    Returns list of (sample_uuid, tokens) tuples in same order as input.
    """
    with engine.begin() as conn:
        result = conn.execute(
            insert(samples_table).returning(
                samples_table.c.id,
                samples_table.c.tokens
            ),
            samples_data
        )
        return [(row.id, row.tokens) for row in result]


def get_feature_uuid_mapping(feature_indexes: set, model_id: str, layer: str) -> dict:
    """
    Query database to map feature_index -> feature_uuid.
    Returns dict: {feature_index: feature_uuid}
    """
    with engine.connect() as conn:
        stmt = select(
            features_table.c.feature_index,
            features_table.c.id
        ).where(
            features_table.c.feature_index.in_(feature_indexes),
            features_table.c.model_id == model_id,
            features_table.c.layer == layer
        )
        result = conn.execute(stmt)
        return {row.feature_index: row.id for row in result}


def create_activations_batch(activations_data: list) -> None:
    """Insert multiple activation records in one query"""
    if not activations_data:
        return

    with engine.begin() as conn:
        conn.execute(insert(activations_table), activations_data)


def build_activation_records(
    sample_uuid: str,
    tokens: list,
    api_results: list,
    feature_uuid_map: dict
) -> list:
    """
    Build activation records for a single sample.

    For each unique feature that appears in the sample:
    - Create a values array with length = number of tokens
    - Set activation values at positions where feature appears
    - Set 0.0 at positions where feature doesn't appear

    Returns list of dicts ready for database insertion.
    """
    num_tokens = len(tokens)

    # Group activations by feature_index
    feature_activations = {}  # {feature_index: {token_pos: activation_value}}

    for token_data in api_results:
        token_pos = token_data['token_position']
        for feat in token_data.get('top_features', []):
            feature_idx = feat['feature_index']
            act_val = feat['activation_value']

            if feature_idx not in feature_activations:
                feature_activations[feature_idx] = {}
            feature_activations[feature_idx][token_pos] = act_val

    # Build database records
    activation_records = []

    for feature_idx, position_values in feature_activations.items():
        # Skip if feature not found in database
        if feature_idx not in feature_uuid_map:
            continue

        feature_uuid = feature_uuid_map[feature_idx]

        # Build values array: 0.0 for positions without activation
        values = [position_values.get(i, 0.0) for i in range(num_tokens)]

        # Calculate max/min for this feature across all positions
        non_zero_values = [v for v in values if v != 0.0]
        max_value = max(non_zero_values) if non_zero_values else 0.0
        max_token_idx = values.index(max_value) if max_value > 0 else None
        min_value = min(non_zero_values) if non_zero_values else 0.0

        activation_records.append({
            'sample_id': sample_uuid,
            'feature_id': feature_uuid,
            'values': values,
            'max_value': max_value,
            'max_value_token_index': max_token_idx,
            'min_value': min_value
        })

    return activation_records


def extract_features(
    text: str,
    server_url: str = "http://127.0.0.1:5002",
    model: str = DEFAULT_MODEL,
    source: str = DEFAULT_SOURCE,
    top_k: int = 100
) -> dict:
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


def process_text(
    text: str,
    dataset_id: str,
    server_url: str,
    model_id: str,
    layer: str,
    top_k: int = 10
) -> dict:
    """
    Process a single text sample:
    1. Extract features via API
    2. Create sample record
    3. Map feature_indexes to UUIDs
    4. Create activation records

    Returns dict with stats.
    """
    # Step 1: Call API
    api_result = extract_features(text, server_url, top_k=top_k)

    if not api_result or 'results' not in api_result:
        return {'error': 'No results from API'}

    tokens = api_result.get('tokens', [])
    results = api_result['results']

    # Step 2: Create sample record
    sample_data = [{
        'dataset_id': dataset_id,
        'tokens': tokens,
        'sample_text': text
    }]

    samples = create_samples_batch(sample_data)
    sample_uuid, sample_tokens = samples[0]

    # Step 3: Get all unique feature_indexes from API results
    unique_feature_indexes = set()
    for token_data in results:
        for feat in token_data.get('top_features', []):
            unique_feature_indexes.add(feat['feature_index'])

    # Step 4: Map feature_index -> feature_uuid
    feature_uuid_map = get_feature_uuid_mapping(
        unique_feature_indexes,
        model_id,
        layer
    )

    # Step 5: Build and insert activation records
    activation_records = build_activation_records(
        sample_uuid,
        sample_tokens,
        results,
        feature_uuid_map
    )

    create_activations_batch(activation_records)

    return {
        'sample_uuid': sample_uuid,
        'num_tokens': len(tokens),
        'num_features': len(unique_feature_indexes),
        'num_features_found': len(feature_uuid_map),
        'num_features_missing': len(unique_feature_indexes) - len(feature_uuid_map),
        'num_activations': len(activation_records)
    }


def process_batch(
    texts: List[str],
    dataset_id: str,
    server_url: str,
    model_id: str,
    layer: str,
    top_k: int = 10,
    batch_size: int = 50
) -> Dict:
    """
    Process a batch of texts efficiently:
    1. Call API for each text
    2. Batch insert all samples
    3. Map all unique features once
    4. Batch insert all activations

    Returns aggregated stats.
    """
    all_api_results = []
    all_sample_data = []

    # Step 1: Call API for each text (with progress bar)
    for text in tqdm(texts, desc="Calling API", leave=False):
        api_result = extract_features(text, server_url, top_k=top_k)

        if api_result and 'results' in api_result:
            all_api_results.append({
                'text': text,
                'tokens': api_result.get('tokens', []),
                'results': api_result['results']
            })
            all_sample_data.append({
                'dataset_id': dataset_id,
                'tokens': api_result.get('tokens', []),
                'sample_text': text
            })

    if not all_sample_data:
        return {'error': 'No valid API results'}

    # Step 2: Batch insert all samples
    samples = create_samples_batch(all_sample_data)

    # Step 3: Collect ALL unique feature_indexes from all samples
    all_unique_features = set()
    for api_result in all_api_results:
        for token_data in api_result['results']:
            for feat in token_data.get('top_features', []):
                all_unique_features.add(feat['feature_index'])

    # Step 4: Map all features to UUIDs in ONE query
    feature_uuid_map = get_feature_uuid_mapping(
        all_unique_features,
        model_id,
        layer
    )

    # Step 5: Build all activation records for all samples
    all_activation_records = []
    for (sample_uuid, sample_tokens), api_result in zip(samples, all_api_results):
        activation_records = build_activation_records(
            sample_uuid,
            sample_tokens,
            api_result['results'],
            feature_uuid_map
        )
        all_activation_records.extend(activation_records)

    # Step 6: Batch insert all activations
    create_activations_batch(all_activation_records)

    return {
        'num_samples_processed': len(samples),
        'num_samples_failed': len(texts) - len(samples),
        'num_unique_features': len(all_unique_features),
        'num_features_found': len(feature_uuid_map),
        'num_features_missing': len(all_unique_features) - len(feature_uuid_map),
        'num_activations': len(all_activation_records)
    }


def load_texts_from_file(file_path: str, text_column: str = 'text', limit: int = None) -> pd.DataFrame:
    """Load texts from CSV or parquet file"""
    path = Path(file_path)

    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    print(f"Loading data from {path}")

    if path.suffix == '.csv':
        df = pd.read_csv(path)
    elif path.suffix in ['.parquet', '.pq']:
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv or .parquet")

    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found. Available columns: {list(df.columns)}")

    if limit:
        df = df.head(limit)

    print(f"Loaded {len(df)} samples")
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Extract SAE features and store in database"
    )
    parser.add_argument("--text", help="Single text to process")
    parser.add_argument("--file", help="CSV or parquet file to process")
    parser.add_argument("--text-column", default="text", help="Column name containing text (default: 'text')")
    parser.add_argument("--dataset-name", default="test-dataset", help="Dataset name")
    parser.add_argument("--server-url", default="http://127.0.0.1:5002/")
    parser.add_argument("--model-id", default=DEFAULT_MODEL)
    parser.add_argument("--layer", default=DEFAULT_LAYER)
    parser.add_argument("--top-k", type=int, default=10, help="Number of top features per token")
    parser.add_argument("--limit", type=int, help="Limit number of samples to process")
    parser.add_argument("--batch-size", type=int, default=50,
                       help="Number of samples to process in each batch (default: 50)")
    args = parser.parse_args()

    # Create dataset
    print(f"Creating dataset: {args.dataset_name}")
    dataset_id = create_dataset(args.dataset_name)
    print(f"Dataset ID: {dataset_id}\n")

    # Process single text
    if args.text:
        print(f"Processing single text: {args.text[:50]}...")
        stats = process_text(
            text=args.text,
            dataset_id=dataset_id,
            server_url=args.server_url,
            model_id=args.model_id,
            layer=args.layer,
            top_k=args.top_k
        )

        print(f"\nResults:")
        print(f"  Sample UUID: {stats['sample_uuid']}")
        print(f"  Tokens: {stats['num_tokens']}")
        print(f"  Features triggered: {stats['num_features']}")
        print(f"  Features found in DB: {stats['num_features_found']}")
        print(f"  Features missing from DB: {stats['num_features_missing']}")
        print(f"  Activation records created: {stats['num_activations']}")

    # Process file
    elif args.file:
        df = load_texts_from_file(args.file, args.text_column, args.limit)
        texts = df[args.text_column].tolist()

        print(f"Processing {len(texts)} samples in batches of {args.batch_size}...")

        # Process in batches with progress bar
        total_stats = {
            'num_samples_processed': 0,
            'num_samples_failed': 0,
            'num_unique_features': set(),
            'num_features_found': 0,
            'num_features_missing': 0,
            'num_activations': 0
        }

        for i in tqdm(range(0, len(texts), args.batch_size), desc="Processing batches"):
            batch_texts = texts[i:i + args.batch_size]

            batch_stats = process_batch(
                texts=batch_texts,
                dataset_id=dataset_id,
                server_url=args.server_url,
                model_id=args.model_id,
                layer=args.layer,
                top_k=args.top_k,
                batch_size=args.batch_size
            )

            if 'error' not in batch_stats:
                total_stats['num_samples_processed'] += batch_stats['num_samples_processed']
                total_stats['num_samples_failed'] += batch_stats['num_samples_failed']
                total_stats['num_activations'] += batch_stats['num_activations']
                # Note: feature counts are per batch, not cumulative

        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}")
        print(f"  Total samples processed: {total_stats['num_samples_processed']}")
        print(f"  Total samples failed: {total_stats['num_samples_failed']}")
        print(f"  Total activation records created: {total_stats['num_activations']}")
        print(f"{'='*60}")

    else:
        print("Error: Provide either --text or --file")
        print("\nExamples:")
        print("  Single text:  python extract_features.py --text 'hello world'")
        print("  From CSV:     python extract_features.py --file data.csv --text-column 'text'")
        print("  From parquet: python extract_features.py --file data.parquet --limit 100")


if __name__ == "__main__":
    main()
