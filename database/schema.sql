-- Create database with the new English name and proper charset
CREATE DATABASE IF NOT EXISTS deltascope DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE deltascope;

-- 1. Users Table (老师与学生)
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary Key',
    openid VARCHAR(64) UNIQUE NOT NULL COMMENT 'WeChat OpenID for unique identification',
    account VARCHAR(64) UNIQUE NOT NULL COMMENT 'Login Account',
    password_hash VARCHAR(128) NOT NULL COMMENT 'Password Hash',
    nickname VARCHAR(64) NOT NULL COMMENT 'User Nickname',
    avatar_url VARCHAR(255) DEFAULT '' COMMENT 'Avatar URL',
    role ENUM('teacher', 'student') NOT NULL DEFAULT 'student' COMMENT 'User Role (Access Control)',
    total_score DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Total Score for Ranking',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Update Time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User Table';

-- 2. Questions Table (每周一题题目表)
CREATE TABLE IF NOT EXISTS questions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Question ID',
    teacher_id BIGINT NOT NULL COMMENT 'Creator (Teacher) ID',
    title VARCHAR(128) NOT NULL COMMENT 'Question Title',
    content TEXT NOT NULL COMMENT 'Text Content/Description',
    image_urls JSON NOT NULL COMMENT 'Array of Image URLs',
    max_score DECIMAL(10,2) NOT NULL COMMENT 'Maximum Possible Score',
    deadline DATETIME NOT NULL COMMENT 'Submission Deadline',
    status ENUM('draft', 'published', 'closed') NOT NULL DEFAULT 'published' COMMENT 'Question Status',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Update Time',
    KEY idx_questions_teacher (teacher_id),
    KEY idx_questions_deadline (deadline),
    KEY idx_questions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Weekly Questions Table';

-- 3. Submissions Table (学生作答与老师批改表)
CREATE TABLE IF NOT EXISTS submissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Submission ID',
    question_id BIGINT NOT NULL COMMENT 'Related Question ID',
    student_id BIGINT NOT NULL COMMENT 'Submitting Student ID',
    answer_image_urls JSON NOT NULL COMMENT 'Array of Answer Image URLs',
    score DECIMAL(10,2) DEFAULT NULL COMMENT 'Given Score (null means ungraded)',
    teacher_comment VARCHAR(500) DEFAULT NULL COMMENT 'Teacher Feedback',
    status ENUM('submitted', 'graded') NOT NULL DEFAULT 'submitted' COMMENT 'Grading Status',
    submit_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Submission Time',
    graded_at DATETIME DEFAULT NULL COMMENT 'Time of Grading',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Update Time',
    UNIQUE KEY uk_submissions_question_student (question_id, student_id) COMMENT 'One submission per student per question',
    KEY idx_submissions_question_status (question_id, status),
    KEY idx_submissions_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Student Submissions Table';
