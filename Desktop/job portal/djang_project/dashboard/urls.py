from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard,name='dashboard'),
    # path('applicant_dashboard/',views.applicant_dashboard,name='applicant_dashboard'),
    # path('recruiter_dashboard',views.recruiter_dashboard,name='recruiter_dashboard'),

]
