from flask import request, jsonify, make_response, current_app as app
from . import db
from .models import Departments, Jobs, HiredEmployees
from .utils import get_quarter
import pandas as pd
from sqlalchemy import func
from io import StringIO

MODELS = {
        'hired_employees': HiredEmployees,
        'departments': Departments,
        'jobs': Jobs
        }

# Bulk insert function
def bulk_insert(table, data):
    db.session.bulk_insert_mappings(table, data)
    db.session.commit()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'table' not in request.form:
        return jsonify({'error': 'File and table are required'}), 400

    file = request.files['file']
    table = request.form['table']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        if file:
            data = pd.read_csv(file, header=None)
            
            data.columns = MODELS[table].__table__.columns.keys()

            if table == 'hired_employees':

                # Input datetime in case value is missing and convert to datetime
                data['datetime'].fillna('2000-01-01T00:00:00Z', inplace=True)
                data["datetime"] = pd.to_datetime(data["datetime"])

            bulk_insert(MODELS[table], data.to_dict(orient='records'))
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({'message': 'Data uploaded successfully'}), 201

@app.route('/upload_files', methods=['POST'])
def upload_files():
    if 'hired_employees' not in request.files:
        return jsonify({'error': 'File for hired employees is required'}), 400

    if 'departments' not in request.files:
        return jsonify({'error': 'File for departments is required'}), 400

    if 'jobs' not in request.files:
        return jsonify({'error': 'File for jobs is required'}), 400

    files = {
        'hired_employees': request.files['hired_employees'],
        'departments': request.files['departments'],
        'jobs': request.files['jobs']
        }

    for label, file_ in files.items():
        if file_.filename == '':
            return jsonify({'error': f'No selected file for {label} data'}), 400

    try:
        for label, file_ in files.items():
            data = pd.read_csv(file_, header=None)
            data.columns = MODELS[label].__table__.columns.keys()
            
            if label == "hired_employees":
                # Input datetime in case value is missing and convert to datetime
                data['datetime'].fillna('2000-01-01T00:00:00Z', inplace=True)
                data["datetime"] = pd.to_datetime(data["datetime"])

            bulk_insert(MODELS[label], data.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({'message': 'Data uploaded successfully'}), 201

@app.route('/hired_per_quarter', methods=['GET'])
def hired_per_quarter():
    employees_2021 = db.session.query(
        Departments.department, Jobs.job, HiredEmployees.datetime
    ).join(Departments, HiredEmployees.department_id == Departments.id)\
     .join(Jobs, HiredEmployees.job_id == Jobs.id)\
     .filter(func.strftime('%Y', HiredEmployees.datetime) == '2021').all()
    
    data = {}
    for department, job, datetime in employees_2021:
        quarter = get_quarter(datetime.month)
        if department not in data:
            data[department] = {}
        if job not in data[department]:
            data[department][job] = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}
        data[department][job][quarter] += 1

    # Convert to a list of dictionaries for DataFrame creation
    rows = []
    for department, jobs in data.items():
        for job, quarters in jobs.items():
            row = {'department': department, 'job': job}
            row.update(quarters)  # Add Q1, Q2, Q3, Q4 hires to row
            rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(rows)
    df.sort_values(["department", "job"], inplace=True)

    # Write DataFrame to CSV
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=hires_per_quarter_2021.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@app.route('/departments_above_mean', methods=['GET'])
def departments_above_mean():
    # Subquery for 2021 data to get mean hires value
    subquery = db.session.query(
        HiredEmployees.department_id,
        func.count(HiredEmployees.id).label('total_hires')
    ).filter(func.strftime('%Y', HiredEmployees.datetime) == '2021')\
     .group_by(HiredEmployees.department_id).subquery()
    
    mean_hires = db.session.query(func.avg(subquery.c.total_hires)).scalar()
    
    # Aggregation with all data to compare
    subquery_all = db.session.query(
        HiredEmployees.department_id,
        func.count(HiredEmployees.id).label('total_hires')
    ).group_by(HiredEmployees.department_id).subquery()

    results = db.session.query(
        Departments.id, Departments.department, subquery_all.c.total_hires
    ).join(subquery_all, Departments.id == subquery_all.c.department_id)\
     .filter(subquery_all.c.total_hires > mean_hires)\
     .order_by(subquery_all.c.total_hires.desc()).all()
    
    # Convert to a list of dictionaries for DataFrame creation
    rows = [
        {"department_id": dept_id, "department_name": dept_name, "hired": hires}
        for dept_id, dept_name, hires in results
    ]
    
    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Write DataFrame to CSV
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=departments_above_mean_2021.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
