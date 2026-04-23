from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('categorie/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
]