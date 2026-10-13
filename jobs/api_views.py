from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Job, Application
from .serializers import (
    JobSerializer,
    ApplicationSerializer,
    ApplicationApplySerializer,
    ApplicationStatusUpdateSerializer,
    MatchRequestSerializer,
    MatchResponseSerializer,
)
from .api_permissions import IsAdminOrReadOnly, IsPlacementAdmin, IsStudentUser
from resumes.models import Resume
from resumes.matcher import match


@extend_schema(tags=['Jobs'])
class JobViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for Job openings:
    - Any authenticated student or admin can list and view jobs.
    - Only placement admins can create, update, or delete jobs.
    """
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('search', '').strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(company__icontains=query) |
                Q(required_skills__icontains=query)
            )
        return queryset

    @extend_schema(
        summary="Calculate candidate match score for this job",
        responses={200: MatchResponseSerializer}
    )
    @action(detail=True, methods=['get'], permission_classes=[IsStudentUser])
    def match(self, request, pk=None):
        """
        Check how well the calling student's resume matches this job opening.
        """
        job = self.get_object()
        student_resume = Resume.objects.filter(user=request.user).first()
        if not student_resume or not student_resume.extracted_text:
            return Response(
                {"error": "Please upload a resume first to calculate match scores."},
                status=status.HTTP_400_BAD_REQUEST
            )

        match_data = match(student_resume.extracted_text, job.required_skills)
        match_data.update({
            'job_id': job.id,
            'job_title': job.title,
            'company': job.company,
        })
        return Response(match_data, status=status.HTTP_200_OK)


@extend_schema(tags=['Applications'])
class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Endpoints for job applications:
    - Students see only their applications and can apply for jobs.
    - Admins see all applications and can update candidate hiring status.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.is_superuser:
            qs = Application.objects.all().select_related('user', 'job').order_by('-match_score', '-applied_at')
            job_id = self.request.query_params.get('job_id')
            if job_id and job_id.isdigit():
                qs = qs.filter(job_id=int(job_id))
            return qs
        # Students see only their applications
        return Application.objects.filter(user=user).select_related('job').order_by('-applied_at')

    @extend_schema(
        summary="Submit job application (Students only)",
        request=ApplicationApplySerializer,
        responses={201: ApplicationSerializer}
    )
    def create(self, request, *args, **kwargs):
        """
        Students apply for a job with their active resume.
        The current match score is automatically computed and saved with the application.
        """
        if request.user.role != 'student':
            return Response(
                {"error": "Only student accounts can apply for jobs."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApplicationApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data['job_id']

        job = get_object_or_404(Job, id=job_id)

        # Check for existing application
        if Application.objects.filter(user=request.user, job=job).exists():
            return Response(
                {"error": f"You have already applied for '{job.title}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Compute match score from resume
        score = 0.0
        resume = Resume.objects.filter(user=request.user).first()
        if resume and resume.extracted_text:
            match_res = match(resume.extracted_text, job.required_skills)
            score = match_res['score']

        application = Application.objects.create(
            user=request.user,
            job=job,
            status='Applied',
            match_score=score
        )

        output_serializer = ApplicationSerializer(application)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update applicant status (Admins only)",
        request=ApplicationStatusUpdateSerializer,
        responses={200: ApplicationSerializer}
    )
    @action(detail=True, methods=['patch', 'post'], permission_classes=[IsPlacementAdmin])
    def update_status(self, request, pk=None):
        """
        Admins update the status of an application (Applied, Shortlisted, Interview, Selected, Rejected).
        """
        application = self.get_object()
        serializer = ApplicationStatusUpdateSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ApplicationSerializer(application).data, status=status.HTTP_200_OK)


@extend_schema(tags=['Match Results'])
class MatchCheckAPIView(APIView):
    """
    Endpoint for evaluating candidate resume compatibility against any job.
    """
    permission_classes = [IsStudentUser]

    @extend_schema(
        summary="Check resume match against a job",
        request=MatchRequestSerializer,
        responses={200: MatchResponseSerializer}
    )
    def post(self, request):
        serializer = MatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data['job_id']

        job = get_object_or_404(Job, id=job_id)
        resume = Resume.objects.filter(user=request.user).first()

        if not resume or not resume.extracted_text:
            return Response(
                {"error": "No resume found. Please upload a PDF or TXT resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        match_data = match(resume.extracted_text, job.required_skills)
        match_data.update({
            'job_id': job.id,
            'job_title': job.title,
            'company': job.company,
        })
        return Response(match_data, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class CustomObtainAuthToken(ObtainAuthToken):
    """
    Endpoint to exchange username & password for an API Token.
    Returns token, username, and user role.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
        })
