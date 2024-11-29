from django.db import models
from users.models import User


class Jobs(models.Model):

    job_type_choices = [("FT", "Full-Time"), ("PT", "Part-Time"), ("CT", "Contract")]
    work_from_choices = [
        ("WFH", "Work From Home"),
        ("WFO", "Work From Office"),
        ("H", "Hybrid"),
    ]

    employer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="jobs"
    )
    job_title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=50, choices=job_type_choices)
    required_skills = models.CharField(max_length=255, verbose_name="Required skills")
    experience_level = models.CharField(max_length=50)
    posted_date = models.DateTimeField(auto_now_add=True)
    job_open = models.BooleanField(default=True)
    work_from = models.CharField(max_length=30, choices=work_from_choices)

    def __str__(self):
        return self.job_title


class Application(models.Model):

    application_status_choices = [
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
        ("hold", "Hold"),
    ]

    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applicant"
    )
    job_listing = models.ForeignKey(
        Jobs, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=20, choices=application_status_choices, default="applied")
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant} - {self.job_listing.job_title}"
