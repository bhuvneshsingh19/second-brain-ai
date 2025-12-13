-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the artifacts table
CREATE TABLE IF NOT EXISTS artifacts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384), -- CHANGED: 384 dimensions for Local MiniLM
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create an HNSW index
CREATE INDEX ON artifacts USING hnsw (embedding vector_cosine_ops);