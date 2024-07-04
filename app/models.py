from . import db

# Define models for Departments, Jobs and Hired Employees
class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(80), nullable=False)

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.String(80), nullable=False)

class HiredEmployees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    datetime = db.Column(db.DateTime, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"))
