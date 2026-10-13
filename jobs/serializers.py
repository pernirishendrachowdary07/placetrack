from rest_framework import serializers
from .models import Job, Application


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for Job postings with parsed skills list.
    """
    skills_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'company', 'description', 'required_skills', 'skills_list', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_skills_list(self, obj):
        return obj.get_skills_list()


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing job applications.
    Includes applicant info and job details.
    """
    applicant_username = serializers.CharField(source='user.username', read_only=True)
    applicant_email = serializers.CharField(source='user.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'user', 'applicant_username', 'applicant_email',
            'job', 'job_title', 'job_company',
            'status', 'match_score', 'applied_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'match_score', 'applied_at']


class ApplicationApplySerializer(serializers.Serializer):
    """
    Serializer for students applying to a job.
    """
    job_id = serializers.IntegerField(help_text="ID of the job opening to apply for")


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admins updating application status.
    """
    class Meta:
        model = Application
        fields = ['status']


class MatchRequestSerializer(serializers.Serializer):
    """
    Request serializer to check match score against a job.
    """
    job_id = serializers.IntegerField(help_text="ID of the target job position")


class MatchResponseSerializer(serializers.Serializer):
    """
    Response serializer returning match score and skill breakdown.
    """
    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    company = serializers.CharField()
    score = serializers.FloatField(help_text="Match score percentage (0.0 to 100.0)")
    matched_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    total_skills = serializers.IntegerField()
