from django.urls import path
from . import views

urlpatterns = [
path('', views.show_data, name = 'show_data'),
#path('mean', views.cal_means, name = 'cal_means'),
path('fileupload', views.fileupload, name = 'cal_means'),

]