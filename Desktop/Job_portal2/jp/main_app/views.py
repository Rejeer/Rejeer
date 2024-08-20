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
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
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
def applicant_detail(request):
    applicant_obj = Applicant.objects.all()
    context = {'applicant_obj':applicant_obj}
    return render(request,'applicant_details.html',context)


@login_required
def company_detail(request):
    company_obj = Company.objects.all()
    context = {'company_obj':company_obj}
    return render(request,'company_detail.html',context)

@login_required
def company_dashboard(request):
    # Get the companies associated with the logged-in user
    company = request.user.companies.first()  # Retrieves the first company associated with the user
    
   

    # Fetch job posts related to this company
    job_posts = JobAds.objects.filter(company=company)

    return render(request, 'company_dashboard.html', {'job_posts': job_posts, 'company': company})

from django.shortcuts import render, redirect
from django.http import HttpResponse

def applicant_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    try:
        search_term = request.GET.get('title', '')
        selected_location = request.GET.get('location', '')

        job_posts = JobAds.objects.all()
        
        if search_term:
            job_posts = job_posts.filter(title__icontains=search_term)
        
        if selected_location:
            job_posts = job_posts.filter(location=selected_location)
        
        job_posts = job_posts.order_by('-created_at')
        
        locations = JobAds.objects.values('location').distinct()
        
        context = {
            'job_posts': job_posts,
            'locations': locations,
            'search_term': search_term,
            'selected_location': selected_location
        }
        
        return render(request, 'applicant_dashboard.html', context)

    except Exception as e:
        # Log the error if needed
        return HttpResponse(f"An error occurred: {e}")


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
            print(f"Job Post ID: {job_post.id}")
            return redirect('company_dashboard')
    else:
        form = JobPostForm()
       

        
    education_choices = Education.objects.all()
    print("Education choices:", list(education_choices))  # Add this line
    
    return render(request, 'job_post.html', {'form': form})

@login_required
def edit_job_post(request, post_id):
    # Get the job post for the given post_id that belongs to the user's company
    job_post = get_object_or_404(JobAds, id=post_id)
    
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job_post)
        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.save()
            return redirect('company_dashboard')
    else:
        form = JobPostForm(instance=job_post)

    education_choices = Education.objects.all()
    print("Education choices:", list(education_choices))

    return render(request, 'job_post.html', {'form': form, 'edit_mode': True})

@login_required
def delete_job_post(request, post_id):
    # Get the job post for the given post_id that belongs to the user's company
    job_post = get_object_or_404(JobAds, id=post_id, company__user=request.user)
    
    # If the request is a POST (confirming deletion)
    if request.method == 'POST':
        job_post.delete()
        return redirect('company_dashboard')
    
    # If the request is a GET, render a confirmation page
    return render(request, 'delete_job.html', {'job_post': job_post})


@login_required
def jobList(request):
    if request.user.is_authenticated:
        # User company check
        if hasattr(request.user, 'company'):
            user_company = request.user.company

            # Filter job posts based on the user's company
            job_posts = JobAds.objects.filter(company=user_company).order_by('-created_at')
        else:
            # If the user has no associated company, show no posts
            job_posts = JobAds.objects.none()
    else:
        # If the user is not logged in, show all job posts
        job_posts = JobAds.objects.all().order_by('-created_at')
    return render(request, 'jobpost_list.html', {'job_posts': job_posts} )

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
    return render(request,'apply_for_job.html',context)

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

    if request.method == 'POST':
        if Application.objects.filter(job=job, seeker=applicant).exists():
            return render(request, 'already_applied.html', {
                'job': job,
                'message': 'You have already applied for this job.'
            })

        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter')

        # Check if resume is provided
        if not resume:
            return render(request, 'view_application.html', {
                'job': job,
                'error': 'Please upload a resume to apply.'
            })

        applied = Application.objects.create(
            job=job,
            seeker=applicant,
            resume=resume,
            cover_letter=cover_letter
        )

        company_user = job.company.user
        Notification.objects.create(
            company=company_user,
            applicant=applicant,
            job=job,
            message=f"New application received for {job.title}"
        )

        return redirect('applicant_view_application.html', application_id=applied.id)

    return render(request, 'apply_job.html', {'job': job})




def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Assuming the Application model has a reference to the Company
    company_email = application.job.company.email  # Retrieve the company's email from the application
    
    # Send email to the company to notify about the application
    send_mail(
        subject='New Application Viewed',  # Subject of the email
        message=f'The application for {application.job.title} has been viewed.',  # Email body
        from_email=settings.DEFAULT_FROM_EMAIL,  # Email sender
        recipient_list=[company_email],  # Recipient list
        fail_silently=False,  # Ensures failure is raised if email fails to send
    )
    
    return render(request, 'applicant_notification.html', {'application': application})

# delete and edit

@login_required
def edit_application(request, application_id):
    # Implementation for editing application
    pass

@login_required
def delete_application(request, application_id):
    # Implementation for deleting application
    pass

@login_required
def view_job(request, job_id):
    job = get_object_or_404(JobAds, id=job_id)
    return render(request, 'view_job.html', {'job': job})


@login_required
def view_applicant_detail(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    return render(request, 'applicant_detail.html', {'applicant': applicant})


@login_required
def view_applicant_detail(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    return render(request, 'applicant_detail.html', {'applicant': applicant})

@login_required
def applicant_notifications(request):
    # Your logic for handling notifications goes here
    return render(request, 'applicant_notification.html')

@login_required
def company_notifications(request):
    company = request.user.companies.first()  # Assuming the user has one company

    # Filter job ads where the company matches the logged-in user's company
    job_ads = JobAds.objects.filter(company=company)

    # Filter applications where the job is one of the company's job ads
    applications = Application.objects.filter(job__in=job_ads)
    return render(request, 'applicant_notification.html' , {'applications': applications})


@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'application_detail.html', {'application': application})


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def toggle_applicant_status(request, applicant_id):
    applicant = get_object_or_404(CustomUser, id=applicant_id, role=3)  # Ensure it targets only applicants
    applicant.is_active = not applicant.is_active  # Toggle active status
    applicant.save()
    return redirect('applicant_detail')