show databases;

create database cms;
use cms;

show tables;
select * from student;
select * from courses;

CREATE TABLE Student (
  Student_id VARCHAR(50) NOT NULL,
  Name VARCHAR(255) NOT NULL,
  Total_credits INT NOT NULL,
  PRIMARY KEY (Student_id)
);

CREATE TABLE Summer_Course (
  Course_id VARCHAR(50) NOT NULL,
  Title VARCHAR(255) NOT NULL,
  Credits INT NOT NULL,
  PRIMARY KEY (Course_id)
);

CREATE TABLE Courses (
  Course_id VARCHAR(50) NOT NULL,
  Title VARCHAR(255) NOT NULL,
  Credits INT NOT NULL,
  PRIMARY KEY (Course_id)
);

CREATE TABLE Chooses (
  Student_id VARCHAR(50) NOT NULL,
  Course_id VARCHAR(50) NOT NULL,
  FOREIGN KEY (Student_id) REFERENCES Student(Student_id),
  FOREIGN KEY (Course_id) REFERENCES Summer_Course(Course_id)
);

CREATE TABLE Internship (
  Company_name VARCHAR(255) NOT NULL,
  Credits INT NOT NULL,
  Duration INT NOT NULL,
  Company_id INT NOT NULL,
  PRIMARY KEY (Company_id)
);

CREATE TABLE Capstone_Project (
  Title VARCHAR(255) NOT NULL,
  Mentor VARCHAR(255) NOT NULL,
  Credits INT NOT NULL,
  Project_id INT NOT NULL,
  PRIMARY KEY (Project_id)
);

CREATE TABLE Workson (
  Student_id VARCHAR(50) NOT NULL,
  Project_id INT NOT NULL,
  FOREIGN KEY (Student_id) REFERENCES Student(Student_id),
  FOREIGN KEY (Project_id) REFERENCES Capstone_Project(Project_id)
);

CREATE TABLE Sem_courses (
  Student_id VARCHAR(50) NOT NULL,
  Course_id VARCHAR(50) NOT NULL,
  FOREIGN KEY (Student_id) REFERENCES Student(Student_id),
  FOREIGN KEY (Course_id) REFERENCES Courses(Course_id)
);

CREATE TABLE Participates (
  Student_id VARCHAR(50) NOT NULL,
  Company_id INT NOT NULL,
  FOREIGN KEY (Student_id) REFERENCES Student(Student_id),
  FOREIGN KEY (Company_id) REFERENCES Internship(Company_id) ON DELETE CASCADE
);

ALTER TABLE students
ADD COLUMN Password VARCHAR(255) NOT NULL;


CREATE TABLE IF NOT EXISTS admins (
    `Admin ID` VARCHAR(50) NOT NULL,
    `Password` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`Admin ID`)
);

DELIMITER //

CREATE PROCEDURE UpdateSemesterCredits(IN student_id_param VARCHAR(50))
BEGIN
    DECLARE total_credits INT;

    -- Calculate the total credits based on sem_courses
    SELECT COALESCE(SUM(Courses.Credits), 0)
    INTO total_credits
    FROM Sem_courses
    JOIN Courses ON Sem_courses.Course_id = Courses.Course_id
    WHERE Sem_courses.Student_id = student_id_param;

    -- Update the total credits in the student table
    UPDATE Student
    SET Total_Credits = total_credits
    WHERE Student_id = student_id_param;
END //

DELIMITER ;


DELIMITER //

CREATE PROCEDURE UpdateTotalCredits(IN student_id_param VARCHAR(50))
BEGIN
    DECLARE total_credits INT;

    -- Calculate the total credits based on various activities
    SELECT COALESCE(SUM(credits), 0)
    INTO total_credits
    FROM (
        SELECT Credits FROM Courses WHERE Course_id IN( SELECT Course_id FROM Sem_courses WHERE Student_id = student_id_param)
        UNION ALL
        SELECT Credits FROM Internship WHERE Company_id IN( SELECT Company_id FROM Participates WHERE Student_id = student_id_param)
        UNION ALL
        SELECT Credits FROM Summer_course WHERE Course_id IN (SELECT Course_id FROM Chooses WHERE Student_id = student_id_param)
        UNION ALL
        SELECT Credits FROM Capstone_Project WHERE Project_id IN (SELECT Project_id FROM Workson WHERE Student_id = student_id_param)
        
    ) AS activities;

    -- Update the total credits in the Student table
    UPDATE Student
    SET Total_credits = total_credits
    WHERE Student_id = student_id_param;
END //

DELIMITER ;





DELIMITER //

-- Trigger for Sem_courses table
CREATE TRIGGER AfterSemCoursesInsert
AFTER INSERT ON Sem_courses
FOR EACH ROW
BEGIN
    CALL UpdateTotalCredits(NEW.Student_id);
END //


-- Trigger for Sem_courses table
CREATE TRIGGER AfterInternshipInsert
AFTER INSERT ON Participates
FOR EACH ROW
BEGIN
    CALL UpdateTotalCredits(NEW.Student_id);
END //


CREATE TRIGGER AfterSummerInsert
AFTER INSERT ON Chooses
FOR EACH ROW
BEGIN
    CALL UpdateTotalCredits(NEW.Student_id);
END //

CREATE TRIGGER Capinsert
AFTER INSERT ON Workson
FOR EACH ROW
BEGIN
    CALL UpdateTotalCredits(NEW.Student_id);
END //



DELIMITER ;

DELIMITER //



show tables;


DROP TRIGGER IF EXISTS AfterSemCoursesDelete;
-- DROP TRIGGER IF EXISTS AfterSummerInsert;
-- DROP TRIGGER IF EXISTS AfterSemCoursesUpdate;
DROP PROCEDURE IF EXISTS UpdateSemesterCredits;

SHOW TRIGGERS;





