# Generated migration for SchoolConfiguration school_type field length increase

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_fix_userprofile_school_relationship'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolconfiguration',
            name='school_type',
            field=models.CharField(choices=[
                ('daycare', 'Daycare/Childcare Center'),
                ('preschool', 'Preschool/Pre-K'),
                ('kindergarten', 'Kindergarten'),
                ('primary', 'Primary School (Grades 1-6)'),
                ('elementary', 'Elementary School (K-5)'),
                ('junior_primary', 'Junior Primary School'),
                ('middle_school', 'Middle School (Grades 6-8)'),
                ('junior_high', 'Junior High School (Grades 7-9)'),
                ('high_school', 'High School (Grades 9-12)'),
                ('senior_high', 'Senior High School (Grades 11-12)'),
                ('secondary', 'Secondary School (O-Level & A-Level)'),
                ('college', 'College'),
                ('university', 'University'),
                ('technical_college', 'Technical College'),
                ('vocational_college', 'Vocational College'),
                ('community_college', 'Community College'),
                ('polytechnic', 'Polytechnic Institute'),
                ('special_education', 'Special Education School'),
                ('stem_school', 'STEM School'),
                ('arts_school', 'Arts School'),
                ('music_school', 'Music Conservatory'),
                ('sports_academy', 'Sports Academy'),
                ('language_school', 'Language School'),
                ('international_school', 'International School'),
                ('montessori', 'Montessori School'),
                ('waldorf', 'Waldorf School'),
                ('catholic_school', 'Catholic School'),
                ('christian_school', 'Christian School'),
                ('islamic_school', 'Islamic School'),
                ('jewish_school', 'Jewish School'),
                ('buddhist_school', 'Buddhist School'),
                ('hindu_school', 'Hindu School'),
                ('charter_school', 'Charter School'),
                ('magnet_school', 'Magnet School'),
                ('homeschool_coop', 'Homeschool Cooperative'),
                ('online_school', 'Online/Virtual School'),
                ('microschool', 'Microschool'),
                ('adult_education', 'Adult Education Center'),
                ('continuing_ed', 'Continuing Education'),
                ('corporate_training', 'Corporate Training Center'),
                ('professional_development', 'Professional Development Institute'),
                ('military_academy', 'Military Academy'),
                ('boarding_school', 'Boarding School'),
                ('hospital_school', 'Hospital School'),
                ('prison_education', 'Correctional Education'),
                ('refugee_school', 'Refugee Education Center'),
                ('nursery', 'Nursery School'),
                ('combined', 'Combined School (Multiple Levels)'),
            ], max_length=50),
        ),
    ]
