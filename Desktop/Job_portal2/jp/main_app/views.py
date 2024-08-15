from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate,logout, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from django.urls import reverse
from django.http import HttpResponse
from .forms import JobPostForm

# Custom User Creation Form
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Redirect based on user role
            if user.role == 1:  # Admin
                return redirect('admin_dashboard')
            elif user.role == 2:  # Company
                return redirect('company_dashboard')
            elif user.role == 3:  # Applicant
                return redirect('applicant_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.role == 1:  # Admin
                return redirect('admin_dashboard')
            elif user.role == 2:  # Company
                return redirect('company_dashboard')
            elif user.role == 3:  # Applicant
                return redirect('applicant_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def company_dashboard(request):
    # Get the companies associated with the logged-in user
    company = request.user.companies.first()  # Retrieves the first company associated with the user
    
    if not company:
        return HttpResponse("No company found for this user")

    # Fetch job posts related to this company
    job_posts = JobAds.objects.filter(company=company)

    return render(request, 'company_dashboard.html', {'job_posts': job_posts, 'company': company})


@login_required
def applicant_dashboard(request):
    job_posts = JobAds.objects.all().filter().order_by('-created_at')

    context = {
        'job_posts': job_posts,
    }
    return render(request, 'applicant_dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login') 

@login_required
def company_profile(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user  # Set the user to the current logged-in user
            company.save()
            return redirect('company_dashboard')  # Redirect to a success page or another view
    else:
        form = CompanyForm()
    
    return render(request, 'company_prfl_creation.html', {'form': form})

@login_required
def company_profile_view(request):
    try:
        
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
     
        company = None
    
    return render(request, 'company_profile.html', {'company': company})

@login_required
def create_job_post(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)    
        if form.is_valid():
            job_post = form.save(commit=False)
            try:
                company = Company.objects.get(user=request.user)
                job_post.company = company
            except Company.DoesNotExist:
                # Handle the case where the user does not have a company profile
                pass
            job_post.save()
            return redirect('joblist')
    else:
        form = JobPostForm()
       

        
    education_choices = Education.objects.all()
    print("Education choices:", list(education_choices))  # Add this line
    
    return render(request, 'job_post.html', {'form': form})


@login_required
def jobList(request):
    
    job_posts = JobAds.objects.all().order_by('-created_at') 
    return render(request, 'jobpost_list.html', {'job_posts': job_posts})

@login_required
def jobdetail(request,job_id):
    try:
        job_obj = JobAds.objects.get(id=job_id)
    except JobAds.DoesNotExist:
        job_obj = None

    context = {
        'job_ad': job_obj,
        'education_required': job_obj.education_required if job_obj else None,
    }
    return render(request,'applicant_update_status.html',context)

#applicant
@login_required
def create_applicant_profile(request):
    if request.method == 'POST':
        form = ApplicantProfileForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save(commit=False)
            applicant.user = request.user
            applicant.save()
            return redirect('applicant__profile_view')
    else:
        form = ApplicantProfileForm()

    return render(request, 'applicant_create_profile.html', {'form': form})

# context_processors.py
def applicant_profile_status(request):
    if request.user.is_authenticated:
        return {
            'has_applicant_profile': hasattr(request.user, 'applicant')
        }
    return {}


@login_required
def view_applicant_profile(request):
    # Get the applicant profile for the logged-in user
    applicant = get_object_or_404(Applicant, user=request.user)
    return render(request, 'applicant_profile.html', {'applicant': applicant})


@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(JobAds, id=job_id)
    applicant = request.user

    # Check if the applicant has already applied for this job
    if Application.objects.filter(job=job, seeker=applicant).exists():
        context = {
            'job': job,
            'message': 'You have already applied for this job.',
            'success': False
        }
    else:
        # Create a new application
        Application.objects.create(job=job, seeker=applicant, resume=applicant.applicant.resume)
        
        # Now create a notification for the company
        company_user = job.company.user  # Get the 'CustomUser' associated with the company
        Notification.objects.create(
            company=company_user,  # This is now the 'CustomUser' instance
            applicant=applicant,   # The applicant applying for the job
            job=job,               # The job to which the applicant applied
            message="New job application received!"
        )

        context = {
            'job': job,
            'message': 'Your application has been submitted successfully.',
            'success': True
        }

    return render(request, 'applicant_view_application.html', context)


@login_required
def view_applications(request, job_id):
    try:
        job = JobAds.objects.get(id=job_id, company__user=request.user)
        applications = Application.objects.filter(job=job)
    except JobAds.DoesNotExist:
        applications = None

    return render(request, 'view_applications.html', {'job': job, 'applications': applications})


@login_required
def companyNotifications(request, job_id):

    job = get_object_or_404(JobAds, id=job_id, company=request.user.company)  # Ensure the job belongs to the company
    notifications = Notification.objects.filter(job=job)  # Fetch notifications for the job
    return render(request, 'company_notifications.html', {'notifications': notifications, 'job': job})

@login_required
def applicantNotifications(request):
    return render(request,'applicant_notification.html')

