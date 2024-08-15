from django.urls import path
from . import views

urlpatterns = [
    #register,login and logout
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('company_dashboard/', views.company_dashboard, name='company_dashboard'),
    path('', views.applicant_dashboard, name='applicant_dashboard'),
    #company profile creation
    path('comapny_profile_create/', views.company_profile, name='company_profile_creation'),
    path('company-profile/',views.company_profile_view, name='company_profile_view'),
    #job posting
    path('company/jobs/create/', views.create_job_post, name='create_job_post'),
    path('company/job_list/',views.jobList , name='joblist'),
    #applicant profiles
    path('applicant/create-profile/', views.create_applicant_profile, name='create_appli_profile'),
    path('applicant/view_profile/',views.view_applicant_profile,name='applicant__profile_view'),
     # Application Recruiter URLs
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('applicant/application/detail/<int:job_id>/', views.jobdetail, name='applicant_update_application_status'),
    path('job/<int:job_id>/applications/',views.view_applications, name='view_applications'),        
    #Notification
    path('company-notifications/<int:job_id>/', views.companyNotifications, name='company_notifications'),
    path('notification/applicant_notification/',views.applicantNotifications,name='applicant_notifications'),
    
]