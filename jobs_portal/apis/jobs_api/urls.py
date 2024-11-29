from django.urls import path
from . import views


urlpatterns = [
    path("", views.JobsView.as_view(),name="view_all_jobs"),
    path("<int:emp_id>/",views.EmployerJobs.as_view(),name="view_jobs_employer_wise"),
    path("<int:emp_id>/<int:job_id>/",views.EmployerJobs.as_view(),name="job_detail_and_edit"),
    path("<int:emp_id>/<int:job_id>/applications/",views.EmpApplicationView.as_view(),name="view_applications_per_job"),
    path("apply/", views.ApplicationView.as_view(), name="view_all_applications_of_applicant"),
]