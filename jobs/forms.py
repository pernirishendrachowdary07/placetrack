from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    """
    Form for creating and updating job postings.
    Includes validation and clear input placeholders.
    """
    class Meta:
        model = Job
        fields = ['title', 'company', 'description', 'required_skills']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Junior Python Developer'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Google, Nexus Tech'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter comprehensive job responsibilities and overview...'
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Python, Django, SQL, REST APIs (comma-separated)'
            }),
        }
        help_texts = {
            'required_skills': 'Separate skills with commas (e.g. Python, Django, Docker). These are matched with student resumes.'
        }
