CREATE TABLE IF NOT EXISTS report_jobs (
    job_id UUID PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_audio_text (
    job_id UUID REFERENCES report_jobs(job_id),
    transcript_en TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_images (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES report_jobs(job_id),
    image_data BYTEA NOT NULL,
    position INT NOT NULL
);
