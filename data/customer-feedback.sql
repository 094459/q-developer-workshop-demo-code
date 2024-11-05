-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Surveys table
CREATE TABLE surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR NOT NULL,
    description TEXT,
    creator_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- Survey options table
CREATE TABLE survey_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    text VARCHAR NOT NULL,
    FOREIGN KEY (survey_id) REFERENCES surveys(id)
);

-- Survey responses table
CREATE TABLE survey_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    respondent_email VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(id),
    FOREIGN KEY (option_id) REFERENCES survey_options(id)
);

-- Trigger to update the 'updated_at' field in the surveys table
CREATE TRIGGER update_survey_timestamp 
AFTER UPDATE ON surveys
FOR EACH ROW
BEGIN
    UPDATE surveys SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Trigger to check the number of options for a survey (on insert)
CREATE TRIGGER check_survey_options_insert
AFTER INSERT ON survey_options
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM survey_options WHERE survey_id = NEW.survey_id) > 5 THEN
            RAISE(ABORT, 'A survey cannot have more than 5 options')
    END;
END;

-- Trigger to check the number of options for a survey (on delete)
CREATE TRIGGER check_survey_options_delete
AFTER DELETE ON survey_options
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM survey_options WHERE survey_id = OLD.survey_id) < 2 THEN
            RAISE(ABORT, 'A survey must have at least 2 options')
    END;
END;
