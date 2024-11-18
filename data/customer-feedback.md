# Customer Feedback Database Schema

## Entity Relationship Diagram

```mermaid
erDiagram
    Users {
        int user_id PK
        varchar email
        varchar password_hash
        timestamp created_at
    }
    Surveys {
        int survey_id PK
        int user_id FK
        varchar title
        text description
        timestamp created_at
        timestamp updated_at
    }
    Questions {
        int question_id PK
        int survey_id FK
        text question_text
        int question_order
    }
    Options {
        int option_id PK
        int question_id FK
        text option_text
        int option_order
    }
    Responses {
        int response_id PK
        int survey_id FK
        varchar respondent_email
        timestamp created_at
    }
    AnswerChoices {
        int answer_choice_id PK
        int response_id FK
        int question_id FK
        int option_id FK
    }

    Users ||--o{ Surveys : creates
    Surveys ||--o{ Questions : contains
    Questions ||--o{ Options : has
    Surveys ||--o{ Responses : receives
    Responses ||--o{ AnswerChoices : includes
    Questions ||--o{ AnswerChoices : answers
    Options ||--o{ AnswerChoices : selected
```

## Schema Description

This diagram represents a customer feedback system with the following components:

- Users can create multiple surveys
- Each survey contains multiple questions
- Questions have multiple choice options
- Responses are collected for each survey
- Individual answer choices are tracked for each response
