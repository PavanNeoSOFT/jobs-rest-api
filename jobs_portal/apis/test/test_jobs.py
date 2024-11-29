from faker import Faker
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group
from users.models import User
from jobs.models import Jobs

class JobAPITest(APITestCase):
    def setUp(self):

        self.fake = Faker()

        self.get_all_jobs = reverse("view_all_jobs")

        return super().setUp()
    
    def create_applicant_user(self):
        """Create"""
        
        self.applicant_user = {
            "username":"testusera",
            "password":"password123",
            "first_name":self.fake.first_name(),
            "last_name":self.fake.last_name(),
            "email":self.fake.email(),
            "user_type":"applicant",
        }
        Group.objects.get_or_create(name="applicant")

        self.client.post(path=reverse("register_user"), data=self.applicant_user)

        login = self.client.post(
            path=reverse("token_obtain_pair"),
            data={"username": self.applicant_user["username"], "password": self.applicant_user["password"]},
        )
        self.access_token = login.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        return User.objects.get(username="testusera")

    def create_employer_user(self):
        
        self.employer_user = {
            "username":"testusere",
            "password":"password123",
            "first_name":self.fake.first_name(),
            "last_name":self.fake.last_name(),
            "email":self.fake.email(),
            "user_type":"employer",
        }
        Group.objects.get_or_create(name="employer")

        self.client.post(path=reverse("register_user"), data=self.employer_user)

        login = self.client.post(
            path=reverse("token_obtain_pair"),
            data={"username": self.employer_user["username"], "password": self.employer_user["password"]},
        )
        self.access_token = login.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        return User.objects.get(username="testusere")
    
    def create_job_post(self, employer):

        job_dict = {
            "employer": employer,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Docker, Kubernetes, Jenkins, Cloud Computing",
            "experience_level": "5+ years",
            "job_open": True,
            "work_from": "H"
        }

        job_obj = Jobs.objects.create(**job_dict)
        job_obj.save()
        return job_obj
    
    def test_fetch_jobs_all(self):

        emp_obj = self.create_employer_user()
        self.create_job_post(employer=emp_obj)

        response = self.client.get(path=self.get_all_jobs)
        self.assertEqual(response.status_code,200)

    def test_create_job_success(self):

        emp_obj = self.create_employer_user()
        job_dict = {
            "employer": emp_obj.id,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.post(path=self.get_all_jobs,data=job_dict)
        self.assertEqual(response.status_code,200)

    def test_create_job_few_data_error(self):
    
        emp_obj = self.create_employer_user()
        job_dict = {
            "employer": emp_obj.id,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
        }

        response = self.client.post(path=self.get_all_jobs,data=job_dict)
        self.assertEqual(response.status_code,400)

    def test_create_job_no_employer(self):

        job_dict = {
            "employer": "",
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.post(path=self.get_all_jobs,data=job_dict)
        self.assertEqual(response.status_code,401)
    
    def test_fetch_job_employer_wise(self):

        emp_obj = self.create_employer_user()
        self.create_job_post(employer=emp_obj)

        response = self.client.get(path=f"/api/job/{emp_obj.id}/")
        self.assertEqual(response.status_code, 200)

    def test_job_detail_view(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(employer=emp_obj)

        response = self.client.get(path=f"/api/job/{emp_obj.id}/{job_obj.id}/")
        self.assertEqual(response.status_code, 200)

    def test_fetch_job_employer_error(self):

        response = self.client.get(path=f"/api/job/10/")
        self.assertEqual(response.status_code, 200)

    def test_job_detail_view_error(self):

        emp_obj = self.create_employer_user()

        response = self.client.get(path=f"/api/job/{emp_obj.id}/10/")
        self.assertEqual(response.status_code, 400)

    def test_update_job_success(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(employer=emp_obj)

        job_update_dict = {
            "employer": emp_obj.id,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.put(path=f"/api/job/{emp_obj.id}/{job_obj.id}/", data= job_update_dict)
        self.assertEqual(response.status_code, 200)

    def test_update_job_error(self):

        job_update_dict = {
            "employer": 10,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.put(path=f"/api/job/10/10/", data= job_update_dict)
        self.assertEqual(response.status_code, 401)

    def test_update_job_incorrect_emp_id(self):

        emp_obj = self.create_employer_user()

        job_update_dict = {
            "employer": emp_obj.id,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.put(path=f"/api/job/{emp_obj.id + 1}/1/", data= job_update_dict)
        self.assertEqual(response.status_code, 400)

    def test_update_job_no_job_id(self):

        emp_obj = self.create_employer_user()

        job_update_dict = {
            "employer": emp_obj.id,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.put(path=f"/api/job/{emp_obj.id}/", data= job_update_dict)
        self.assertEqual(response.status_code, 400)

    def test_update_incorrect_job_id(self):

        emp_obj = self.create_employer_user()

        job_update_dict = {
            "employer": emp_obj.id,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.put(path=f"/api/job/{emp_obj.id}/100/", data= job_update_dict)
        self.assertEqual(response.status_code, 400)

    def test_update_job_desc_wrong_empid(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(employer=emp_obj)

        job_update_dict = {
            "employer": 100,
            "job_title": self.fake.job(),
            "description": self.fake.paragraph(nb_sentences=1),
            "location": self.fake.address(),
            "salary_min": self.fake.random_number(digits=5,fix_len=True),
            "salary_max": self.fake.random_number(digits=5,fix_len=True),
            "job_type": "CT",
            "required_skills": "Python",
            "experience_level": "0 years",
            "job_open": True,
            "work_from": "H"
        }

        response = self.client.put(path=f"/api/job/{emp_obj.id}/{job_obj.id}/", data= job_update_dict)
        self.assertEqual(response.status_code, 400)

    def test_view_applications_for_employers(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(employer=emp_obj)

        response = self.client.get(path=f"/api/job/{emp_obj.id}/{job_obj.id}/applications/",)
        self.assertEqual(response.status_code, 200)

    def test_view_applications_for_employers_error(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(employer=emp_obj)

        response = self.client.get(path=f"/api/job/{emp_obj.id +1}/{job_obj.id}/applications/",)
        self.assertEqual(response.status_code, 400)

    def test_view_applications_for_emp_wrong_jobid(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(employer=emp_obj)

        response = self.client.get(path=f"/api/job/{emp_obj.id}/{job_obj.id +1}/applications/",)
        self.assertEqual(response.status_code, 400)

    def test_create_application_success(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(emp_obj)

        self.create_applicant_user()

        response = self.client.post(path="/api/job/apply/",data={"job_listing" : job_obj.id})
        self.assertEqual(response.status_code, 200)

    def test_create_duplicate_application(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(emp_obj)

        self.create_applicant_user()

        response = self.client.post(path="/api/job/apply/",data={"job_listing" : job_obj.id})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(path="/api/job/apply/",data={"job_listing" : job_obj.id})
        self.assertEqual(response.status_code, 400)

    def test_view_applications_for_applicant(self):

        emp_obj = self.create_employer_user()
        job_obj = self.create_job_post(emp_obj)

        self.create_applicant_user()

        response = self.client.post(path="/api/job/apply/",data={"job_listing" : job_obj.id})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path="/api/job/apply/")
        self.assertEqual(response.status_code, 200)

    def test_view_applications_without_login(self):

        response = self.client.get(path="/api/job/apply/")
        self.assertEqual(response.status_code, 401)
