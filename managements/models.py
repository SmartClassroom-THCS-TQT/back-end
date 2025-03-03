from django.db import models

# Create your models here.
from django.db import models
from datetime import timedelta, date
from accounts.models import Student


class Room (models.Model):
    code = models.CharField(max_length=10, primary_key=True)

    name = models.CharField(max_length=255)
    manager = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    def get_students(self):
        return Student.objects.filter(classroom=self)
    def get_capacity(self):
        return self.students.count()  # Trả về số học sinh trong phòng học
    def __str__(self):
        return self.name + ' - ' + self.code
# Bảng học kỳ   
class Semester(models.Model):
    code = models.IntegerField(primary_key=True)

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
            return None  # Ngày vượt qua ngày kết thúc của học kỳ
        return current_week


    def __str__(self):
        return f"{self.code} - {self.start_date} - {self.weeks_count} weeks- {self.end_date}"

# bảng môn học
class Subject(models.Model):
    code = models.BigIntegerField(primary_key=True)  

    name = models.CharField(max_length=255)  
    description= models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name + ' - ' + str(self.code)

# bảng chia thời gian trong ngày học
class Time_slot(models.Model):
    code = models.PositiveIntegerField(primary_key=True)  # Time slot number
    start_time = models.TimeField()  # Start time of the session
    end_time = models.TimeField()  # End time of the session

    def __str__(self):
        return f"Session {self.code} from {self.start_time} to {self.end_time}"
  
    

GRADE_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
]

# bảng phiên học
class Session(models.Model):
    id = models.AutoField(primary_key=True)
    semester_code = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='sessions') # học kỳ
    subject_code = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions') # môn học
    room_code = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='sessions')  # Room where the lesson is taught
    day = models.DateField()  # Session day
    time_slot = models.ForeignKey(Time_slot, on_delete=models.CASCADE)  # Session time

    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE,related_name='sessions')  # Teacher teaching the lesson
    lesson_number = models.IntegerField()  # Lesson number
    lesson_name = models.CharField(max_length=255)
    detail = models.TextField(blank=True, null=True)  
    document = models.FileField(upload_to='lesson-documents/', blank=True, null=True)  # Document of the lesson
    comment = models.TextField(blank=True, null=True)  # Optional comment
    grade = models.CharField(max_length=1,choices=GRADE_CHOICES, blank=True, null=True)  # Grade of the class session
    absences = models.PositiveIntegerField(null=True, blank=True)  # Number of absences
    status = models.BooleanField(default=False)  # Status of the class session

    def __str__(self):
        return f"{self.semester_code} - {self.room_code} - {self.day} - {self.time_slot} - {self.subject_code} - {self.teacher}"
    
class Teacher_assignment(models.Model):
    semester_code = models.ForeignKey(Semester, on_delete=models.CASCADE,related_name='teacher_assignment')  # Semester of the assignment
    subject_code = models.ForeignKey(Subject, on_delete=models.CASCADE,related_name='teacher_assignment')  # Subject of the assignment
    room_code = models.ForeignKey(Room, on_delete=models.CASCADE,related_name='teacher_assignment')  # Room where the lesson is taught

    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, related_name='teacher_assignment')  # Teacher of the assignment

    def __str__(self):
        return f"{self.semester_code} - {self.subject_code} - {self.room_code} - {self.teacher}"