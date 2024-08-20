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
    path("", views.applicant_dashboard, name='applicant_dashboard'),
    #company profile creation
    path('comapny_profile_create/', views.company_profile, name='company_profile_creation'),
    path('company-profile/',views.company_profile_view, name='company_profile_view'),
    #job posting ,edit and delete 
    path('company/jobs/create/', views.create_job_post, name='create_job_post'),
    path('company/job_list/',views.jobList , name='joblist'),
    path('job/edit/<int:post_id>/', views.edit_job_post, name='edit_job_post'),
    path('job/delete/<int:post_id>/', views.delete_job_post, name='delete_job_post'),
    #applicant profiles
    path('applicant/create-profile/', views.create_applicant_profile, name='create_appli_profile'),
    path('applicant/view_profile/',views.view_applicant_profile,name='applicant__profile_view'),
     # Application Recruiter URLs
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('applicant/application/detail/<int:job_id>/', views.jobdetail, name='applicant_update_application_status'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),      
    #Notification
    # path('company-notifications/', views.notifications_page, name='notifications_page'),
    # path('notification/applicant_notification/',views.applicantNotifications,name='applicant_notifications'),
    path('notifications/', views.applicant_notifications, name='applicant_notifications'),
    path('notifications/', views.company_notifications, name='applicant_notifications'),
    #delete and edit 
    path('edit-application/<int:application_id>/',views. edit_application, name='edit_application'),
    path('delete-application/<int:application_id>/',views.delete_application, name='delete_application'),
    path('view-job/<int:job_id>/',views.view_job, name='view_job'),
    #application_details
    path('applicant/<int:applicant_id>/', views.view_applicant_detail, name='view_applicant_detail'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    #admin_dashboard details
    path('company_details/admin_dashboard/',views.company_detail,name='company_detail'),
    path('applicant_details/admin_dashboard/',views.applicant_detail,name='applicant_detail'),
    #is activate and Deactivate
    path('applicant/<int:applicant_id>/toggle-status/',views.toggle_applicant_status, name='toggle_applicant_status'),
]
