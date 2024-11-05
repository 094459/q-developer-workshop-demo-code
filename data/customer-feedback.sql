-- Users table
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Surveys table
CREATE TABLE Surveys (
    survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Questions table
CREATE TABLE Questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_order INTEGER NOT NULL,
    FOREIGN KEY (survey_id) REFERENCES Surveys(survey_id)
);

-- Options table
CREATE TABLE Options (
    option_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    option_order INTEGER NOT NULL,
    FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);

-- Responses table
CREATE TABLE Responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    respondent_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES Surveys(survey_id)
);

-- AnswerChoices table
CREATE TABLE AnswerChoices (
    answer_choice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    FOREIGN KEY (response_id) REFERENCES Responses(response_id),
    FOREIGN KEY (question_id) REFERENCES Questions(question_id),
    FOREIGN KEY (option_id) REFERENCES Options(option_id)
);
