CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";


CREATE TABLE verification_token
(
  identifier TEXT NOT NULL,
  expires TIMESTAMPTZ NOT NULL,
  token TEXT NOT NULL,
 
  PRIMARY KEY (identifier, token)
);
 
CREATE TABLE accounts
(
  id SERIAL,
  "userId" INTEGER NOT NULL,
  type VARCHAR(255) NOT NULL,
  provider VARCHAR(255) NOT NULL,
  "providerAccountId" VARCHAR(255) NOT NULL,
  refresh_token TEXT,
  access_token TEXT,
  expires_at BIGINT,
  id_token TEXT,
  scope TEXT,
  session_state TEXT,
  token_type TEXT,
 
  PRIMARY KEY (id)
);
 
CREATE TABLE sessions
(
  id SERIAL,
  "userId" INTEGER NOT NULL,
  expires TIMESTAMPTZ NOT NULL,
  "sessionToken" VARCHAR(255) NOT NULL,
 
  PRIMARY KEY (id)
);
 
CREATE TABLE users
(
  id SERIAL,
  name VARCHAR(255),
  email VARCHAR(255),
  "emailVerified" TIMESTAMPTZ,
  image TEXT,
 
  PRIMARY KEY (id)
);

CREATE TABLE samples(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID,
    "tokens" TEXT[],
    sample_text TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by INTEGER
);
 

CREATE TABLE "features" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "model_id" TEXT NOT NULL,
    "layer" TEXT NOT NULL,
    feature_index INTEGER NOT NULL,
    "source_set_name" TEXT,
    "neg_str" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "neg_values" DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    "pos_str" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "pos_values" DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    "frac_nonzero" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_by" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT NOW()
);

CREATE TABLE activations(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID REFERENCES samples(id) ON DELETE CASCADE,
    feature_id UUID REFERENCES features(id) ON DELETE CASCADE, 
    "values" DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    "max_value" DOUBLE PRECISION ,
    "max_value_token_index" INTEGER ,
    "min_value" DOUBLE PRECISION ,
    "created_by" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT NOW()
);


CREATE TABLE "explanations" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_id UUID, --REFERENCES features(id) ON DELETE CASCADE,
    --temporary! just to do the mapping to feature id

--UPDATE explanations e
-- SET feature_id = f.id
-- FROM features f
-- WHERE e.layer = f.layer
-- AND e.feature_index = f.feature_index
    "model_id" TEXT NOT NULL,
    "layer" TEXT NOT NULL,
    feature_index INTEGER NOT NULL,


    "embedding" vector(256),
    "description" TEXT NOT NULL,
    "notes" TEXT,
    "type_name" TEXT,
    "explanation_model" TEXT,
    created_by INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT NOW(),
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT NOW()
);

CREATE TABLE datasets(
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
name VARCHAR(255),
description TEXT,
link VARCHAR(255), --hf id
type VARCHAR(255), --huggingface
created_at TIMESTAMP NOT NULL DEFAULT NOW(),
created_by INTEGER
);


