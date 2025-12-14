## Fetch Data (Optional)
Optional if STREAM_FROM_DISK = false in the stream_*.py scripts
First, fetch data from neuronpedia with fetch-DATASET.py
activations - 20GB
explanations - 0.6 GB
features - 0.5 GB

## Insert to postgres
Make sure DATABASE_URL connection string is set in .env or environment
```bash
export DATABASE_URL=psycopg2://user:pass@host:port/database
```
Stream each type of data
```bash
python stream_explanations_to_db.py
```
If STREAM_FROM_DISK is true, will use previously saved data