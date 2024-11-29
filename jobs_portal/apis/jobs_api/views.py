from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apis.util import ApiResponse
from apis.permissions import EmployerPermissions, ApplicantPermissions
from jobs.models import Jobs, Application
from .serializers import JobsModelSerializer, ApplicationModelSerializer


class JobsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        queryset = Jobs.objects.all()
        serializer = JobsModelSerializer(instance = queryset, many=True)

        return ApiResponse.success(serializer.data, "Jobs Fetched Successfully")
    
    def post(self, request):
        self.permission_classes = [EmployerPermissions]
        self.check_permissions(request)

        serializer = JobsModelSerializer(data = request.data)
        if not serializer.is_valid():
            return ApiResponse.serializer_error(serializer.errors, "Error Occoured")
        
        serializer.save()
        return ApiResponse.success(serializer.data, "Job Created Successfully")
    

class EmployerJobs(APIView):
    permission_classes = [AllowAny]
    
    def get(self,request, emp_id, job_id=None):
        self.permission_classes = [AllowAny]
        self.check_permissions(request)


        if job_id is not None:
            try:
                queryset = Jobs.objects.get(employer_id= emp_id, pk=job_id)
            except Exception as e:
                return ApiResponse.error(str(e), "Please Enter Correct Job ID")
            
            serializer = JobsModelSerializer(instance=queryset)
            return ApiResponse.success(serializer.data,"Jobs Fetched Successfully")

        queryset = Jobs.objects.filter(employer_id=emp_id)
        serializer = JobsModelSerializer(instance=queryset, many=True)

        return ApiResponse.success(serializer.data, "Jobs Fetched Successfully")
    
    def put(self,request,emp_id, job_id=None):
        self.permission_classes = [EmployerPermissions]
        self.check_permissions(request)

        if emp_id != request.user.id:
            return ApiResponse.error("Invalid Operation", "Error Occoured")

        if not job_id:
            return ApiResponse.error("Job Id is required to Update Record", "Error Occoured")
        
        try:
            job_obj = Jobs.objects.get(id=job_id)
        except Exception as e:
            return ApiResponse.error(str(e),"Error Occoured")
        
        serializer = JobsModelSerializer(instance= job_obj,data= request.data, partial=True)
        if not serializer.is_valid():
            return ApiResponse.serializer_error(serializer.errors, "Failed to Update Data")
        
        serializer.save()
        return ApiResponse.success(serializer.data, "Job Updated Successfully")


class EmpApplicationView(APIView):
    permission_classes = [EmployerPermissions]

    def get(self, request, emp_id, job_id):

        if emp_id != request.user.id:
            return ApiResponse.error("Invalid Operation", "Error Occoured.")

        try:
            job_obj = Jobs.objects.get(employer_id = emp_id, id = job_id)
        except Exception as e:
            return ApiResponse.error(str(e), "Please Enter correct employer and job id.")
        
        queryset = Application.objects.filter(job_listing=job_obj)
        serializer = ApplicationModelSerializer(instance=queryset, many=True)

        return ApiResponse.success(serializer.data, "All applications for this JOB")


class ApplicationView(APIView):
    permission_classes = [ApplicantPermissions]

    def get(self,request):
        queryset = Application.objects.filter(applicant = request.user)
        serializer = ApplicationModelSerializer(instance=queryset, many=True)

        return ApiResponse.success(serializer.data, f"All application of user {request.user.first_name} {request.user.last_name}")

    def post(self,request):
        post_data = request.data.copy()
        post_data.update({"applicant" : request.user.id})
        serializer = ApplicationModelSerializer(data = post_data)

        if not serializer.is_valid():
            return ApiResponse.serializer_error(serializer.errors, "Error Occoured")
        
        serializer.save()
        return ApiResponse.success(serializer.data, "Job Applied Successfully")