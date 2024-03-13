from django.urls import path
from . import views

urlpatterns = (
    path(r'^home/', views.home, name='supervisor_home'),
    path(r'^$', views.home),
    path(r'^logout/$', views._logout, name='supervisor_logout'),

    path(r'^ongoing/$', views.ongoing_projects, name='ongoing_projects'),
    path(r'^unverified/$', views.unverified_projects, name='unverified_projects'),
    path(r'^submittedprojects/$', views.submitted_projects, name='submitted_projects'),
    path(r'^completedprojects/$', views.completed_projects, name='completed_projects'),
    path(r'^deletedprojects/$', views.deleted_projects, name='deleted_projects'),

    path(r'^project/(?P<project_id>[0-9]+)/$', views.viewproject, name='super_viewproject'),
    path(r'^project/presented/(?P<project_id>[0-9]+)/$', views.toggle_presented_project, name='toggle_presented'),
    path(r'^verify/(?P<project_id>[0-9]+)/$', views.verify_project, name='verify_project'),
    path(r'^unverify/(?P<project_id>[0-9]+)/$', views.unverify_project, name='unverify_project'),
    path(r'^complete/(?P<project_id>[0-9]+)/$', views.complete, name='complete'),
    path(r'^download/(?P<doc_id>[0-9]+)/$', views.download, name='super_download'),
    path(r'^student/(?P<user_id>[0-9]+)/$', views.view_student, name='super_viewuser'),
    path(r'^email/project/(?P<project_id>[0-9]+)/$', views.email_project, name='super_email_project'),
    path(r'^delete/project/(?P<project_id>[0-9]+)/$', views.deleteproject, name='super_delete_project'),
    path(r'^delete/project/(?P<project_id>[0-9]+)/force/$', views.force_delete_project,
        name='super_force_delete_project'),
    path(r'^delete/project/(?P<project_id>[0-9]+)/revert/$', views.revert_delete_project,
        name='super_revert_delete_project'),

    path(r'^allprojects/$', views.allprojects, name='super_allprojects'),
    path(r'^allow_project/$', views.allow_project, name='allow_project'),
    path(r'^toggle_allow_project/$', views.toggle_allow_project, name='toggle_allow_project'),

    path(r'^new_sem_page/$', views.new_sem_page, name='new_sem_page'),
    path(r'^create_new_semester/$', views.all_semesters, name='create_new_semester'),
    path(r'^update_semester/(?P<id>[0-9]+)/$', views.update_semester, name='update-semester'),
    path(r'^delete_semester/$', views.delete_semester, name='delete-semester'),

    path(r'^example/$', views.example_projects, name='example_projects'),
    path(r'^addtoexamples/(?P<project_id>[0-9]+)/$', views.add_to_examples, name='addtoexamples'),
    path(r'^removefromexamples/(?P<example_project_id>[0-9]+)/$', views.remove_from_examples, name='removefromexamples'),

    path(r'^basic_search/$', views.basic_search),
    path(r'^advanced_search/$', views.advance_search, name='advance_search'),

    path(r'^news/new/$', views.add_news, name='add_news'),
    path(r'^news/all/$', views.all_news, name='all_news'),
    path(r'^news/(?P<news_id>[0-9]+)/$', views.view_news, name='view_news'),
    path(r'^delete_news/(?P<news_id>[0-9]+)/$', views.delete_news, name='super_delete_news'),

    path(r'^all_ngos/$', views.all_NGO, name='super_all_NGO'),
    path(r'^NGO/(?P<NGO_id>[0-9]+)/$', views.view_NGO, name='super_view_ngo'),
    path(r'^NGO/(?P<NGO_id>[0-9]+)/update/$', views.update_ngo, name='super_update_ngo'),
    path(r'^suggested_NGO/$', views.suggested_NGOs, name='super_suggested_ngos'),
    path(r'^acceptNGO/(?P<noti_id>[0-9]+)/$', views.accept_NGO, name='accept_NGO'),
    path(r'^rejectNGO/(?P<noti_id>[0-9]+)/$', views.reject_NGO, name='reject_NGO'),
    path(r'^removeNGO/(?P<ngo_id>[0-9]+)/$', views.remove_NGO, name='remove_NGO'),
    path(r'^addNGO/$', views.add_NGO),

    path(r'^category/all/$', views.all_categories, name='super_allcategories'),
    path(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='super_viewcategory'),
    path(r'^addcategory/$', views.add_category),
    path(r'^deletecategory/(?P<category_id>[0-9]+)', views.delete_category, name='super_delete_category'),
    path(r'^category/(?P<category_id>[0-9]+)/update/$', views.update_category, name='super_update_category'),

    path(r'^TA/$', views.change_TA, name="TA"),
    path(r'^TA/(?P<TA_id>[0-9]+)/$', views.change_TA, name="TA_delete"),

    path(r'^report_semester/$', views.generateReport, name='generateReport'),
    path(r'^report_batch/$', views.generateBatchReport, name='generateBatchReport'),

    path(r'^logs/project/(?P<project_id>[0-9]+)/$', views.get_project_logs, name='super_project_logs'),
    path(r'^logs/TA/(?P<ta_id>[0-9]+)/$', views.get_TA_logs, name='super_TA_logs'),
    path(r'^update_batch/$', views.update_batch, name="update_batch"),

)
