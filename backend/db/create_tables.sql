CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255),
    name VARCHAR(255),
    image TEXT,
    created_at TIMESTAMP(3) NOT NULL DEFAULT NOW()
);

CREATE TABLE activations(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id TEXT,
    dataset_id TEXT,
    "tokens" TEXT[],
    "values" DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    "index" TEXT NOT NULL,
    "layer" TEXT NOT NULL,
    "model_id" TEXT NOT NULL,
    "feature_id" UUID, 
    "max_value" DOUBLE PRECISION ,
    "max_value_token_index" INTEGER ,
    "min_value" DOUBLE PRECISION ,
    "created_by" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT NOW()
);


CREATE TABLE "features" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "model_id" TEXT NOT NULL,
    "layer" TEXT NOT NULL,
    "index" TEXT NOT NULL,
    "source_set_name" TEXT,
    "neg_str" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "neg_values" DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    "pos_str" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "pos_values" DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    "frac_nonzero" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_by" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT NOW()
);


CREATE TABLE "explanations" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "model_id" TEXT NOT NULL,
    "layer" TEXT NOT NULL,
    "index" TEXT NOT NULL,
    feature_id UUID,
    "embedding" vector(256),
    "description" TEXT NOT NULL,
    "notes" TEXT,
    "type_name" TEXT,
    "explanation_model" TEXT,
    created_by UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT NOW(),
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT NOW()
);