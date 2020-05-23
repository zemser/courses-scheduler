# courses-scheduler-
simulator of assigning classrooms to courses. written in python and sql.

I built a sqlite3 database that holds the courses, students, and classrooms
tables.
The database filename will be classes.db.
we 2 Python modules: create_db.py and schedule.py.

The database classes.db has three table:

• courses: This table holds information of the courses. The columns are:

id INTEGER PRIMARY KEY

course_name TEXT NOT NULL

student TEXT NOT NULL

number_of_students INTEGER NOT NULL

class_id INTEGER REFERENCES classrooms(id)

course_length INTEGER NOT NULL


• students: This table holds the number of students per grade. The columns
are:

grade TEXT PRIMARY KEY

count INTEGER NOT NULL


• classrooms: This table holds the location and the status of each class room.
The columns are:

id INTEGER PRIMARY KEY

location TEXT NOT NULL

current_course_id INTEGER NOT NULL

current_course_time_left INTEGER NOT NULL


schedule.py

This module is in charge of orchestrating the schedule of the courses.
It will run in a loop until one of the following conditions hold:

1. The database file schedule.db does not exist.

2. All courses are done (The courses table is empty)

At each iteration do the following per classroom 

1. If a classroom is free assign next course to it if exists and

a. print: ([iteration No.]) [classroom location]: [course name] is scheduled to start

b. Update the values of “current_course_id” and “current_course_time_left in the
classrooms table.

2. If a classroom is occupied:

a. Print ([iteration No.]) [classroom location]: occupied by [course name]

b. Decrease by 1 the current_course_time_left in the classrooms table.

3. If a course just finished (current_course_time_left=0)

a. print ([iteration No.]) [classroom location]: [course name] is done

b. Remove the course from the DB

c. Go to 1 to assign a new course to the classroom immediately if exists (same
iteration number).
