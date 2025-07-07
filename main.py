import os
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask_sqlalchemy import SQLAlchemy

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(
    current_dir, "database.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    courses = db.relationship("Course",
                              secondary="enrollments",
                              back_populates="students")


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    students = db.relationship("Student",
                               secondary="enrollments",
                               back_populates="courses")


class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer,
                            db.ForeignKey("student.student_id"),
                            nullable=False)
    ecourse_id = db.Column(db.Integer,
                           db.ForeignKey("course.course_id"),
                           nullable=False)


@app.route("/", methods=["GET"])
def students():
    students = db.session.query(Student).all()
    return render_template("student_list.html", students=students)


@app.route("/student/create", methods=["GET", "POST"])
def Add_Student():
    all_courses = db.session.query(Course).all()
    if request.method == "POST":
        roll_number = request.form["roll"]
        first_name = request.form["f_name"]
        last_name = request.form["l_name"]
        course_ids = request.form.getlist("courses")
        if Student.query.filter_by(roll_number=roll_number).first():
            return render_template("Exist.html")
        new_student = Student(roll_number=roll_number,
                              first_name=first_name,
                              last_name=last_name)
        db.session.add(new_student)
        db.session.flush()
        for c in course_ids:
            if c.startswith("course_"):
                try:
                    course_id = int(c.replace("course_", ""))
                    db.session.add(
                        Enrollments(estudent_id=new_student.student_id,
                                    ecourse_id=course_id))
                except ValueError:
                    continue
        db.session.commit()
        return render_template("student_list.html",
                               students=Student.query.all())
    return render_template("Add_Student.html", courses=all_courses)


@app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update(student_id):
    student = db.session.get(Student, student_id)
    all_courses = Course.query.all()

    if request.method == "POST":
        student.first_name = request.form["f_name"]
        student.last_name = request.form["l_name"]
        course_ids = request.form.getlist("courses")
        Enrollments.query.filter_by(estudent_id=student.student_id).delete()
        for cid in course_ids:
            if cid.startswith("course_"):
                try:
                    course_id = int(cid.replace("course_", ""))
                    db.session.add(
                        Enrollments(estudent_id=student.student_id,
                                    ecourse_id=course_id))
                except ValueError:
                    continue
        db.session.commit()
        return render_template("student_list.html",
                               students=Student.query.all())
    return render_template("Update.html",
                           student=student,
                           courses=all_courses,
                           roll_number=student.roll_number,
                           first_name=student.first_name,
                           last_name=student.last_name)


@app.route("/student/<int:student_id>", methods=["GET", "POST"])
def info(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    return render_template("info.html",
                           student=student,
                           courses=student.courses,
                           roll_number=student.roll_number,
                           first_name=student.first_name,
                           last_name=student.last_name)


@app.route("/student/<int:student_id>/delete", methods=["GET", "POST"])
def delete(student_id):
    student = db.session.get(Student, student_id)
    db.session.delete(student)
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    db.session.commit()
    return render_template("student_list.html", students=Student.query.all())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
