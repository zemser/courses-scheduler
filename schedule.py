import atexit
import os
import sqlite3


def main():
    if os.path.isfile('schedule.db'):
        repo = _Repository()
        atexit.register(repo._close)
        if not repo.courses.is_courses_table_not_empty():
            print('courses')
            repo.courses.print_all()
            print('classrooms')
            repo.classrooms.print_all()
            print('students')
            repo.students.print_all()
            return
    iteration_count = 0
    while os.path.isfile('schedule.db'):
        if not repo.courses.is_courses_table_not_empty():
            return
        repo.classrooms.decrease_time_left()  # decrease time left in all occupied classrooms
        repo.print_occupied_classes(iteration_count)  # print all the occupied classroooms
        classes = repo.classrooms.find_vacant_classes()  # get a list of al the vacant classrooms
        for classroom in classes:
            if classroom[2] != 0:
                course_name = repo.courses.get_course_name_by_id(classroom[2])
                course = repo.courses.find(classroom[2]) # find course by id
                if course is not None:
                   print("({}) {}: {} is done".format(iteration_count, classroom[1], course_name[0]))
                   repo.courses.deletecourse(course[0])  # delete the course from the courses table
                   repo.classrooms.remove_course_from_classroom(classroom[0])
            waiting_course = repo.courses.get_waiting_course_by_class_id(classroom[0])
            if waiting_course is not None:  # check if there is a waiting course and if there is enough students
                repo.classrooms.start_course(waiting_course[0], waiting_course[5], classroom[0])   # initiate the course in the classroom
                repo.students.decrease_number_of_students(waiting_course[3], waiting_course[2])  # decrease number of students in the students table
                print("({}) {}: {} is schedule to start".format(iteration_count, classroom[1], waiting_course[1]))

        print('courses')
        repo.courses.print_all()
        print('classrooms')
        repo.classrooms.print_all()
        print('students')
        repo.students.print_all()
        iteration_count = iteration_count+1


class Student:
    def __init__(self, grade, count):
        self.grade = grade
        self.count = count


class Course:
    def __init__(self, id, course_name, student, number_of_students, class_id, course_length):
        self.id = id
        self.course_name = course_name
        self.student = student
        self.number_of_students = number_of_students
        self.class_id = class_id
        self.course_length = course_length


class Classroom:
    def __init__(self, id, location, current_course_id, current_course_time_left):
        self.id = id
        self.location = location
        self.current_course_id = current_course_id
        self.current_course_time_left = current_course_time_left

# Data Access Objects:


class _Students:
    def __init__(self, conn):
        self._conn = conn

    def decrease_number_of_students(self, num_students, student_grade):
        c = self._conn.cursor()
        c.execute("""
            UPDATE students
            SET count=count - ?
            WHERE grade= ?
        """, (num_students, student_grade))

    def print_all(self):
        c = self._conn.cursor()
        table = c.execute("""
                    SELECT *  FROM students
                """, ).fetchall()
        print_table(table)


class _Courses:
    def __init__(self, conn):
        self._conn = conn

    def find(self, course_id):
        c = self._conn.cursor()
        course=c.execute("""
             SELECT id, course_name, student, class_id, course_length  FROM courses WHERE id = ?
        """, (course_id, ))
        return course.fetchone()

    def get_waiting_course_by_class_id(self, classid ):
        c = self._conn.cursor()
        returned_course = c.execute("""
                SELECT * FROM courses WHERE class_id = (?)
        """, [classid]).fetchone()
        return returned_course

    def get_course_name_by_id(self, courseid):
        c = self._conn.cursor()
        course = c.execute("""
            SELECT course_name FROM courses WHERE id = ?
        """, (courseid, ))
        return course.fetchone()

    def deletecourse(self, courseid):
        c = self._conn.cursor()
        c.execute("""
                DELETE FROM courses WHERE id=(?)
        """, (courseid, ))
        self._conn.commit()

    def is_courses_table_not_empty(self):
        c = self._conn.cursor()
        table = c.execute("""
            SELECT * FROM courses
        """, ).fetchall()
        if table is not None:
            if len(table) == 0:
                return False
        return True

    def print_all(self):
        c = self._conn.cursor()
        table = c.execute("""
                    SELECT * FROM courses
                """, ).fetchall()
        print_table(table)


class _Classrooms:
    def __init__(self, conn):
        self._conn = conn

    def find(self, classroom_id):
        c = self._conn.cursor()
        c.execute("""
             SELECT id, location, current_course_id, current_course_time_left  FROM classrooms WHERE id = ?
        """, [classroom_id])

        return Classroom(*c.fetchone())

    def decrease_time_left(self):
        c = self._conn.cursor()
        c.execute("""
            UPDATE classrooms 
            SET current_course_time_left=current_course_time_left-1
            WHERE current_course_time_left>0
        """)

    def find_vacant_classes(self):
        c = self._conn.cursor()
        #c.execute("SELECT * FROM classrooms WHERE current_course_time_left=(?)", (0,))
        classrooms=c.execute("""
            SELECT * FROM classrooms 
            WHERE current_course_time_left = ?
        """, [0], ).fetchall()
        return classrooms

    def print_all(self):
        c = self._conn.cursor()
        table = c.execute("""
                    SELECT * FROM classrooms
                """, ).fetchall()
        print_table(table)

    def start_course(self, course_id, course_length, classid):
        c = self._conn.cursor()
        c.execute("""
            UPDATE classrooms 
            SET current_course_id = ? , current_course_time_left = ?
            WHERE id = ?
        """, (course_id, course_length, classid))

    def remove_course_from_classroom(self, classid):
        c = self._conn.cursor()
        c.execute("""
            UPDATE classrooms
            SET current_course_id = ?
            WHERE id = ?
        """, (0, classid,))


def print_table(list_of_tuples):
    for item in list_of_tuples:
        print(item)


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

    def print_occupied_classes(self, iteration_number):
        c = self._conn.cursor()
        occupied_classes=c.execute("""
            SELECT classrooms.location, courses.course_name
            FROM classrooms
            JOIN courses ON classrooms.current_course_id = courses.id AND classrooms.current_course_time_left>0
        """).fetchall()
        for occupied_class in occupied_classes:
            print("({}) {}: occupied by {}".format(iteration_number, occupied_class[0], occupied_class[1]))


if __name__ == '__main__':
    main()




