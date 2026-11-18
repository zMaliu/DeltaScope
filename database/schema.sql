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
    school VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'School',
    college VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'College',
    major VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'Major',
    grade VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'Grade',
    class_name VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'Class Name',
    real_name VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'Real Name',
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

-- 4. Learning Resources Table (课程资料与题解资源库)
CREATE TABLE IF NOT EXISTS learning_resources (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Resource ID',
    category VARCHAR(32) NOT NULL DEFAULT 'course' COMMENT 'Resource Category',
    course VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'Related Course',
    title VARCHAR(128) NOT NULL COMMENT 'Resource Title',
    summary VARCHAR(500) NOT NULL DEFAULT '' COMMENT 'Resource Summary',
    content TEXT NULL COMMENT 'Resource Content or Placeholder',
    status ENUM('draft', 'published', 'planning') NOT NULL DEFAULT 'planning' COMMENT 'Publish Status',
    sort_order INT NOT NULL DEFAULT 0 COMMENT 'Sort Order',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Update Time',
    KEY idx_learning_resources_category (category),
    KEY idx_learning_resources_status (status),
    KEY idx_learning_resources_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Learning Resources Table';

-- 5. Forum Posts Table (智库论坛帖子框架)
CREATE TABLE IF NOT EXISTS forum_posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Post ID',
    author_id BIGINT NOT NULL DEFAULT 0 COMMENT 'Author User ID',
    channel VARCHAR(32) NOT NULL DEFAULT 'qa' COMMENT 'Forum Channel',
    course VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'Related Course',
    title VARCHAR(128) NOT NULL COMMENT 'Post Title',
    content TEXT NOT NULL COMMENT 'Post Content',
    status ENUM('draft', 'published', 'archived') NOT NULL DEFAULT 'published' COMMENT 'Post Status',
    reply_count INT NOT NULL DEFAULT 0 COMMENT 'Reply Count',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Update Time',
    KEY idx_forum_posts_channel (channel),
    KEY idx_forum_posts_status (status),
    KEY idx_forum_posts_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Forum Posts Table';

-- 6. Knowledge Nodes Table (知识图谱节点)
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Node ID',
    parent_id BIGINT DEFAULT NULL COMMENT 'Parent Node ID',
    course VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'Related Course',
    name VARCHAR(64) NOT NULL COMMENT 'Node Name',
    description VARCHAR(500) NOT NULL DEFAULT '' COMMENT 'Node Description',
    difficulty INT NOT NULL DEFAULT 1 COMMENT 'Difficulty Level',
    sort_order INT NOT NULL DEFAULT 0 COMMENT 'Sort Order',
    status ENUM('planning', 'available') NOT NULL DEFAULT 'planning' COMMENT 'Node Status',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Update Time',
    KEY idx_knowledge_nodes_parent (parent_id),
    KEY idx_knowledge_nodes_course (course),
    KEY idx_knowledge_nodes_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Knowledge Graph Nodes Table';

-- 7. Learning Events Table (学习行为事件，用于学情中心)
CREATE TABLE IF NOT EXISTS learning_events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Event ID',
    user_id BIGINT NOT NULL COMMENT 'User ID',
    event_type VARCHAR(32) NOT NULL COMMENT 'Event Type',
    target_type VARCHAR(32) NOT NULL DEFAULT '' COMMENT 'Target Type',
    target_id BIGINT DEFAULT NULL COMMENT 'Target ID',
    metadata JSON NULL COMMENT 'Extra Metadata',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
    KEY idx_learning_events_user (user_id),
    KEY idx_learning_events_type (event_type),
    KEY idx_learning_events_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Learning Events Table';

-- Seed framework content for the MVP skeleton. Safe to run repeatedly.
INSERT INTO learning_resources (category, course, title, summary, content, status, sort_order)
SELECT 'course', '数学分析', '数学分析章节笔记', '沉淀学院课程配套资料、重点概念与复习提纲。', '资源库首批框架内容，后续由教师/助教/学生共建。', 'planning', 10
WHERE NOT EXISTS (SELECT 1 FROM learning_resources WHERE title = '数学分析章节笔记');

INSERT INTO learning_resources (category, course, title, summary, content, status, sort_order)
SELECT 'solution', '每周一题', '每周一题优秀解法', '收录高质量解法、典型错误与老师点评。', '用于承接每周一题活动沉淀。', 'planning', 20
WHERE NOT EXISTS (SELECT 1 FROM learning_resources WHERE title = '每周一题优秀解法');

INSERT INTO learning_resources (category, course, title, summary, content, status, sort_order)
SELECT 'exam', '考研数学', '考研数学可视化专题', '规划专题课程、题包和阶段训练。', '可视化专题将在后续版本接入。', 'planning', 30
WHERE NOT EXISTS (SELECT 1 FROM learning_resources WHERE title = '考研数学可视化专题');

INSERT INTO forum_posts (channel, course, title, content, status)
SELECT 'qa', '数学分析', '一致连续证明里有限覆盖怎么理解？', '示例帖：用于展示提问答疑区的内容形态，真实发帖将在后续开放。', 'published'
WHERE NOT EXISTS (SELECT 1 FROM forum_posts WHERE title = '一致连续证明里有限覆盖怎么理解？');

INSERT INTO forum_posts (channel, course, title, content, status)
SELECT 'share', '高等代数', '相似矩阵与线性变换视角整理', '示例帖：用于展示经验分享区的内容形态，后续可沉淀为资源库资料。', 'published'
WHERE NOT EXISTS (SELECT 1 FROM forum_posts WHERE title = '相似矩阵与线性变换视角整理');

INSERT INTO knowledge_nodes (course, name, description, difficulty, sort_order, status)
SELECT '数学分析', '极限初探', '理解极限定义、数列极限与函数极限。', 1, 10, 'available'
WHERE NOT EXISTS (SELECT 1 FROM knowledge_nodes WHERE name = '极限初探');

INSERT INTO knowledge_nodes (course, name, description, difficulty, sort_order, status)
SELECT '数学分析', '导数利刃', '掌握导数定义、几何意义与常见求导法则。', 2, 20, 'planning'
WHERE NOT EXISTS (SELECT 1 FROM knowledge_nodes WHERE name = '导数利刃');

INSERT INTO knowledge_nodes (course, name, description, difficulty, sort_order, status)
SELECT '数学分析', '积分领地', '建立积分累加、面积与反常积分的直观理解。', 2, 30, 'planning'
WHERE NOT EXISTS (SELECT 1 FROM knowledge_nodes WHERE name = '积分领地');

INSERT INTO knowledge_nodes (course, name, description, difficulty, sort_order, status)
SELECT '数学分析', '泰勒迷宫', '理解局部近似、余项估计与级数展开。', 3, 40, 'planning'
WHERE NOT EXISTS (SELECT 1 FROM knowledge_nodes WHERE name = '泰勒迷宫');

INSERT INTO knowledge_nodes (course, name, description, difficulty, sort_order, status)
SELECT '高等代数', '线性空间', '从向量空间、基、维数理解线性结构。', 2, 50, 'planning'
WHERE NOT EXISTS (SELECT 1 FROM knowledge_nodes WHERE name = '线性空间');
