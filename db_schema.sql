CREATE TABLE comments_comment (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES comments_comment(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    homepage VARCHAR(200),
    text TEXT NOT NULL,
    image VARCHAR(100),
    attachment VARCHAR(100),
    ip_address INET,
    user_agent TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX comments_comment_created_at_idx ON comments_comment (created_at DESC);
CREATE INDEX comments_comment_username_idx ON comments_comment (username);
CREATE INDEX comments_comment_email_idx ON comments_comment (email);
CREATE INDEX comments_comment_parent_idx ON comments_comment (parent_id);

CREATE TABLE comments_captchachallenge (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(64) NOT NULL UNIQUE,
    answer VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    used BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX comments_captcha_created_at_idx ON comments_captchachallenge (created_at);
