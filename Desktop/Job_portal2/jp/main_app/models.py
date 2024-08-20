from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.conf import settings

ROLE_CHOICES = [
    (1, 'Admin'),
    (2, 'Company'),
    (3, 'Applicant')
]

class CustomUserManager(BaseUserManager):
    def create_user(self, username=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not password:
            raise ValueError('The password field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 1)
        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='active')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.IntegerField(choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    def has_company(self):
        return self.companies.exists()
    
    def has_company(self):
        return Company.objects.filter(user=self).exists()
    
    def has_applicant_profile(self):
        return hasattr(self, 'applicant')


User=get_user_model()

class Company(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=50, null=True, blank=True)
    est_year = models.IntegerField(null=True)
    
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)  # Ensure this field is present
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.name
    

class Education(models.Model):
    EDUCATION_CHOICES = [
        ('HS', 'Higher Secondary'),
        ('DIP', 'Diploma'),
        ('DEG', 'Degree'),
        ('PG', 'Post Graduation'),
        ('MAS', 'Master'),
    ]

    education = models.CharField(max_length=30, choices=EDUCATION_CHOICES, blank=True)
    def __str__(self):
        return self.get_education_display()

class Skill(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.name

class JobType(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    )
    job_type = models.CharField(max_length=30,choices=JOB_TYPE_CHOICES, blank=True)
    def __str__(self):
        return dict(self.JOB_TYPE_CHOICES).get(self.job_type, 'Unknown Job Type')
    

class JobAds(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, null=True, blank=True)
    employment_type = models.ForeignKey(JobType,on_delete=models.SET_NULL, null=True, blank=True)  # e.g., Full-time, Part-time
    experience_required = models.IntegerField(null=True, blank=True)  # Number of years required
    education_required = models.ForeignKey(Education, on_delete=models.SET_NULL, null=True, blank=True)
    skills_required = models.ManyToManyField(Skill, related_name='job_posts')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    

class Applicant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=20, null=True)
    title = models.CharField(max_length=20, null=True)
    resume = models.FileField(upload_to='resumes/')
    education = models.ForeignKey(Education, on_delete=models.SET_NULL, null=True)
    skills = models.TextField()
    experience = models.TextField()

    def __str__(self) -> str:
        return self.first_name
    

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

class Application(models.Model):
    APPLICATION_STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    )
    job = models.ForeignKey(JobAds, on_delete=models.CASCADE)
    seeker = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return f" {self.seeker}: {self.job}"
    


@receiver(post_save, sender=Application)
def send_status_update_email(sender, instance, **kwargs):
    if kwargs.get('created', False):
        # Send email only when the status is changed and not when the application is created
        return

    subject = f"Your application status for {instance.job.title} has been updated"
    message = f"Dear {instance.seeker.first_name},\n\nYour application status has been updated to {instance.get_status_display()}.\n\nThank you for your interest in {instance.job.company_name}.\n\nBest regards,\n{instance.job.company_name}"
    
    recipient_list = [instance.seeker.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


class Notification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_notifications')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(JobAds, on_delete=models.CASCADE, related_name='job_notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.company.name}: {self.message}"