"""
Management command to create default positions for schools
"""
from django.core.management.base import BaseCommand
from core.models import School
from employees.models import Position


class Command(BaseCommand):
    help = 'Create default positions for all schools'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school-code',
            type=str,
            help='Create positions for specific school (by code)',
        )

    def handle(self, *args, **options):
        school_code = options.get('school_code')
        
        if school_code:
            schools = School.objects.filter(code=school_code)
            if not schools.exists():
                self.stdout.write(self.style.ERROR(f'School with code {school_code} not found'))
                return
        else:
            schools = School.objects.all()
        
        # Common positions for all schools
        positions = [
            # Leadership
            ('Head Teacher', 'Leadership'),
            ('Deputy Head Teacher', 'Leadership'),
            ('Director', 'Leadership'),
            ('Principal', 'Leadership'),
            
            # Academic Staff
            ('Teacher', 'Academic'),
            ('Senior Teacher', 'Academic'),
            ('Head of Department', 'Academic'),
            ('Subject Teacher', 'Academic'),
            ('Class Teacher', 'Academic'),
            ('Head of Class', 'Academic'),
            
            # Specialized Academic
            ('Director of Studies (DOS)', 'Academic'),
            ('Registrar', 'Academic'),
            ('Examinations Officer', 'Academic'),
            ('Librarian', 'Academic'),
            ('Laboratory Technician', 'Academic'),
            ('ICT Teacher', 'Academic'),
            
            # Administrative
            ('School Administrator', 'Administrative'),
            ('Office Manager', 'Administrative'),
            ('Secretary', 'Administrative'),
            ('Receptionist', 'Administrative'),
            ('Data Entry Clerk', 'Administrative'),
            
            # Finance
            ('Bursar', 'Finance'),
            ('Accountant', 'Finance'),
            ('Accounts Assistant', 'Finance'),
            ('Cashier', 'Finance'),
            
            # Human Resources
            ('HR Manager', 'Human Resources'),
            ('HR Officer', 'Human Resources'),
            
            # Student Services
            ('Guidance Counselor', 'Student Services'),
            ('School Nurse', 'Student Services'),
            ('Matron', 'Student Services'),
            ('Patron', 'Student Services'),
            ('Social Worker', 'Student Services'),
            
            # Support Staff
            ('Security Guard', 'Support'),
            ('Cleaner', 'Support'),
            ('Cook', 'Support'),
            ('Driver', 'Support'),
            ('Gardener', 'Support'),
            ('Maintenance Worker', 'Support'),
            
            # Sports & Activities
            ('Sports Teacher', 'Sports'),
            ('Games Master', 'Sports'),
            ('Music Teacher', 'Arts'),
            ('Art Teacher', 'Arts'),
            
            # Early Childhood (for nursery/baby care)
            ('Nursery Teacher', 'Early Childhood'),
            ('Nursery Assistant', 'Early Childhood'),
            ('Baby Care Attendant', 'Early Childhood'),
            
            # Technical/Vocational
            ('Workshop Instructor', 'Technical'),
            ('Vocational Trainer', 'Technical'),
            ('Technical Assistant', 'Technical'),
        ]
        
        total_created = 0
        
        for school in schools:
            self.stdout.write(f'\nProcessing school: {school.name} ({school.code})')
            
            for title, category in positions:
                position, created = Position.objects.get_or_create(
                    school=school,
                    title=title,
                    defaults={
                        'category': category,
                        'is_active': True
                    }
                )
                if created:
                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {title} ({category})'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {total_created} positions for {schools.count()} school(s)'
            )
        )
