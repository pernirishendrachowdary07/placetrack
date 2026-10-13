import os
from django import forms
from .models import Resume

# 5 MB in bytes (5 * 1024 * 1024)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = ['.pdf', '.txt']


class ResumeUploadForm(forms.ModelForm):
    """
    Form for uploading a candidate resume file.
    Validates file extension (.pdf, .txt) and file size (<= 5 MB).
    """
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.txt',
                'id': 'resume-file-input',
            })
        }
        labels = {
            'file': 'Select Resume File (.pdf or .txt)'
        }
        help_texts = {
            'file': 'Maximum allowed file size: 5 MB. Text-based PDF or plain TXT files only.'
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if not uploaded_file:
            raise forms.ValidationError("Please select a resume file to upload.")

        # 1. Check file extension
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f"Unsupported file format '{ext}'. Only .pdf and .txt files are accepted."
            )

        # 2. Check maximum 5 MB file size
        if uploaded_file.size > MAX_FILE_SIZE_BYTES:
            size_in_mb = round(uploaded_file.size / (1024 * 1024), 2)
            raise forms.ValidationError(
                f"File size ({size_in_mb} MB) exceeds the maximum allowed limit of 5 MB."
            )

        return uploaded_file
