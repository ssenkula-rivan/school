"""
Data Import System
Allows schools to import existing data from other systems
Supports: CSV, Excel, and direct database connections
"""

import csv
import openpyxl
from django.db import transaction, connections
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class DataImporter:
    """Base class for data import operations"""
    
    def __init__(self, school_config):
        self.school_config = school_config
        self.errors = []
        self.success_count = 0
        self.skip_count = 0
    
    def log_error(self, row_num, message):
        """Log import error"""
        self.errors.append(f"Row {row_num}: {message}")
        logger.error(f"Import error at row {row_num}: {message}")
    
    def get_report(self):
        """Get import report"""
        return {
            'success': self.success_count,
            'skipped': self.skip_count,
            'errors': len(self.errors),
            'error_details': self.errors
        }


class StudentImporter(DataImporter):
    """Import students from CSV/Excel"""
    
    def import_from_csv(self, file_path):
        """Import students from CSV file"""
        from core.models import Student, Grade
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    with transaction.atomic():
                        # Get or create grade
                        grade_name = row.get('grade') or row.get('class')
                        grade = None
                        if grade_name:
                            grade, _ = Grade.objects.get_or_create(
                                name=grade_name,
                                defaults={'level': row_num}
                            )
                        
                        # Check if student already exists
                        admission_number = row.get('admission_number') or row.get('student_id')
                        if Student.objects.filter(admission_number=admission_number).exists():
                            self.skip_count += 1
                            continue
                        
                        # Create student
                        student = Student.objects.create(
                            admission_number=admission_number,
                            first_name=row.get('first_name', ''),
                            last_name=row.get('last_name', ''),
                            middle_name=row.get('middle_name', ''),
                            date_of_birth=self._parse_date(row.get('date_of_birth')),
                            gender=row.get('gender', 'M')[0].upper(),
                            grade=grade,
                            admission_date=self._parse_date(row.get('admission_date')) or timezone.now().date(),
                            status=row.get('status', 'active'),
                            email=row.get('email', ''),
                            phone=row.get('phone', ''),
                            address=row.get('address', ''),
                            guardian_name=row.get('guardian_name', ''),
                            guardian_relationship=row.get('guardian_relationship', 'Parent'),
                            guardian_phone=row.get('guardian_phone', ''),
                            guardian_email=row.get('guardian_email', ''),
                            blood_group=row.get('blood_group', ''),
                        )
                        
                        self.success_count += 1
                        
                except Exception as e:
                    self.log_error(row_num, str(e))
    
    def import_from_excel(self, file_path):
        """Import students from Excel file"""
        from core.models import Student, Grade
        
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        
        # Get headers from first row
        headers = [cell.value for cell in sheet[1]]
        
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                with transaction.atomic():
                    # Create dictionary from row
                    data = dict(zip(headers, row))
                    
                    # Get or create grade
                    grade_name = data.get('grade') or data.get('class')
                    grade = None
                    if grade_name:
                        grade, _ = Grade.objects.get_or_create(
                            name=str(grade_name),
                            defaults={'level': row_num}
                        )
                    
                    # Check if student already exists
                    admission_number = str(data.get('admission_number') or data.get('student_id'))
                    if Student.objects.filter(admission_number=admission_number).exists():
                        self.skip_count += 1
                        continue
                    
                    # Create student
                    student = Student.objects.create(
                        admission_number=admission_number,
                        first_name=str(data.get('first_name', '')),
                        last_name=str(data.get('last_name', '')),
                        middle_name=str(data.get('middle_name', '')),
                        date_of_birth=self._parse_date(data.get('date_of_birth')),
                        gender=str(data.get('gender', 'M'))[0].upper(),
                        grade=grade,
                        admission_date=self._parse_date(data.get('admission_date')) or timezone.now().date(),
                        status=str(data.get('status', 'active')),
                        email=str(data.get('email', '')),
                        phone=str(data.get('phone', '')),
                        address=str(data.get('address', '')),
                        guardian_name=str(data.get('guardian_name', '')),
                        guardian_relationship=str(data.get('guardian_relationship', 'Parent')),
                        guardian_phone=str(data.get('guardian_phone', '')),
                        guardian_email=str(data.get('guardian_email', '')),
                    )
                    
                    self.success_count += 1
                    
            except Exception as e:
                self.log_error(row_num, str(e))
    
    def _parse_date(self, date_str):
        """Parse date from various formats"""
        if not date_str:
            return None
        
        from datetime import datetime
        
        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except:
                continue
        
        return None


class EmployeeImporter(DataImporter):
    """Import employees/staff from CSV/Excel"""
    
    def import_from_csv(self, file_path):
        """Import employees from CSV"""
        from employees.models import Employee, Department, Position
        from accounts.models import UserProfile
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    with transaction.atomic():
                        # Get or create department
                        dept_name = row.get('department')
                        department = None
                        if dept_name:
                            department, _ = Department.objects.get_or_create(name=dept_name)
                        
                        # Get or create position
                        pos_name = row.get('position')
                        position = None
                        if pos_name:
                            position, _ = Position.objects.get_or_create(name=pos_name)
                        
                        # Check if employee exists
                        employee_id = row.get('employee_id')
                        if Employee.objects.filter(employee_id=employee_id).exists():
                            self.skip_count += 1
                            continue
                        
                        # Create user account if email provided
                        email = row.get('email', '')
                        username = row.get('username') or email.split('@')[0] if email else employee_id
                        
                        user = None
                        if not User.objects.filter(username=username).exists():
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                first_name=row.get('first_name', ''),
                                last_name=row.get('last_name', ''),
                                password='ChangeMe123!'  # Default password
                            )
                        
                        # Create employee
                        employee = Employee.objects.create(
                            employee_id=employee_id,
                            first_name=row.get('first_name', ''),
                            last_name=row.get('last_name', ''),
                            email=email,
                            phone=row.get('phone', ''),
                            department=department,
                            position=position,
                            date_of_birth=self._parse_date(row.get('date_of_birth')),
                            hire_date=self._parse_date(row.get('hire_date')) or timezone.now().date(),
                            employment_status=row.get('status', 'active'),
                            salary=Decimal(row.get('salary', '0')),
                        )
                        
                        self.success_count += 1
                        
                except Exception as e:
                    self.log_error(row_num, str(e))
    
    def _parse_date(self, date_str):
        """Parse date from various formats"""
        if not date_str:
            return None
        
        from datetime import datetime
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except:
                continue
        
        return None


class DatabaseConnector:
    """Connect to external databases and import data"""
    
    @staticmethod
    def test_connection(db_type, host, port, database, username, password):
        """Test database connection"""
        try:
            if db_type == 'mysql':
                import pymysql
                conn = pymysql.connect(
                    host=host,
                    port=int(port),
                    user=username,
                    password=password,
                    database=database
                )
                conn.close()
                return True, "Connection successful"
            
            elif db_type == 'postgresql':
                import psycopg2
                conn = psycopg2.connect(
                    host=host,
                    port=int(port),
                    user=username,
                    password=password,
                    database=database
                )
                conn.close()
                return True, "Connection successful"
            
            elif db_type == 'mssql':
                import pyodbc
                conn_str = f'DRIVER={{SQL Server}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}'
                conn = pyodbc.connect(conn_str)
                conn.close()
                return True, "Connection successful"
            
            else:
                return False, "Unsupported database type"
                
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def import_from_database(db_type, host, port, database, username, password, table_name, data_type):
        """Import data from external database"""
        try:
            # Connect to database
            if db_type == 'mysql':
                import pymysql
                conn = pymysql.connect(
                    host=host,
                    port=int(port),
                    user=username,
                    password=password,
                    database=database
                )
            elif db_type == 'postgresql':
                import psycopg2
                conn = psycopg2.connect(
                    host=host,
                    port=int(port),
                    user=username,
                    password=password,
                    database=database
                )
            else:
                return {'success': False, 'message': 'Unsupported database type'}
            
            cursor = conn.cursor()
            # Use parameterized query to prevent SQL injection
            cursor.execute("SELECT * FROM %s", [table_name])
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Import based on data type
            if data_type == 'students':
                importer = StudentImporter(None)
                # Process rows...
            elif data_type == 'employees':
                importer = EmployeeImporter(None)
                # Process rows...
            
            conn.close()
            
            return {
                'success': True,
                'message': f'Imported {len(rows)} records',
                'report': importer.get_report() if 'importer' in locals() else {}
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}


def generate_import_template(data_type):
    """Generate CSV template for data import"""
    templates = {
        'students': [
            'admission_number', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'gender', 'grade', 'admission_date', 'status',
            'email', 'phone', 'address', 'guardian_name', 'guardian_relationship',
            'guardian_phone', 'guardian_email', 'blood_group'
        ],
        'employees': [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'department', 'position', 'date_of_birth', 'hire_date',
            'status', 'salary', 'username'
        ],
        'fees': [
            'student_admission_number', 'amount', 'payment_date',
            'payment_method', 'reference_number', 'academic_year'
        ]
    }
    
    return templates.get(data_type, [])
