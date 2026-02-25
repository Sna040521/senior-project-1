CREATE TYPE grade_enum AS ENUM (
  'A','A-','B+','B','B-','C+','C','C-','D','F','W','TR','IP','S'
);

CREATE TABLE majors (
  major_id SERIAL PRIMARY KEY,
  major_code TEXT NOT NULL UNIQUE,
  major_name TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE main_categories (
  main_category_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE courses (
  course_id SERIAL PRIMARY KEY,
  course_name TEXT NOT NULL,
  credits INTEGER NOT NULL CHECK (credits >= 0),

  is_english BOOLEAN NOT NULL DEFAULT FALSE,
  is_ethics_seminar BOOLEAN NOT NULL DEFAULT FALSE,
  is_sequential BOOLEAN NOT NULL DEFAULT FALSE,

  is_active BOOLEAN NOT NULL DEFAULT TRUE,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE curriculums (
  curriculum_id SERIAL PRIMARY KEY,
  curriculum_code TEXT NOT NULL UNIQUE,
  major_id INTEGER NOT NULL REFERENCES majors(major_id) ON DELETE RESTRICT,
  total_required_credits INTEGER CHECK (total_required_credits >= 0),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE course_codes (
  course_code_id SERIAL PRIMARY KEY,
  course_code TEXT NOT NULL UNIQUE,
  course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE RESTRICT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE curriculum_id_ranges (
  range_id SERIAL PRIMARY KEY,
  curriculum_id INTEGER NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  id_start BIGINT NOT NULL,
  id_end BIGINT NOT NULL,
  CHECK (id_start <= id_end)
);

CREATE TABLE course_prerequisites (
  course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
  prerequisite_course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE RESTRICT,
  PRIMARY KEY (course_id, prerequisite_course_id),
  CHECK (course_id <> prerequisite_course_id)
);

CREATE TABLE curriculum_main_categories (
  curriculum_id INTEGER NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  main_category_id INTEGER NOT NULL REFERENCES main_categories(main_category_id) ON DELETE RESTRICT,
  required_credits INTEGER CHECK (required_credits >= 0),
  PRIMARY KEY (curriculum_id, main_category_id)
);

CREATE TABLE curriculum_subcategories (
  subcategory_id SERIAL PRIMARY KEY,
  curriculum_id INTEGER NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  main_category_id INTEGER NOT NULL REFERENCES main_categories(main_category_id) ON DELETE RESTRICT,
  name TEXT NOT NULL,
  required_credits INTEGER CHECK (required_credits >= 0),
  display_order INTEGER,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (curriculum_id, main_category_id, name)
);

CREATE TABLE subcategory_course_codes (
  subcategory_id INTEGER NOT NULL REFERENCES curriculum_subcategories(subcategory_id) ON DELETE CASCADE,
  course_code_id INTEGER NOT NULL REFERENCES course_codes(course_code_id) ON DELETE RESTRICT,
  PRIMARY KEY (subcategory_id, course_code_id)
);

CREATE TABLE course_code_ranges (
  range_id SERIAL PRIMARY KEY,
  subcategory_id INTEGER NOT NULL REFERENCES curriculum_subcategories(subcategory_id) ON DELETE CASCADE,
  prefix TEXT NOT NULL,
  number_start INTEGER NOT NULL,
  number_end INTEGER NOT NULL,
  CHECK (number_start <= number_end),
  CHECK (number_start >= 0),
  CHECK (number_end >= 0)
);

CREATE TABLE major_elective_groups (
  group_id SERIAL PRIMARY KEY,
  curriculum_id INTEGER NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  subcategory_id INTEGER NOT NULL REFERENCES curriculum_subcategories(subcategory_id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  min_courses INTEGER CHECK (min_courses >= 0),
  required_credits INTEGER CHECK (required_credits >= 0),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (curriculum_id, subcategory_id, name)
);

CREATE TABLE major_elective_group_course_codes (
  group_id INTEGER NOT NULL REFERENCES major_elective_groups(group_id) ON DELETE CASCADE,
  course_code_id INTEGER NOT NULL REFERENCES course_codes(course_code_id) ON DELETE RESTRICT,
  PRIMARY KEY (group_id, course_code_id)
);

CREATE TABLE major_elective_rules (
  curriculum_id INTEGER PRIMARY KEY REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  min_from_chosen_group INTEGER NOT NULL DEFAULT 0 CHECK (min_from_chosen_group >= 0),
  min_from_all_groups INTEGER NOT NULL DEFAULT 0 CHECK (min_from_all_groups >= 0)
);

CREATE TABLE curriculum_course_min_grades (
  curriculum_id INTEGER NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
  min_required_grade grade_enum NOT NULL,
  PRIMARY KEY (curriculum_id, course_id)
);

CREATE TABLE curriculum_course_credit_requirements (
  curriculum_id INTEGER NOT NULL REFERENCES curriculums(curriculum_id) ON DELETE CASCADE,
  course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
  min_earned_credits INTEGER NOT NULL CHECK (min_earned_credits >= 0),
  PRIMARY KEY (curriculum_id, course_id)
);


