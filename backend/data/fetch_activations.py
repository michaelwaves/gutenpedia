
import gzip
import shutil
import requests
import os

MODEL="gemma-2-9b-it"
LAYER="20-gemmascope-res-131k"
LINK="https://neuronpedia-datasets.s3.amazonaws.com/v1/{model}/{layer}/explanations/batch-{i}.jsonl.gz"
save_dir  = f"{LAYER}/{MODEL}/activations"
os.makedirs(save_dir, exist_ok=True)

for i in range(0,127):
    url = LINK.format(i=i, model=MODEL, layer=LAYER)
  
    gz_path = f"{save_dir}/batch-{i}.jsonl.gz"
    jsonl_path = f"{save_dir}/batch-{i}.jsonl"
    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(gz_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Decompression... {gz_path}")
    
    with gzip.open(gz_path, 'rb') as f_in:
        with open(jsonl_path,'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print('Saved:', jsonl_path)