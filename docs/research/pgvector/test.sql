-- Create Extension(enables or say installs pgvector extension)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create Table (creates a table with a vector column)
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
ALTER TABLE items ADD COLUMN IF NOT EXISTS embedding vector(3);

-- Insert Data (inserts a row with a vector value)
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');

-- Upsert Data (inserts or updates a row with a vector value)
INSERT INTO items (id, embedding) VALUES (1, '[1,2,3]'), (2, '[4,5,6]')
    ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;

-- Update Data (updates a row with a new vector value)
UPDATE items SET embedding = '[1,2,3]' WHERE id = 1;

-- Delete Data (deletes a row by id)
DELETE FROM items WHERE id = 1;




