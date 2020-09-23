from django.urls import path, include
from django.conf.urls import url
from . import views
from . import compute

urlpatterns = [
path('home', views.show_data, name = 'show_data'),
#path('mean', views.cal_means, name = 'cal_means'),
path('fileupload', views.fileupload, name = 'cal_means'),
path('filtered-data',views.filtered_data,name='filtereddata'),
path('',views.User_login,name=''),
path('oldstrategy',views.get_oldstrategy,name='oldstrategy'),
path('view_file_metadata',views.get_file_metadata,name='view_file_metadata'),
path('createstrategy',views.create_strategy,name='createstrategy'),
path('treatment',views.treatment,name='treatment'),
path('create_treatment',views.create_treatment,name='create_treatment'),
path('update_treatment',views.update_treatment,name='update_treatment'),
path('update_treatment_detail',views.update_treatment_detail,name='update_treatment_detail'),
path('view_treatment',views.getall_treatments,name='view_treatment'),
path('StrategyTreatmentView',views.stratergy_treatment_view,name='StrategyTreatmentView'),
path('newstrategy-s',views.new_strategy,name='newstrategy'),
path('Viewstrategies',views.getall_startegies,name='Viewstrategies'),
path('ViewSingleStratergy',views.get_single_stratergy,name='ViewSingleStratergy'),
path('tca',views.create_tca,name='tca'),
path('viewtca',views.view_tca,name='viewtca'),  
path('view<str:id>',views.tca_views),
path('edittca',views.update_tca),
path('param_mapping',views.getall_paramsmapping,name='param_mapping'),
path('FetchParamsByFile/<str:file>',views.fetch_param_by_file),
path('FetchParamMappingById/<str:id>',views.fetch_param_mapping_by_id),
path('create_param_mapping',views.create_param_mapping),
path('update_param_mapping',views.update_param_mapping),
path('risk_returns',views.risk_return_view),
path('upload_risk_return_file',views.upload_risk_return_file),
path('custom_view',views.get_custom_views, name='custom_views'),
path('get_all_treat_data',views.get_all_treat_data, name='get_all_treat_data'),
path('GetParamsByTreatmentId/<str:id>',views.get_params_by_treatment_id),
path('visual',views.visual,name="visual"),


# url(r'^FetchParamsByFile/$',views.fetch_param_by_file),


# path('django_plotly_dash/', include('django_plotly_dash.urls')),

#path('newstrategy',views.new_strategy,name='newstrategy')
#path('filtered-data',views.filtered_data,name='filtereddata')

]