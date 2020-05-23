import atexit
import os
import sqlite3
import sys


# Data Transfer Objects:


class Student:
    def __init__(self, grade, count):
        self.grade = grade
        self.count = count


class Course:
    def __init__(self, id, course_name, student, number_of_students,class_id, course_length):
        self.id = id
        self.course_name = course_name
        self.student = student
        self.number_of_students = number_of_students
        self.class_id = class_id
        self.course_length = course_length


class Classroom:
    def __init__(self, id, location):
        self.id = id
        self.location = location
        self.current_course_id = 0
        self.current_course_time_left = 0


# Data Access Objects:

class _Students:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, student):
        self._conn.execute("""
                INSERT INTO students (grade, count) VALUES (?, ?) 
           """, [student.grade, student.count])

    def print_all(self):
        c = self._conn.cursor()
        table = c.execute("""
                    SELECT * FROM students
                """, ).fetchall()
        print_table(table)


class _Courses:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, course):
        self._conn.execute("""
             INSERT INTO courses (id, course_name, student, number_of_students,class_id, course_length) VALUES (?, ?, ?, ?, ?,?) 
           """, [course.id, course.course_name, course.student, course.number_of_students, course.class_id, course.course_length])

    def print_all(self):
        c = self._conn.cursor()
        table = c.execute("""
                    SELECT * FROM courses
                """, ).fetchall()
        print_table(table)


class _Classrooms:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, classroom):
        self._conn.execute("""
           INSERT INTO classrooms(id, location, current_course_id, current_course_time_left) VALUES(?, ?, ?, ?)
       """, [classroom.id, classroom.location, classroom.current_course_id, classroom.current_course_time_left])

    def print_all(self):
        c = self._conn.cursor()
        table = c.execute("""
                    SELECT * FROM classrooms
                """, ).fetchall()
        print_table(table)


# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('schedule.db')
        self.students = _Students(self._conn)
        self.courses = _Courses(self._conn)
        self.classrooms = _Classrooms(self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE courses (
              id      INTEGER         PRIMARY KEY,
              course_name    TEXT        NOT NULL,
              student     TEXT    NOT NULL, 
              number_of_students  INTEGER NOT NULL,
              class_id    INTEGER     REFERENCES    classrooms(id),
              course_length   INTEGER     NOT NULL
        );

        CREATE TABLE students (
              grade     TEXT     PRIMARY KEY,
              count     INTEGER    NOT NULL
        );

        CREATE TABLE classrooms (
              id      INTEGER     PRIMARY KEY,
              location  TEXT     NOT NULL,
              current_course_id           INTEGER     NOT NULL,
              current_course_time_left    INTEGER    NOT NULL

        );
    """)


def print_table(list_of_tuples):
    for item in list_of_tuples:
        print(item)


def main(args):
    if not os.path.isfile('schedule.db'):
        file = open(args[1])
        lines = file.readlines()
        file.close()

        # the repository singleton
        repo = _Repository()
        atexit.register(repo._close)
        repo.create_tables()
        for line in lines:

            splitedline = []
            changed_line = line.replace('\n', '')  # replaces every '\n' with a space
            changed_line = changed_line.replace('\r', '')
            changed_line = changed_line.replace('\t', '')
            splitedline1 = changed_line.split(',')  # returns a list of the string line without spaces
            for s in splitedline1:
                splitedline.append(s.strip())

            if splitedline[0] == 'S':
                s = Student(splitedline[1], splitedline[2])
                repo.students.insert(s)
            elif splitedline[0] == 'C':
                c = Course(splitedline[1], splitedline[2], splitedline[3], splitedline[4], splitedline[5],
                           splitedline[6])
                repo.courses.insert(c)
            elif splitedline[0] == 'R':
                r = Classroom(splitedline[1], splitedline[2])
                repo.classrooms.insert(r)

        print("courses")
        repo.courses.print_all()
        print("classrooms")
        repo.classrooms.print_all()
        print("students")
        repo.students.print_all()


if __name__ == '__main__':
    main(sys.argv)
