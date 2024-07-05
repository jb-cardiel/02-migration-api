# Migration API Data Engineering Challenge

## Overview
This API allows you to migrate data for employees, deparments and jobs from CSV files into a new database and provides endpoints for querying the data.

## Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/jb-cardiel/02-migration-api.git
    cd 02-migration_api
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application**:
    ```sh
    flask run
    ```

## Endpoints

### Upload CSV
- **URL**: `/upload`
- **Method**: `POST`
- **Description**: Upload a CSV file to a specified table.
- **Parameters**:
  - `file`: The CSV file to upload.
  - `table`: The table to upload the data to (`departments`, `jobs`, `hired_employees`).

### Upload all files
- **URL**: `/upload_files`
- **Method**: `POST`
- **Description**: Upload employees, departments and jobs files to tables at once.
- **Parameters**:
  - `hired_employees`: The CSV file with hired employees data to upload.
  - `departments`: The CSV file with department data to upload
  - `jobs`: The CSV file with jobs data to upload

### Hired Per Quarter
- **URL**: `/hired_per_quarter`
- **Method**: `GET`
- **Description**: Get the number of employees hired per quarter in 2021.

### Departments Above Mean
- **URL**: `/departments_above_mean`
- **Method**: `GET`
- **Description**: Get departments that hired more employees than the mean in 2021.

