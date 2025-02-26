from django.db import models

# Create your models here.
from django.db import models
from datetime import timedelta, date
from accounts.models import Student, Teacher, Admin

class Room (models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    def get_students(self):
        return Student.objects.filter(classroom=self)
    def get_capacity(self):
        return self.Student.count()  # Trả về số học sinh trong phòng học
# Bảng học kỳ   
class Semester(models.Model):
    name = models.IntegerField(primary_key=True)
    start_date = models.DateField()
    weeks_count = models.IntegerField()

    class Meta:
        db_table = 'semester'
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'

    def get_day_end(self):
        return self.start_date + timedelta(weeks=self.weeks_count)
    @property
    def end_date(self):
        return self.get_day_end()
    def get_week(self, input_date=None):
        if input_date is None:
            input_date = date.today()  
        if input_date < self.start_date:
            return None 
        delta_days = (input_date - self.start_date).days
        current_week = (delta_days // 7) + 1
        if current_week > self.weeks_count:
            return None  
        return current_week


    def __str__(self):
        day_end = self.get_day_end()
        return f"{self.name}"

   
class Subject(models.Model):
    code = models.BigIntegerField(unique=True)  # Unique subject code
    name = models.CharField(max_length=255)  # Name of the subject
    
    def __str__(self):
        return self.name

class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lesson_name = models.CharField(max_length=255)
    session_count = models.PositiveIntegerField()  # Number of sessions based on the program

    def __str__(self):
        return self.lesson_name

class ClassTime(models.Model):
    number = models.PositiveIntegerField(unique=True)  # Time slot number
    start_time = models.TimeField()  # Start time of the session
    end_time = models.TimeField()  # End time of the session

    def __str__(self):
        return f"Session {self.number} from {self.start_time} to {self.end_time}"

class ClassSession(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    class_group = models.CharField(max_length=50)  # Class group (e.g. Class A, B, C)
    day_of_week = models.PositiveIntegerField()  # Day of the week (1 for Monday, 7 for Sunday)
    number = models.ForeignKey(ClassTime, on_delete=models.CASCADE)  # Session time
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)  # The lesson being taught
    teachers = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE,related_name='class_sessions')  # Teacher teaching the lesson
    comment = models.TextField(blank=True)  # Optional comment
    grade = models.FloatField()  # Grade/score
    absences = models.PositiveIntegerField()  # Number of absences

    def __str__(self):
        return f"{self.class_group} - {self.lesson} - {self.teacher}"
    
