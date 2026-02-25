-- Inserting Majors 

INSERT INTO majors (major_code, major_name)
VALUES 
  ('BSCS', 'Bachelor of Computer Science'),
  ('BSIT', 'Bachelor of Information Technology');

-- Inserting Main Categories

INSERT INTO main_categories (name)
VALUES 
  ('General Education'),
  ('Specialized'),
  ('Free Electives');

-- Insert BSCS653 Curriculum
INSERT INTO curriculums (curriculum_code, major_id, total_required_credits)
VALUES 
  ('BSCS653', 1, 120);

-- Insert Ranges for BSCS653
INSERT INTO curriculum_id_ranges (curriculum_id, id_start, id_end)
VALUES 
  (1, 6530000, 6899999);

-- Insert Curriculum Main Categories for BSCS653
INSERT INTO curriculum_main_categories (curriculum_id, main_category_id, required_credits)
VALUES
  (1, 1, 30),
  (1, 2, 90),
  (1, 3, 12);

--Step 1 — Insert GE Subcategories

INSERT INTO curriculum_subcategories 
(curriculum_id, main_category_id, name, required_credits, display_order)
VALUES
  (1, 1, 'Language Courses', 14, 1),
  (1, 1, 'Humanities Courses', 2, 2),
  (1, 1, 'Social Science Courses', 9, 3),
  (1, 1, 'Science and Mathematics Courses', 5, 4);

--Step 2 — Insert Specialized Subcategories

INSERT INTO curriculum_subcategories 
(curriculum_id, main_category_id, name, required_credits, display_order)
VALUES
  (1, 2, 'Core Courses', 18, 1),
  (1, 2, 'Major Courses', 39, 2),
  (1, 2, 'Major Elective Courses', 33, 3);

--Step 3 — Insert Free Electives Subcategory

INSERT INTO curriculum_subcategories 
(curriculum_id, main_category_id, name, required_credits, display_order)
VALUES
  (1, 3, 'Free Electives', 12, 1);

-- Insert Language Courses into courses from BSCS653 Curriculum
INSERT INTO courses (course_name, credits, is_english, is_sequential)
VALUES
  ('Communicative English I', 3, TRUE, TRUE),
  ('Communicative English II', 3, TRUE, TRUE),
  ('Academic English', 3, TRUE, TRUE),
  ('Advanced Academic English', 3, TRUE, TRUE),
  ('Thai for Professional Communication', 2, FALSE, FALSE),
  ('Thai Language for Multicultural Communication', 2, FALSE, FALSE),
  ('Introductory Thai Usage', 2, FALSE, FALSE);

--Insert into course_codes  

INSERT INTO course_codes (course_code, course_id)
VALUES
  ('ELE1001', 1),
  ('ELE1002', 2),
  ('ELE2000', 3),
  ('ELE2001', 4),
  ('GE1410', 5),
  ('GE1411', 6),
  ('GE1412', 7);

-- Insert Prerequisites Chain

  INSERT INTO course_prerequisites (course_id, prerequisite_course_id)
VALUES
  (2, 1),  -- ELE1002 requires ELE1001
  (3, 2),  -- ELE2000 requires ELE1002
  (4, 3);  -- ELE2001 requires ELE2000

-- Insert Minimum Grade Override

INSERT INTO curriculum_course_min_grades (curriculum_id, course_id, min_required_grade)
VALUES
  (1, 1, 'C'),
  (1, 2, 'C'),
  (1, 3, 'C'),
  (1, 4, 'C');

-- — Link Courses to Language Subcategory
INSERT INTO subcategory_course_codes (subcategory_id, course_code_id)
VALUES
  (1, 1),
  (1, 2),
  (1, 3),
  (1, 4),
  (1, 5),
  (1, 6),
  (1, 7);

-- inset into courses 
  
INSERT INTO courses (course_name, credits)
VALUES
  ('Human Civilizations and Global Citizens', 2);

-- Insert into course_codes
INSERT INTO course_codes (course_code, course_id)
VALUES
  ('GE2110', 8);

-- Link Humanities Course to Subcategory

INSERT INTO subcategory_course_codes (subcategory_id, course_code_id)
VALUES
  (2, 8);

-- Insert into courses

INSERT INTO courses (course_name, credits)
VALUES
  ('Essential Marketing for Entrepreneurs', 2),
  ('Essential Finance for Entrepreneurs', 2),
  ('Essential Economics for Entrepreneurs', 2),
  ('Ethics', 3);

-- Insert into course_codes

INSERT INTO course_codes (course_code, course_id)
VALUES
  ('BBA1004', 9),
  ('BBA1005', 10),
  ('BBA1006', 11),
  ('GE2202', 12);

-- Link Social Science Courses to Subcategory

INSERT INTO subcategory_course_codes (subcategory_id, course_code_id)
VALUES
  (3, 9),
  (3, 10),
  (3, 11),
  (3, 12);

-- Insert into courses

INSERT INTO courses (course_name, credits)
VALUES
  ('Data Analytics for Entrepreneurs', 3),
  ('Science for Sustainable Future', 2);

-- Insert into course_codes

INSERT INTO course_codes (course_code, course_id)
VALUES
  ('BBA1007', 13),
  ('GE1303', 14);

-- Link Science and Mathematics Courses to Subcategory

INSERT INTO subcategory_course_codes (subcategory_id, course_code_id)
VALUES
  (4, 13),
  (4, 14);

-- Insert into courses

INSERT INTO courses (course_name, credits)
VALUES
  ('Principles of Statistics', 3),
  ('Mathematics and Statistics for Data Science', 3),
  ('Mathematics Foundation for Computer Science', 3),
  ('Design Thinking', 3),
  ('Data Science', 3),
  ('Software Engineering', 3);

-- Insert into core course_codes
INSERT INTO course_codes (course_code, course_id)
VALUES
  ('CSX2003', 15),
  ('CSX2006', 16),
  ('CSX2008', 17),
  ('ITX2005', 18),
  ('ITX2007', 19),
  ('ITX3007', 20);

--Insert into course_prerequisites

INSERT INTO course_prerequisites (course_id, prerequisite_course_id)
VALUES
  (19, 16);

--Link Core Courses to Subcategory

INSERT INTO subcategory_course_codes (subcategory_id, course_code_id)
VALUES
  (5, 15),
  (5, 16),
  (5, 17),
  (5, 18),
  (5, 19),
  (5, 20);

--insert major courses into courses
INSERT INTO courses (course_name, credits, is_sequential)
VALUES
  ('Introduction to Information Technology', 3, FALSE),

  ('Senior Project I', 3, TRUE),
  ('Senior Project II', 3, TRUE),

  ('Fundamentals of Computer Programming', 3, FALSE),
  ('Object-Oriented Concepts and Programming', 3, FALSE),
  ('Data Structures and Algorithms', 3, FALSE),
  ('Programming Languages', 3, FALSE),
  ('Algorithm Design', 3, FALSE),

  ('Cloud Computing', 3, FALSE),
  ('Computer Networks', 3, FALSE),
  ('Database Systems', 3, FALSE),
  ('Operating Systems', 3, FALSE),
  ('Computer Architecture', 3, FALSE);

  -- Insert into course_codes for major courses

INSERT INTO course_codes (course_code, course_id)
VALUES
  ('ITX3002', 21),

  ('CSX3010', 22),
  ('CSX3011', 23),

  ('CSX3001', 24),
  ('CSX3002', 25),
  ('CSX3003', 26),
  ('CSX3004', 27),
  ('CSX3009', 28),

  ('CSX2009', 29),
  ('CSX3005', 30),
  ('CSX3006', 31),
  ('CSX3008', 32),
  ('CSX3007', 33);

-- Insert into course_prerequisites for major courses

INSERT INTO course_prerequisites (course_id, prerequisite_course_id)
VALUES
  -- Programming chain
  (25, 24),
  (26, 25),
  (27, 26),
  (28, 27),

  -- Database Systems
  (31, 24),
  (31, 25),

  -- Operating Systems
  (32, 24),
  (32, 25),

  -- Senior Project I
  (22, 24),
  (22, 25),

  -- Senior Project II
  (23, 22);

-- insert grade overrides for major courses

INSERT INTO curriculum_course_min_grades (curriculum_id, course_id, min_required_grade)
VALUES
  (1, 24, 'C'),
  (1, 25, 'C'),
  (1, 26, 'C'),
  (1, 27, 'C'),
  (1, 28, 'C'),
  (1, 30, 'C'),
  (1, 31, 'C'),
  (1, 32, 'C'),
  (1, 33, 'C'),
  (1, 22, 'C'),
  (1, 23, 'C');

--Insert into curriculum_course_credit_requirements for major courses

INSERT INTO curriculum_course_credit_requirements
(curriculum_id, course_id, min_earned_credits)
VALUES
  (1, 22, 72),
  (1, 23, 100);

-- Insert Major Courses into subcategory_course_codes

INSERT INTO subcategory_course_codes (subcategory_id, course_code_id)
VALUES
  (6, 21),
  (6, 22),
  (6, 23),
  (6, 24),
  (6, 25),
  (6, 26),
  (6, 27),
  (6, 28),
  (6, 29),
  (6, 30),
  (6, 31),
  (6, 32),
  (6, 33);

   

--Insert elective groups 

INSERT INTO major_elective_groups (curriculum_id, subcategory_id, name, min_courses, required_credits) 
VALUES 
 (1, 7, 'SED (Software Engineering and Development)', 5, 15), 
 (1, 7, 'IDS (Informatics and Data Science)', 5, 15), 
 (1, 7, 'Group 2 (Open Pool)', NULL, NULL); 

--Insert elective rules (5 from chosen + 6 from anywhere) 

INSERT INTO major_elective_rules (curriculum_id, min_from_chosen_group, min_from_all_groups) 
VALUES 
 (1, 5, 6); 

--Verify group_ids (we’ll need them for mapping) 

SELECT group_id, name 
FROM major_elective_groups 
WHERE curriculum_id = 1 AND subcategory_id = 7 
ORDER BY group_id; 

--You should see 3 rows. Keep those group_id numbers (SED / IDS / Group2). 

 

--Step B — Insert ALL explicit elective courses into courses 

--All are 3 credits (we ignore the (3-0-6) part). 

--Group 1A (SED) + Group 1B (IDS) + Group 2 (explicit only) 

--Run this big insert: 

INSERT INTO courses (course_name, credits) 
VALUES 
 -- Group 1A (SED) 
 ('Information System Analysis and Design', 3), 
 ('Software Testing', 3), 
 ('Web Application Development', 3), 
 ('Android Application Development', 3), 
 ('Backend Application Development', 3), 
 ('Enterprise Application Development', 3), 
 
 -- Group 1B (IDS) 
 ('Artificial Intelligence Concepts', 3), 
 ('Machine Learning', 3), 
 ('Decision Support and Recommender Systems', 3), 
 ('Natural Language Processing and Social Interactions', 3), 
 ('Data Engineering', 3), 
 ('Data Analytics', 3), 
 ('Computer Vision', 3), 
 
 -- Group 2 (Open Pool) 
 ('iOS Application Development', 3), 
 ('Data Mining', 3), 
 ('Big Data Analytics', 3), 
 ('Data Warehousing and Business Intelligence', 3), 
 ('Deep Learning', 3), 
 ('Internet of Things', 3), 
 ('Theory of Computation', 3), 
 ('Neural Networks', 3), 
 ('AR/VR Application Development', 3), 
 ('Cross-platform Application Development', 3), 
 ('Game Design and Development', 3), 
 ('Reusability and Design Patterns', 3), 
 ('UI/UX Design and Prototyping', 3), 
 ('Business Systems', 3), 
 ('Predictive Analytics', 3), 
 ('Artificial Intelligence for Business', 3), 
 ('Tech Startup', 3), 
 ('Cybersecurity', 3), 
 ('Software Configuration Management', 3), 
 ('Blockchain and Digital Currencies', 3), 
 ('Internetworking Workshop', 3); 

 

--Step C — Insert course codes for those courses (NO manual IDs) 

Insert codes using VALUES + JOIN by course_name 

INSERT INTO course_codes (course_code, course_id) 
SELECT v.code, c.course_id 
FROM (VALUES 
 -- Group 1A (SED) 
 ('ITX3004', 'Information System Analysis and Design'), 
 ('ITX4104', 'Software Testing'), 
 ('CSX4107', 'Web Application Development'), 
 ('CSX4109', 'Android Application Development'), 
 ('CSX4110', 'Backend Application Development'), 
 ('CSX4407', 'Enterprise Application Development'), 
 
 -- Group 1B (IDS) 
 ('CSX4201', 'Artificial Intelligence Concepts'), 
 ('CSX4203', 'Machine Learning'), 
 ('CSX4207', 'Decision Support and Recommender Systems'), 
 ('CSX4210', 'Natural Language Processing and Social Interactions'), 
 ('CSX4211', 'Data Engineering'), 
 ('CSX4212', 'Data Analytics'), 
 ('CSX4213', 'Computer Vision'), 
 
 -- Group 2 
 ('CSX4108', 'iOS Application Development'), 
 ('CSX4202', 'Data Mining'), 
 ('CSX4205', 'Big Data Analytics'), 
 ('CSX4206', 'Data Warehousing and Business Intelligence'), 
 ('CSX4208', 'Deep Learning'), 
 ('CSX4306', 'Internet of Things'), 
 ('CSX4501', 'Theory of Computation'), 
 ('CSX4510', 'Neural Networks'), 
 ('CSX4513', 'AR/VR Application Development'), 
 ('CSX4514', 'Cross-platform Application Development'), 
 ('CSX4515', 'Game Design and Development'), 
 ('CSX4516', 'Reusability and Design Patterns'), 
 ('ITX2004', 'UI/UX Design and Prototyping'), 
 ('ITX3003', 'Business Systems'), 
 ('ITX4212', 'Predictive Analytics'), 
 ('ITX4213', 'Artificial Intelligence for Business'), 
 ('ITX4502', 'Tech Startup'), 
 ('ITX4509', 'Cybersecurity'), 
 ('ITX4517', 'Software Configuration Management'), 
 ('ITX4518', 'Blockchain and Digital Currencies'), 
 ('ITX4519', 'Internetworking Workshop') 
) AS v(code, name) 
JOIN courses c ON c.course_name = v.name; 

--Verify some codes exist 

SELECT course_code_id, course_code 
FROM course_codes 
WHERE course_code IN ('CSX4110','CSX4203','CSX4515','ITX4509') 
ORDER BY course_code_id; 

 

--Step D — Link ALL these electives to the Major Electives subcategory (subcategory_id = 7) 

INSERT INTO subcategory_course_codes (subcategory_id, course_code_id) 
SELECT 7, cc.course_code_id 
FROM course_codes cc 
WHERE cc.course_code IN ( 
 'ITX3004','ITX4104','CSX4107','CSX4109','CSX4110','CSX4407', 
 'CSX4201','CSX4203','CSX4207','CSX4210','CSX4211','CSX4212','CSX4213', 
 'CSX4108','CSX4202','CSX4205','CSX4206','CSX4208','CSX4306','CSX4501','CSX4510', 
 'CSX4513','CSX4514','CSX4515','CSX4516','ITX2004','ITX3003','ITX4212','ITX4213', 
 'ITX4502','ITX4509','ITX4517','ITX4518','ITX4519' 
); 

 

--Step E — Add the “Selected Topic” ranges (and attach them to the correct elective group) 

--First, get the group_id values you saw earlier: 

--SED group_id = ? 

--IDS group_id = ? 

--Group 2 group_id = ? 

--Then run these inserts (replace the ?): 

-- SED Selected Topic range: CSX4180–4199 
INSERT INTO course_code_ranges (subcategory_id, prefix, number_start, number_end, group_id) 
VALUES (7, 'CSX', 4180, 4199, ?); 
 
-- IDS Selected Topic range: CSX4280–4299 
INSERT INTO course_code_ranges (subcategory_id, prefix, number_start, number_end, group_id) 
VALUES (7, 'CSX', 4280, 4299, ?); 
 
-- Open Selected Topics: CSX4600–4699 (Group 2) 
INSERT INTO course_code_ranges (subcategory_id, prefix, number_start, number_end, group_id) 
VALUES (7, 'CSX', 4600, 4699, ?); 

 

--Step F — Map explicit course codes into the correct elective groups 

--1) Get group_ids again (copy them) 

SELECT group_id, name 
FROM major_elective_groups 
WHERE curriculum_id = 1 AND subcategory_id = 7 
ORDER BY group_id; 

--Assume: 

--SED = X 

--IDS = Y 

--Group2 = Z 

--2) Insert mappings (explicit codes only) 

-- SED mappings 
INSERT INTO major_elective_group_course_codes (group_id, course_code_id) 
SELECT X, course_code_id 
FROM course_codes 
WHERE course_code IN ('ITX3004','ITX4104','CSX4107','CSX4109','CSX4110','CSX4407'); 
 
-- IDS mappings 
INSERT INTO major_elective_group_course_codes (group_id, course_code_id) 
SELECT Y, course_code_id 
FROM course_codes 
WHERE course_code IN ('CSX4201','CSX4203','CSX4207','CSX4210','CSX4211','CSX4212','CSX4213'); 
 
-- Group 2 mappings 
INSERT INTO major_elective_group_course_codes (group_id, course_code_id) 
SELECT Z, course_code_id 
FROM course_codes 
WHERE course_code IN ( 
 'CSX4108','CSX4202','CSX4205','CSX4206','CSX4208','CSX4306','CSX4501','CSX4510', 
 'CSX4513','CSX4514','CSX4515','CSX4516','ITX2004','ITX3003','ITX4212','ITX4213', 
 'ITX4502','ITX4509','ITX4517','ITX4518','ITX4519' 
); 

 -- Create advising_sessions

 CREATE TABLE advising_sessions (
  session_id BIGSERIAL PRIMARY KEY,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- student info (temporary, per upload)
  student_id_number BIGINT NOT NULL,

  -- resolved curriculum for this student
  curriculum_id INT NOT NULL
    REFERENCES curriculums(curriculum_id),

  -- optional cached total earned credits
  earned_credits INT NOT NULL DEFAULT 0,

  notes TEXT
);

CREATE INDEX idx_advising_sessions_curriculum_id
  ON advising_sessions(curriculum_id);

CREATE INDEX idx_advising_sessions_student_id_number
  ON advising_sessions(student_id_number);

--Create session_course_attempts

CREATE TABLE session_course_attempts (
  attempt_id BIGSERIAL PRIMARY KEY,

  session_id BIGINT NOT NULL
    REFERENCES advising_sessions(session_id)
    ON DELETE CASCADE,

  course_code_id INT NOT NULL
    REFERENCES course_codes(course_code_id),

  grade TEXT NOT NULL,

  credits_earned INT NOT NULL DEFAULT 0,

  term TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT uq_session_course UNIQUE (session_id, course_code_id)
);

CREATE INDEX idx_attempts_session_id
  ON session_course_attempts(session_id);

CREATE INDEX idx_attempts_course_code_id
  ON session_course_attempts(course_code_id);

--Create session_concentration_selection

CREATE TABLE session_concentration_selection (
  session_id BIGINT PRIMARY KEY
    REFERENCES advising_sessions(session_id)
    ON DELETE CASCADE,

  group_id INT NOT NULL
    REFERENCES major_elective_groups(group_id),

  selected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX idx_session_concentration_group_id
  ON session_concentration_selection(group_id);