from django.conf.urls import url

from . import views

urlpatterns = (
    url(r'^home/', views.home, name='supervisor_home'),
    url(r'^$', views.home),
    url(r'^logout/$', views._logout, name='supervisor_logout'),

    url(r'^ongoing/$', views.ongoing_projects, name='ongoing_projects'),
    url(r'^unverified/$', views.unverified_projects, name='unverified_projects'),
    url(r'^submittedprojects/$', views.submitted_projects, name='submitted_projects'),

    url(r'^project/(?P<project_id>[0-9]+)/$', views.viewproject, name='super_viewproject'),
    url(r'^project/presented/(?P<project_id>[0-9]+)/$', views.toggle_presented_project, name='toggle_presented'),
    url(r'^verify/(?P<project_id>[0-9]+)/$', views.verify_project, name='verify_project'),
    url(r'^unverify/(?P<project_id>[0-9]+)/$', views.unverify_project, name='unverify_project'),
    url(r'^complete/(?P<project_id>[0-9]+)/$', views.complete, name='complete'),
    url(r'^download/(?P<doc_id>[0-9]+)/$', views.download, name='super_download'),
    url(r'^student/(?P<user_id>[0-9]+)/$', views.view_student, name='super_viewuser'),
    url(r'^email/project/(?P<project_id>[0-9]+)/$', views.email_project, name='super_email_project'),
    url(r'^delete/project/(?P<project_id>[0-9]+)/$', views.deleteproject, name='super_delete_project'),
    url(r'^delete/project/(?P<project_id>[0-9]+)/force/$', views.force_delete_project,
        name='super_force_delete_project'),
    url(r'^delete/project/(?P<project_id>[0-9]+)/revert/$', views.revert_delete_project,
        name='super_revert_delete_project'),

    url(r'^allprojects/$', views.allprojects, name='super_allprojects'),

    url(r'^example/$', views.example_projects, name='example_projects'),
    url(r'^addtoexamples/(?P<project_id>[0-9]+)/$', views.add_to_examples, name='addtoexamples'),
    url(r'^removefromexamples/(?P<example_project_id>[0-9]+)/$', views.remove_from_examples, name='removefromexamples'),

    url(r'^basic_search/$', views.basic_search),
    url(r'^advanced_search/$', views.advance_search, name='advance_search'),

    url(r'^news/new/$', views.add_news, name='add_news'),
    url(r'^news/all/$', views.all_news, name='all_news'),
    url(r'^news/(?P<news_id>[0-9]+)/$', views.view_news, name='view_news'),
    url(r'^delete_news/(?P<news_id>[0-9]+)/$', views.delete_news, name='super_delete_news'),

    url(r'^all_ngos/$', views.all_NGO, name='super_all_NGO'),
    url(r'^NGO/(?P<NGO_id>[0-9]+)/$', views.view_NGO, name='super_view_ngo'),
    url(r'^NGO/(?P<NGO_id>[0-9]+)/update/$', views.update_ngo, name='super_update_ngo'),
    url(r'^suggested_NGO/$', views.suggested_NGOs, name='super_suggested_ngos'),
    url(r'^acceptNGO/(?P<noti_id>[0-9]+)/$', views.accept_NGO, name='accept_NGO'),
    url(r'^rejectNGO/(?P<noti_id>[0-9]+)/$', views.reject_NGO, name='reject_NGO'),
    url(r'^removeNGO/(?P<ngo_id>[0-9]+)/$', views.remove_NGO, name='remove_NGO'),
    url(r'^addNGO/$', views.add_NGO),

    url(r'^category/all/$', views.all_categories, name='super_allcategories'),
    url(r'^category/(?P<category_id>[0-9]+)/$', views.category, name='super_viewcategory'),
    url(r'^addcategory/$', views.add_category),
    url(r'^deletecategory/(?P<category_id>[0-9]+)', views.delete_category, name='super_delete_category'),
    url(r'^category/(?P<category_id>[0-9]+)/update/$', views.update_category, name='super_update_category'),

    url(r'^TA/$', views.change_TA, name="TA"),
    url(r'^TA/(?P<TA_id>[0-9]+)/$', views.change_TA, name="TA_delete"),

    url(r'^report/$', views.generateReport, name='generateReport'),

    url(r'^logs/project/(?P<project_id>[0-9]+)/$', views.get_project_logs, name='super_project_logs'),
    url(r'^logs/TA/(?P<ta_id>[0-9]+)/$', views.get_TA_logs, name='super_TA_logs'),
)
