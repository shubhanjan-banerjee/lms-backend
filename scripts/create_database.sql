-- SQL script to create the LMS database and user (run as MySQL root or admin)

-- This script will drop the existing database and user if they exist, then create a new database and user with the necessary privileges.
-- DROP USER IF EXISTS 'lmsadmindbuser'@'localhost';
-- DROP DATABASE IF EXISTS lmsdb;

-- Create the LMS database and user
-- CREATE DATABASE IF NOT EXISTS lmsdb;

-- Create the user
-- CREATE USER 'lmsadmindbuser'@'localhost' IDENTIFIED BY 'password1234';
-- GRANT ALL PRIVILEGES ON lmsdb.* TO 'lmsadmindbuser'@'localhost';
-- FLUSH PRIVILEGES;

-- Ensure the user uses the mysql_native_password plugin for compatibility with SQLAlchemy
-- ALTER USER 'lmsadmindbuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password1234';

-- To use with SQLAlchemy, ensure your .env DATABASE_URL is like:
-- mysql+mysqlconnector://lmsadmindbuser:password1234@host:port/lmsdb;

USE lmsdb;

-- Drop Tables in reverse order of dependency to avoid foreign key constraints issues
DROP TABLE IF EXISTS user_course_progress;
DROP TABLE IF EXISTS user_learning_paths;
DROP TABLE IF EXISTS learning_path_courses;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS role_skill_requirements;
DROP TABLE IF EXISTS user_skills;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS learning_paths;
DROP TABLE IF EXISTS project_roles;
DROP TABLE IF EXISTS proficiency_levels;
DROP TABLE IF EXISTS skills;

--
-- Table structure for table `proficiency_levels`
--
CREATE TABLE proficiency_levels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

--
-- Table structure for table `skills`
--
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

--
-- Table structure for table `project_roles`
--
CREATE TABLE project_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

--
-- Table structure for table `users`
--
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sso_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Developer', -- e.g., 'Admin', 'Developer'
    current_project_role_id INT,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (current_project_role_id) REFERENCES project_roles(id)
);

--
-- Table structure for table `user_skills`
--
CREATE TABLE user_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level_id INT NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (proficiency_level_id) REFERENCES proficiency_levels(id) ON DELETE CASCADE,
    UNIQUE (user_id, skill_id) -- A user can only have one entry for a specific skill
);

--
-- Table structure for table `role_skill_requirements`
--
CREATE TABLE role_skill_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_role_id INT NOT NULL,
    skill_id INT NOT NULL,
    min_proficiency_level_id INT NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (project_role_id) REFERENCES project_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (min_proficiency_level_id) REFERENCES proficiency_levels(id) ON DELETE CASCADE,
    UNIQUE (project_role_id, skill_id) -- A role has one requirement per skill
);

--
-- Table structure for table `courses`
--
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    provider VARCHAR(255),
    duration_hours INT,
    skill_id INT,
    recommended_proficiency_level_id INT,
    image_url VARCHAR(255),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    FOREIGN KEY (recommended_proficiency_level_id) REFERENCES proficiency_levels(id) ON DELETE SET NULL
);

--
-- Table structure for table `learning_paths`
--
CREATE TABLE learning_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

--
-- Table structure for table `learning_path_courses`
--
CREATE TABLE learning_path_courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learning_path_id INT NOT NULL,
    course_id INT NOT NULL,
    sequence_order INT NOT NULL,
    FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE (learning_path_id, course_id) -- A course is part of a learning path once
);

--
-- Table structure for table `user_learning_paths`
--
CREATE TABLE user_learning_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    learning_path_id INT NOT NULL,
    assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Assigned', -- 'Assigned', 'Registered', 'In Progress', 'Completed'
    completion_date DATETIME,
    is_mandatory_by_system BOOLEAN NOT NULL DEFAULT FALSE,
    is_registered_by_developer BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id) ON DELETE CASCADE,
    UNIQUE (user_id, learning_path_id) -- A user can be assigned/register for a learning path once
);

--
-- Table structure for table `user_course_progress`
--
CREATE TABLE user_course_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Not Started', -- 'Not Started', 'In Progress', 'Completed'
    progress_percentage INT NOT NULL DEFAULT 0,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completion_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE (user_id, course_id) -- A user has one progress entry per course
);

--
-- Table structure for table `audit_logs`
--
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_user_id) REFERENCES users(id) ON DELETE CASCADE
);

--
-- Sample Data
--

-- Proficiency Levels (10 entries)
INSERT INTO proficiency_levels (id, name, description) VALUES
(1, 'Beginner', 'Basic understanding and limited practical experience.'),
(2, 'Novice', 'Some theoretical knowledge, minimal practical application.'),
(3, 'Intermediate', 'Solid understanding, capable of independent work on moderate tasks.'),
(4, 'Proficient', 'Strong grasp, can handle complex tasks, mentor others.'),
(5, 'Advanced', 'In-depth expertise, recognized as a subject matter expert.'),
(6, 'Expert', 'Leading authority, innovates and sets standards.'),
(7, 'Master', 'Exceptional, globally recognized thought leader.'),
(8, 'Fundamental', 'Core concepts understood.'),
(9, 'Working Knowledge', 'Can perform tasks with some guidance.'),
(10, 'Highly Proficient', 'Can perform tasks efficiently and mentor peers.');

-- Skills (Now 13 entries to include HTML, CSS, FastAPI)
INSERT INTO skills (id, name, description) VALUES
(1, 'Python', 'General-purpose programming language for backend, data science, and scripting.'),
(2, 'JavaScript', 'Core language for web development, both frontend and backend.'),
(3, 'SQL', 'Structured Query Language for database management.'),
(4, 'AWS Cloud', 'Amazon Web Services cloud computing platform.'),
(5, 'React.js', 'JavaScript library for building user interfaces.'),
(6, 'Angular', 'TypeScript-based open-source web application framework.'),
(7, 'Docker', 'Platform for developing, shipping, and running applications in containers.'),
(8, 'Kubernetes', 'Open-source system for automating deployment, scaling, and management of containerized applications.'),
(9, 'Data Analysis', 'Process of inspecting, cleansing, transforming, and modeling data.'),
(10, 'Machine Learning', 'AI field that enables systems to learn from data.'),
(11, 'HTML', 'Standard markup language for creating web pages.'), -- Added missing skill
(12, 'CSS', 'Stylesheet language used for describing the presentation of a document written in HTML.'), -- Added missing skill
(13, 'FastAPI', 'Modern, fast (high-performance) web framework for building APIs with Python 3.7+.'); -- Added missing skill

-- Project Roles (10 entries)
INSERT INTO project_roles (id, name, description) VALUES
(1, 'Frontend Developer', 'Develops user-facing web applications.'),
(2, 'Backend Developer', 'Builds server-side logic and databases.'),
(3, 'Fullstack Developer', 'Works on both frontend and backend.'),
(4, 'DevOps Engineer', 'Manages infrastructure, CI/CD, and deployment.'),
(5, 'Data Scientist', 'Analyzes and interprets complex data.'),
(6, 'Technical Lead', 'Leads a technical team and guides architectural decisions.'),
(7, 'QA Engineer', 'Ensures software quality through testing.'),
(8, 'Product Owner', 'Defines and prioritizes product backlog.'),
(9, 'Scrum Master', 'Facilitates agile development processes.'),
(10, 'Cloud Architect', 'Designs cloud infrastructure and solutions.');

-- Users (10 entries, 2 Admin, 8 Developer)
-- Passwords are 'password123' hashed with bcrypt.
-- You should replace 'hashed_password' with actual bcrypt hashes for production.
-- Example hash for 'password123': $2b$12$EXAMPLE_HASH_STRING_GOES_HERE
-- For simplicity in this script, we'll use a placeholder.
-- In a real scenario, you'd generate these hashes programmatically.
INSERT INTO users (id, sso_id, email, first_name, last_name, hashed_password, role, current_project_role_id) VALUES
(1, 'admin.user1', 'admin1@example.com', 'Alice', 'Admin', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Admin', NULL), -- Placeholder hash
(2, 'admin.user2', 'admin2@example.com', 'Bob', 'Admin', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Admin', NULL), -- Placeholder hash
(3, 'dev.john', 'john.doe@example.com', 'John', 'Doe', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Frontend Developer')),
(4, 'dev.jane', 'jane.smith@example.com', 'Jane', 'Smith', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Backend Developer')),
(5, 'dev.peter', 'peter.jones@example.com', 'Peter', 'Jones', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Fullstack Developer')),
(6, 'dev.mary', 'mary.brown@example.com', 'Mary', 'Brown', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'DevOps Engineer')),
(7, 'dev.chris', 'chris.green@example.com', 'Chris', 'Green', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Data Scientist')),
(8, 'dev.sara', 'sara.white@example.com', 'Sara', 'White', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Frontend Developer')),
(9, 'dev.mike', 'mike.black@example.com', 'Mike', 'Black', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Backend Developer')),
(10, 'dev.lisa', 'lisa.taylor@example.com', 'Lisa', 'Taylor', '$2b$12$s0m3h4shf0r4dm1np4ssw0rd.s0me0th3rch4rs', 'Developer', (SELECT id FROM project_roles WHERE name = 'Fullstack Developer'));

-- User Skills (Many entries to demonstrate various skills for users)
INSERT INTO user_skills (id, user_id, skill_id, proficiency_level_id) VALUES
(1, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'JavaScript'), (SELECT id FROM proficiency_levels WHERE name = 'Advanced')),
(2, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'React.js'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(3, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'HTML'), (SELECT id FROM proficiency_levels WHERE name = 'Expert')),
(4, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'CSS'), (SELECT id FROM proficiency_levels WHERE name = 'Expert')),
(5, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'Angular'), (SELECT id FROM proficiency_levels WHERE name = 'Beginner')),
(6, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Novice')),
(7, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Fundamental')),
(8, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM skills WHERE name = 'AWS Cloud'), (SELECT id FROM proficiency_levels WHERE name = 'Beginner')),

(9, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Advanced')),
(10, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(11, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM skills WHERE name = 'FastAPI'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')), -- FastAPI skill now exists
(12, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM skills WHERE name = 'Docker'), (SELECT id FROM proficiency_levels WHERE name = 'Novice')),
(13, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM skills WHERE name = 'AWS Cloud'), (SELECT id FROM proficiency_levels WHERE name = 'Beginner')),

(14, (SELECT id FROM users WHERE sso_id = 'dev.peter'), (SELECT id FROM skills WHERE name = 'JavaScript'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(15, (SELECT id FROM users WHERE sso_id = 'dev.peter'), (SELECT id FROM skills WHERE name = 'React.js'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')),
(16, (SELECT id FROM users WHERE sso_id = 'dev.peter'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')),
(17, (SELECT id FROM users WHERE sso_id = 'dev.peter'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Working Knowledge')),

(18, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM skills WHERE name = 'AWS Cloud'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(19, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM skills WHERE name = 'Docker'), (SELECT id FROM proficiency_levels WHERE name = 'Advanced')),
(20, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM skills WHERE name = 'Kubernetes'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')),
(21, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Working Knowledge')),

(22, (SELECT id FROM users WHERE sso_id = 'dev.chris'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Advanced')),
(23, (SELECT id FROM users WHERE sso_id = 'dev.chris'), (SELECT id FROM skills WHERE name = 'Data Analysis'), (SELECT id FROM proficiency_levels WHERE name = 'Expert')),
(24, (SELECT id FROM users WHERE sso_id = 'dev.chris'), (SELECT id FROM skills WHERE name = 'Machine Learning'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(25, (SELECT id FROM users WHERE sso_id = 'dev.chris'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Working Knowledge')), -- Corrected line

(26, (SELECT id FROM users WHERE sso_id = 'dev.sara'), (SELECT id FROM skills WHERE name = 'JavaScript'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')),
(27, (SELECT id FROM users WHERE sso_id = 'dev.sara'), (SELECT id FROM skills WHERE name = 'Angular'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(28, (SELECT id FROM users WHERE sso_id = 'dev.sara'), (SELECT id FROM skills WHERE name = 'HTML'), (SELECT id FROM proficiency_levels WHERE name = 'Highly Proficient')),
(29, (SELECT id FROM users WHERE sso_id = 'dev.sara'), (SELECT id FROM skills WHERE name = 'CSS'), (SELECT id FROM proficiency_levels WHERE name = 'Highly Proficient')),

(30, (SELECT id FROM users WHERE sso_id = 'dev.mike'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(31, (SELECT id FROM users WHERE sso_id = 'dev.mike'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Advanced')),
(32, (SELECT id FROM users WHERE sso_id = 'dev.mike'), (SELECT id FROM skills WHERE name = 'Docker'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')),

(33, (SELECT id FROM users WHERE sso_id = 'dev.lisa'), (SELECT id FROM skills WHERE name = 'React.js'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient')),
(34, (SELECT id FROM users WHERE sso_id = 'dev.lisa'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Working Knowledge')),
(35, (SELECT id FROM users WHERE sso_id = 'dev.lisa'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate')),
(36, (SELECT id FROM users WHERE sso_id = 'dev.lisa'), (SELECT id FROM skills WHERE name = 'AWS Cloud'), (SELECT id FROM proficiency_levels WHERE name = 'Beginner'));

-- Role Skill Requirements (10 entries for various roles)
INSERT INTO role_skill_requirements (id, project_role_id, skill_id, min_proficiency_level_id, is_mandatory) VALUES
(1, (SELECT id FROM project_roles WHERE name = 'Frontend Developer'), (SELECT id FROM skills WHERE name = 'JavaScript'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),
(2, (SELECT id FROM project_roles WHERE name = 'Frontend Developer'), (SELECT id FROM skills WHERE name = 'React.js'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), TRUE),
(3, (SELECT id FROM project_roles WHERE name = 'Frontend Developer'), (SELECT id FROM skills WHERE name = 'HTML'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),
(4, (SELECT id FROM project_roles WHERE name = 'Frontend Developer'), (SELECT id FROM skills WHERE name = 'CSS'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),

(5, (SELECT id FROM project_roles WHERE name = 'Backend Developer'), (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),
(6, (SELECT id FROM project_roles WHERE name = 'Backend Developer'), (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),
(7, (SELECT id FROM project_roles WHERE name = 'Backend Developer'), (SELECT id FROM skills WHERE name = 'Docker'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), FALSE), -- Optional

(8, (SELECT id FROM project_roles WHERE name = 'DevOps Engineer'), (SELECT id FROM skills WHERE name = 'AWS Cloud'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),
(9, (SELECT id FROM project_roles WHERE name = 'DevOps Engineer'), (SELECT id FROM skills WHERE name = 'Docker'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), TRUE),
(10, (SELECT id FROM project_roles WHERE name = 'DevOps Engineer'), (SELECT id FROM skills WHERE name = 'Kubernetes'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), TRUE);


-- Courses (10 entries)
INSERT INTO courses (id, name, description, provider, duration_hours, skill_id, recommended_proficiency_level_id, image_url) VALUES
(1, 'React Hooks Masterclass', 'Master React Hooks for efficient state management.', 'Udemy', 15, (SELECT id FROM skills WHERE name = 'React.js'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), 'https://placehold.co/400x250/06B6D4/FFFFFF?text=React+Hooks'),
(2, 'Advanced Python for Data Science', 'Deep dive into Python libraries for data analysis and ML.', 'Coursera', 25, (SELECT id FROM skills WHERE name = 'Python'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), 'https://placehold.co/400x250/22C55E/FFFFFF?text=Python+DS'),
(3, 'SQL Fundamentals for Developers', 'Learn essential SQL queries for database interaction.', 'edX', 10, (SELECT id FROM skills WHERE name = 'SQL'), (SELECT id FROM proficiency_levels WHERE name = 'Beginner'), 'https://placehold.co/400x250/FACC15/0F172A?text=SQL+Basics'),
(4, 'AWS Certified Solutions Architect - Associate', 'Prepare for the AWS Solutions Architect Associate exam.', 'A Cloud Guru', 40, (SELECT id FROM skills WHERE name = 'AWS Cloud'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), 'https://placehold.co/400x250/EC4899/FFFFFF?text=AWS+Cert'),
(5, 'Angular Reactive Forms Deep Dive', 'Understand and implement reactive forms in Angular applications.', 'Pluralsight', 12, (SELECT id FROM skills WHERE name = 'Angular'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), 'https://placehold.co/400x250/EF4444/FFFFFF?text=Angular+Forms'),
(6, 'Dockerizing Your Applications', 'Containerize your applications using Docker.', 'Udemy', 8, (SELECT id FROM skills WHERE name = 'Docker'), (SELECT id FROM proficiency_levels WHERE name = 'Beginner'), 'https://placehold.co/400x250/8B5CF6/FFFFFF?text=Dockerize'),
(7, 'Kubernetes for Beginners', 'Introduction to Kubernetes for orchestrating containers.', 'Coursera', 20, (SELECT id FROM skills WHERE name = 'Kubernetes'), (SELECT id FROM proficiency_levels WHERE name = 'Novice'), 'https://placehold.co/400x250/0EA5E9/FFFFFF?text=K8s'),
(8, 'Machine Learning with Python', 'A comprehensive course on machine learning algorithms with Python.', 'Udacity', 30, (SELECT id FROM skills WHERE name = 'Machine Learning'), (SELECT id FROM proficiency_levels WHERE name = 'Intermediate'), 'https://placehold.co/400x250/FB923C/FFFFFF?text=ML+Python'),
(9, 'Effective Data Storytelling', 'Communicate insights effectively using data visualization.', 'LinkedIn Learning', 6, (SELECT id FROM skills WHERE name = 'Data Analysis'), (SELECT id FROM proficiency_levels WHERE name = 'Proficient'), 'https://placehold.co/400x250/A78BFA/FFFFFF?text=Data+Story'),
(10, 'DevOps Fundamentals', 'Introduction to DevOps principles and practices.', 'Coursera', 18, NULL, NULL, 'https://placehold.co/400x250/6EE7B7/FFFFFF?text=DevOps');


-- Learning Paths (10 entries)
INSERT INTO learning_paths (id, name, description) VALUES
(1, 'Frontend Master Track', 'Comprehensive path to become a senior frontend developer.'),
(2, 'Backend Engineering Excellence', 'Deep dive into building scalable backend systems.'),
(3, 'Fullstack Journey', 'Covers both frontend and backend development.'),
(4, 'Cloud Native DevOps', 'Mastering DevOps practices in cloud environments.'),
(5, 'Data Scientist Career Path', 'From data analysis to advanced machine learning.'),
(6, 'SQL Database Administrator', 'Path for becoming a proficient SQL DBA.'),
(7, 'Certified AWS Professional', 'All courses needed for AWS certifications.'),
(8, 'Container Orchestration Expert', 'Learn Docker and Kubernetes in depth.'),
(9, 'Agile Development Practices', 'Learn how to work effectively in agile teams.'),
(10, 'Enterprise Java Development', 'Path for building robust enterprise applications.');


-- Learning Path Courses (Sample mappings for 10 paths, varied courses)
INSERT INTO learning_path_courses (id, learning_path_id, course_id, sequence_order) VALUES
(1, (SELECT id FROM learning_paths WHERE name = 'Frontend Master Track'), (SELECT id FROM courses WHERE name = 'React Hooks Masterclass'), 1),
(2, (SELECT id FROM learning_paths WHERE name = 'Frontend Master Track'), (SELECT id FROM courses WHERE name = 'Angular Reactive Forms Deep Dive'), 2),

(3, (SELECT id FROM learning_paths WHERE name = 'Backend Engineering Excellence'), (SELECT id FROM courses WHERE name = 'Advanced Python for Data Science'), 1),
(4, (SELECT id FROM learning_paths WHERE name = 'Backend Engineering Excellence'), (SELECT id FROM courses WHERE name = 'SQL Fundamentals for Developers'), 2),

(5, (SELECT id FROM learning_paths WHERE name = 'Fullstack Journey'), (SELECT id FROM courses WHERE name = 'React Hooks Masterclass'), 1),
(6, (SELECT id FROM learning_paths WHERE name = 'Fullstack Journey'), (SELECT id FROM courses WHERE name = 'Advanced Python for Data Science'), 2),

(7, (SELECT id FROM learning_paths WHERE name = 'Cloud Native DevOps'), (SELECT id FROM courses WHERE name = 'AWS Certified Solutions Architect - Associate'), 1),
(8, (SELECT id FROM learning_paths WHERE name = 'Cloud Native DevOps'), (SELECT id FROM courses WHERE name = 'Dockerizing Your Applications'), 2),
(9, (SELECT id FROM learning_paths WHERE name = 'Cloud Native DevOps'), (SELECT id FROM courses WHERE name = 'Kubernetes for Beginners'), 3),

(10, (SELECT id FROM learning_paths WHERE name = 'Data Scientist Career Path'), (SELECT id FROM courses WHERE name = 'Advanced Python for Data Science'), 1),
(11, (SELECT id FROM learning_paths WHERE name = 'Data Scientist Career Path'), (SELECT id FROM courses WHERE name = 'Machine Learning with Python'), 2),
(12, (SELECT id FROM learning_paths WHERE name = 'Data Scientist Career Path'), (SELECT id FROM courses WHERE name = 'Effective Data Storytelling'), 3),

(13, (SELECT id FROM learning_paths WHERE name = 'SQL Database Administrator'), (SELECT id FROM courses WHERE name = 'SQL Fundamentals for Developers'), 1),

(14, (SELECT id FROM learning_paths WHERE name = 'Certified AWS Professional'), (SELECT id FROM courses WHERE name = 'AWS Certified Solutions Architect - Associate'), 1),

(15, (SELECT id FROM learning_paths WHERE name = 'Container Orchestration Expert'), (SELECT id FROM courses WHERE name = 'Dockerizing Your Applications'), 1),
(16, (SELECT id FROM learning_paths WHERE name = 'Container Orchestration Expert'), (SELECT id FROM courses WHERE name = 'Kubernetes for Beginners'), 2);


-- User Learning Paths (Many entries to demonstrate various assignments)
INSERT INTO user_learning_paths (id, user_id, learning_path_id, assigned_date, status, is_mandatory_by_system, is_registered_by_developer) VALUES
(1, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM learning_paths WHERE name = 'Frontend Master Track'), '2024-01-10', 'In Progress', TRUE, FALSE),
(2, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM learning_paths WHERE name = 'Backend Engineering Excellence'), '2024-02-15', 'Assigned', TRUE, FALSE),
(3, (SELECT id FROM users WHERE sso_id = 'dev.peter'), (SELECT id FROM learning_paths WHERE name = 'Fullstack Journey'), '2024-03-01', 'In Progress', FALSE, TRUE), -- Optional
(4, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM learning_paths WHERE name = 'Cloud Native DevOps'), '2024-01-20', 'In Progress', TRUE, FALSE),
(5, (SELECT id FROM users WHERE sso_id = 'dev.chris'), (SELECT id FROM learning_paths WHERE name = 'Data Scientist Career Path'), '2024-04-05', 'Assigned', TRUE, FALSE),
(6, (SELECT id FROM users WHERE sso_id = 'dev.sara'), (SELECT id FROM learning_paths WHERE name = 'Frontend Master Track'), '2024-01-15', 'Completed', TRUE, FALSE),
(7, (SELECT id FROM users WHERE sso_id = 'dev.mike'), (SELECT id FROM learning_paths WHERE name = 'Backend Engineering Excellence'), '2024-03-10', 'In Progress', TRUE, FALSE),
(8, (SELECT id FROM users WHERE sso_id = 'dev.lisa'), (SELECT id FROM learning_paths WHERE name = 'Fullstack Journey'), '2024-02-20', 'Assigned', FALSE, TRUE), -- Optional
(9, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM learning_paths WHERE name = 'Certified AWS Professional'), '2024-05-01', 'Assigned', FALSE, TRUE), -- Optional for John
(10, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM learning_paths WHERE name = 'Container Orchestration Expert'), '2024-04-10', 'In Progress', FALSE, TRUE); -- Optional for Mary


-- User Course Progress (Many entries to demonstrate various progress states)
INSERT INTO user_course_progress (id, user_id, course_id, status, progress_percentage, last_accessed, completion_date) VALUES
(1, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM courses WHERE name = 'React Hooks Masterclass'), 'In Progress', 75, '2024-06-19 10:00:00', NULL),
(2, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM courses WHERE name = 'Angular Reactive Forms Deep Dive'), 'Not Started', 0, '2024-06-18 09:00:00', NULL),
(3, (SELECT id FROM users WHERE sso_id = 'dev.jane'), (SELECT id FROM courses WHERE name = 'Advanced Python for Data Science'), 'Not Started', 0, '2024-06-17 11:00:00', NULL),
(4, (SELECT id FROM users WHERE sso_id = 'dev.peter'), (SELECT id FROM courses WHERE name = 'React Hooks Masterclass'), 'In Progress', 40, '2024-06-16 12:00:00', NULL),
(5, (SELECT id FROM users WHERE sso_id = 'dev.mary'), (SELECT id FROM courses WHERE name = 'AWS Certified Solutions Architect - Associate'), 'In Progress', 60, '2024-06-15 13:00:00', NULL),
(6, (SELECT id FROM users WHERE sso_id = 'dev.chris'), (SELECT id FROM courses WHERE name = 'Advanced Python for Data Science'), 'Not Started', 0, '2024-06-14 14:00:00', NULL),
(7, (SELECT id FROM users WHERE sso_id = 'dev.sara'), (SELECT id FROM courses WHERE name = 'React Hooks Masterclass'), 'Completed', 100, '2024-05-30 15:00:00', '2024-05-30 15:00:00'),
(8, (SELECT id FROM users WHERE sso_id = 'dev.mike'), (SELECT id FROM courses WHERE name = 'Advanced Python for Data Science'), 'In Progress', 20, '2024-06-13 16:00:00', NULL),
(9, (SELECT id FROM users WHERE sso_id = 'dev.lisa'), (SELECT id FROM courses WHERE name = 'React Hooks Masterclass'), 'Not Started', 0, '2024-06-12 17:00:00', NULL),
(10, (SELECT id FROM users WHERE sso_id = 'dev.john'), (SELECT id FROM courses WHERE name = 'SQL Fundamentals for Developers'), 'In Progress', 90, '2024-06-20 09:30:00', NULL);


-- Audit Logs (Many entries to demonstrate various admin actions)
INSERT INTO audit_logs (id, admin_user_id, action, details, timestamp) VALUES
(1, (SELECT id FROM users WHERE sso_id = 'admin.user1'), 'Manual Role Change', '{"user_id": 3, "old_role": "Developer", "new_role": "Frontend Developer"}', '2024-06-01 08:00:00'),
(2, (SELECT id FROM users WHERE sso_id = 'admin.user2'), 'Skill Matrix Upload', '{"filename": "skill_matrix_v1.xlsx", "rows_processed": 50}', '2024-06-02 09:15:00'),
(3, (SELECT id FROM users WHERE sso_id = 'admin.user1'), 'Assigned Learning Path', '{"user_id": 3, "learning_path_id": 1}', '2024-06-03 10:30:00'),
(4, (SELECT id FROM users WHERE sso_id = 'admin.user1'), 'Bulk Assigned Courses', '{"users_count": 5, "courses_count": 3}', '2024-06-04 11:45:00'),
(5, (SELECT id FROM users WHERE sso_id = 'admin.user2'), 'Updated User Skill', '{"user_id": 4, "skill_id": 1, "old_proficiency": "Novice", "new_proficiency": "Intermediate"}', '2024-06-05 13:00:00'),
(6, (SELECT id FROM users WHERE sso_id = 'admin.user1'), 'Created New Course', '{"course_name": "Advanced Data Structures"}', '2024-06-06 14:15:00'),
(7, (SELECT id FROM users WHERE sso_id = 'admin.user2'), 'Deleted Project Role', '{"role_name": "Junior Developer"}', '2024-06-07 15:30:00'),
(8, (SELECT id FROM users WHERE sso_id = 'admin.user1'), 'Updated Learning Path', '{"learning_path_id": 2, "changes": "Added 2 new courses"}', '2024-06-08 16:45:00'),
(9, (SELECT id FROM users WHERE sso_id = 'admin.user1'), 'Reviewed Compliance Report', '{"report_date": "2024-06-01", "overall_compliance": "70%"}', '2024-06-09 17:00:00'),
(10, (SELECT id FROM users WHERE sso_id = 'admin.user2'), 'Adjusted User Skill', '{"user_id": 5, "skill_id": 2, "proficiency": "Expert"}', '2024-06-10 10:00:00');

