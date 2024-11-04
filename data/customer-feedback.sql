-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Surveys table
CREATE TABLE surveys (
    survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

-- Survey options table
CREATE TABLE survey_options (
    option_id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id)
);

-- Votes table
CREATE TABLE votes (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    ip_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id),
    FOREIGN KEY (option_id) REFERENCES survey_options(option_id)
);

-- Trigger to ensure surveys have between 2 and 5 options
CREATE TRIGGER check_survey_options
AFTER INSERT ON survey_options
BEGIN
    SELECT CASE 
        WHEN (SELECT COUNT(*) FROM survey_options WHERE survey_id = NEW.survey_id) > 5
        THEN RAISE(ABORT, 'A survey cannot have more than 5 options')
    END;
END;

-- Trigger to prevent deletion if it would result in less than 2 options
CREATE TRIGGER ensure_minimum_options
BEFORE DELETE ON survey_options
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM survey_options WHERE survey_id = OLD.survey_id) <= 2
        THEN RAISE(ABORT, 'A survey must have at least 2 options')
    END;
END;
