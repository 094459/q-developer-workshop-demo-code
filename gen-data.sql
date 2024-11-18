-- Insert 10 sample users
INSERT INTO users (email, password_hash, created_at) VALUES
('user1@example.com', 'hash1', CURRENT_TIMESTAMP),
('user2@example.com', 'hash2', CURRENT_TIMESTAMP),
('user3@example.com', 'hash3', CURRENT_TIMESTAMP),
('user4@example.com', 'hash4', CURRENT_TIMESTAMP),
('user5@example.com', 'hash5', CURRENT_TIMESTAMP),
('user6@example.com', 'hash6', CURRENT_TIMESTAMP),
('user7@example.com', 'hash7', CURRENT_TIMESTAMP),
('user8@example.com', 'hash8', CURRENT_TIMESTAMP),
('user9@example.com', 'hash9', CURRENT_TIMESTAMP),
('user10@example.com', 'hash10', CURRENT_TIMESTAMP);

-- Insert 100 surveys (10 surveys per user)
INSERT INTO surveys (title, description, creator_id, created_at, updated_at) 
SELECT 
    'Survey ' || seq as title,
    'Description for survey ' || seq as description,
    ((seq - 1) % 10) + 1 as creator_id,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM (
    WITH RECURSIVE cnt(seq) AS (
        SELECT 1
        UNION ALL
        SELECT seq + 1 FROM cnt WHERE seq < 100
    )
    SELECT seq FROM cnt
);

-- Insert survey options (3 options per survey)
INSERT INTO survey_options (survey_id, text)
SELECT 
    s.id,
    'Option ' || 
    CASE num
        WHEN 1 THEN 'A'
        WHEN 2 THEN 'B'
        WHEN 3 THEN 'C'
    END || ' for Survey ' || s.id
FROM surveys s
CROSS JOIN (
    SELECT 1 as num UNION ALL SELECT 2 UNION ALL SELECT 3
) options;

-- Insert sample feedback (2 feedbacks per survey)
INSERT INTO feedbacks (survey_id, option_id, user_email, comment, created_at)
SELECT 
    s.id,
    so.id,
    'respondent' || (ROW_NUMBER() OVER (PARTITION BY s.id)) || '@example.com',
    'Feedback comment for survey ' || s.id || ' option ' || so.id,
    CURRENT_TIMESTAMP
FROM surveys s
CROSS JOIN (
    SELECT 1 as feedback_num UNION ALL SELECT 2
) f
JOIN survey_options so ON so.survey_id = s.id
GROUP BY s.id, f.feedback_num
HAVING so.id = MIN(so.id);
