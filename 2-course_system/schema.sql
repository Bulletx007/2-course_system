-- ============================================================
--  schema.sql — ระบบคอร์สออนไลน์ (นิสิตออกแบบและเขียนเอง)
--  กติกา: ลงทะเบียน = M:N (learner × course), ความคืบหน้า = M:N (learner × lesson),
--         บทเรียน 1:M จาก course, คอร์สมี prerequisite อ้างถึง course เอง (self-reference)
-- ============================================================


-- ลบตารางเก่าทิ้งก่อน (ลบลูกก่อนพ่อแม่เพื่อไม่ให้ติด Foreign Key)
DROP TABLE IF EXISTS progress;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS lesson;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS promotion;
DROP TABLE IF EXISTS learner;



-- 2. สร้างตาราง learner
CREATE TABLE learner (
    learner_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    join_date   DATE NOT NULL,
    member_tier ENUM('normal','vip') NOT NULL DEFAULT 'normal'
);

-- 3. สร้างตาราง promotion
CREATE TABLE promotion (
    promo_id     INT AUTO_INCREMENT PRIMARY KEY,
    promo_code   VARCHAR(30) NOT NULL UNIQUE,
    discount_pct DECIMAL(5,2) NOT NULL,
    start_date   DATE NOT NULL,
    end_date     DATE NOT NULL,
    vip_only     TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT chk_promo_pct CHECK (discount_pct >= 0 AND discount_pct <= 100)
);

-- 4. สร้างตาราง course (แก้ไขโดยเอา CHECK ที่พ่วงกับ auto_increment ออก)
CREATE TABLE course (
    course_id       INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    seat_limit      INT NOT NULL DEFAULT 50,
    prerequisite_id INT NULL,
    CONSTRAINT chk_course_price CHECK (price >= 0),
    CONSTRAINT fk_course_prereq FOREIGN KEY (prerequisite_id) 
        REFERENCES course(course_id) ON DELETE RESTRICT
);

-- 5. สร้างตาราง lesson (อ้างอิง course)
CREATE TABLE lesson (
    lesson_id    INT AUTO_INCREMENT PRIMARY KEY,
    course_id    INT NOT NULL,
    title        VARCHAR(200) NOT NULL,
    seq_no       INT NOT NULL,
    duration_min INT NOT NULL,
    CONSTRAINT uq_lesson_seq UNIQUE (course_id, seq_no),
    CONSTRAINT fk_lesson_course FOREIGN KEY (course_id) 
        REFERENCES course(course_id) ON DELETE CASCADE
);

-- 6. สร้างตาราง enrollment (อ้างอิง learner, course, promotion)
CREATE TABLE enrollment (
    enroll_id   INT AUTO_INCREMENT PRIMARY KEY,
    learner_id  INT NOT NULL,
    course_id   INT NOT NULL,
    enroll_date DATE NOT NULL,
    status      ENUM('active','completed','dropped') NOT NULL DEFAULT 'active',
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    promo_id    INT NULL,
    CONSTRAINT uq_enroll_pair UNIQUE (learner_id, course_id),
    CONSTRAINT fk_enroll_learner FOREIGN KEY (learner_id) 
        REFERENCES learner(learner_id) ON DELETE CASCADE,
    CONSTRAINT fk_enroll_course FOREIGN KEY (course_id) 
        REFERENCES course(course_id) ON DELETE RESTRICT,
    CONSTRAINT fk_enroll_promo FOREIGN KEY (promo_id) 
        REFERENCES promotion(promo_id) ON DELETE SET NULL
);

-- 7. สร้างตาราง progress (อ้างอิง learner และ lesson)
CREATE TABLE progress (
    learner_id     INT NOT NULL,
    lesson_id      INT NOT NULL,
    watched        TINYINT(1) NOT NULL DEFAULT 0,
    completed_date DATE NULL,
    PRIMARY KEY (learner_id, lesson_id),
    CONSTRAINT fk_progress_learner FOREIGN KEY (learner_id) 
        REFERENCES learner(learner_id) ON DELETE CASCADE,
    CONSTRAINT fk_progress_lesson FOREIGN KEY (lesson_id) 
        REFERENCES lesson(lesson_id) ON DELETE CASCADE
);

-- TODO: INSERT ข้อมูลตัวอย่างทุกตาราง

-- 1. ผู้เรียน (3 คน)
INSERT INTO learner (name, email, join_date, member_tier) VALUES
('Alice Smith',   'alice@example.com',   '2025-01-10', 'vip'),
('Bob Johnson',   'bob@example.com',     '2025-01-15', 'normal'),
('Charlie Brown', 'charlie@example.com', '2025-02-01', 'normal');

-- 2. โปรโมชัน (2 โค้ดส่วนลด)
INSERT INTO promotion (promo_code, discount_pct, start_date, end_date, vip_only) VALUES
('NEW2026', 10.00, '2026-01-01', '2026-12-31', 0),
('VIP50',   50.00, '2025-01-01', '2026-12-31', 1);

-- 3. คอร์สเรียน (3 คอร์ส: มีวิชาเริ่มต้นและวิชาต่อเนื่อง)
INSERT INTO course (title, category, price, seat_limit, prerequisite_id) VALUES
('Python Basics',     'Programming', 1500.00, 50, NULL), -- id 1 (เรียนได้เลย ไม่มีเงื่อนไข)
('Advanced Python',   'Programming', 2500.00, 30, 1),    -- id 2 (ต้องผ่านคอร์ส id 1 ก่อน)
('Database SQL',      'Database',    2000.00, 40, NULL); -- id 3 (เรียนได้เลย ไม่มีเงื่อนไข)

-- 4. บทเรียนย่อย (ผูกกับแต่ละคอร์ส)
INSERT INTO lesson (course_id, title, seq_no, duration_min) VALUES
(1, 'Installation & Setup', 1, 30),
(1, 'Variables & Types',    2, 45),
(2, 'Deep Dive into OOP',   1, 60),
(3, 'SQL SELECT Statement', 1, 40);

-- 5. การลงทะเบียน (คละสถานะ: สำเร็จ, กำลังเรียน, ถอนวิชา)
INSERT INTO enrollment (learner_id, course_id, enroll_date, status, paid_amount) VALUES
(1, 1, '2025-01-12', 'completed', 1500.00), -- อลิซ จบคอร์ส 1 แล้ว
(1, 2, '2025-02-01', 'active',    2500.00), -- อลิซ กำลังเรียนคอร์ส 2
(2, 1, '2025-01-20', 'completed', 1500.00), -- บ๊อบ จบคอร์ส 1 แล้ว
(3, 3, '2025-02-10', 'dropped',   2000.00); -- ชาลี ถอนคอร์ส SQL

-- 6. ความคืบหน้าการเรียน (เช็กสถานะการดูบทเรียน)
INSERT INTO progress (learner_id, lesson_id, watched, completed_date) VALUES
(1, 1, 1, '2025-01-13'),
(1, 2, 1, '2025-01-15'),
(2, 1, 1, '2025-01-22'),
(3, 4, 0, NULL);
