from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')



class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'est_year', 'city', 'state']


class JobPostForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        empty_label="Select Company",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    education_required = forms.ModelChoiceField(
        queryset=Education.objects.all(),
        empty_label="Select Education",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = JobAds
        fields = ['company', 'title', 'description', 'location', 'employment_type', 'experience_required', 'education_required', 'skills_required', 'salary']
    
    education_required = forms.ModelChoiceField(queryset=Education.objects.all(), required=False)


class ApplicantProfileForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['first_name', 'last_name', 'title', 'resume', 'education', 'skills', 'experience']