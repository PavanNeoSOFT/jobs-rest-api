from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError as drfValidationError
from jobs.models import Jobs, Application


class JobsModelSerializer(ModelSerializer):
    class Meta:
        model = Jobs
        fields = "__all__"


class ApplicationModelSerializer(ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"

    def validate(self, data):
        applicant_id = data.get("applicant")
        job_id = data.get("job_listing")
        
        if Application.objects.filter(applicant_id = applicant_id, job_listing_id = job_id).exists():
            raise drfValidationError("Application Already Submitted")
        
        return data
