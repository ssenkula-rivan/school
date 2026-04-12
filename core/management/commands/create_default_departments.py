"""
Management command to create default departments for schools
"""
from django.core.management.base import BaseCommand
from core.models import School, Department


class Command(BaseCommand):
    help = 'Create default departments for all schools based on their type'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school-code',
            type=str,
            help='Create departments for specific school (by code)',
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
        
        # Common departments for all schools
        common_departments = [
            'Administration',
            'Finance & Accounts',
            'Human Resources',
            'ICT & Technology',
            'Security',
            'Maintenance',
        ]
        
        # School-specific departments
        school_specific = {
            'nursery': [
                'Early Childhood Education',
                'Nursery Care',
                'Play & Recreation',
            ],
            'primary': [
                'Lower Primary (P1-P3)',
                'Upper Primary (P4-P7)',
                'Sports & Games',
                'Library',
                'Guidance & Counseling',
            ],
            'secondary': [
                'Sciences Department',
                'Arts & Humanities',
                'Mathematics Department',
                'Languages Department',
                'Sports & Physical Education',
                'Library',
                'Guidance & Counseling',
                'Examinations Office',
            ],
            'college': [
                'Academic Affairs',
                'Student Affairs',
                'Examinations & Records',
                'Library & Research',
                'Sports & Recreation',
            ],
            'university': [
                'Academic Affairs',
                'Student Affairs',
                'Examinations & Records',
                'Research & Innovation',
                'Library Services',
                'Sports & Recreation',
                'Career Services',
            ],
            'combined': [
                'Nursery Section',
                'Primary Section',
                'Secondary Section',
                'Sciences Department',
                'Arts & Humanities',
                'Sports & Physical Education',
                'Library',
                'Guidance & Counseling',
                'Examinations Office',
            ],
        }
        
        total_created = 0
        
        for school in schools:
            self.stdout.write(f'\nProcessing school: {school.name} ({school.code})')
            
            # Create common departments
            for dept_name in common_departments:
                dept, created = Department.objects.get_or_create(
                    school=school,
                    name=dept_name,
                    defaults={'is_active': True}
                )
                if created:
                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f'   Created: {dept_name}'))
            
            # Create school-specific departments
            specific_depts = school_specific.get(school.school_type, [])
            for dept_name in specific_depts:
                dept, created = Department.objects.get_or_create(
                    school=school,
                    name=dept_name,
                    defaults={'is_active': True}
                )
                if created:
                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f'   Created: {dept_name}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n Successfully created {total_created} departments for {schools.count()} school(s)'
            )
        )
