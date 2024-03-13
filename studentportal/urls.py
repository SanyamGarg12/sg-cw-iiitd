from django.urls import path
from . import views

urlpatterns = (
    # basic
    path(r'^home/', views.home, name='studenthome'),
    path(r'^$', views.index, name='index'),
    path(r'^profile/$', views.profile, name='studentprofile'),

    # projects and documents
    path(r'^add/$', views.addproject, name='addproject'),
    path(r'^project/(?P<project_id>[0-9]+)/edit/$', views.editproject, name='editproject'),
    path(r'^project/(?P<project_id>[0-9]+)/upload/$', views._upload, name='upload_document'),
    path(r'^project/(?P<project_id>[0-9]+)/$', views.viewproject, name='viewproject'),
    path(r'^project/(?P<project_id>[0-9]+)/submit/$', views.submitproject, name='submitproject'),
    path(r'^project/(?P<project_id>[0-9]+)/NGO/$', views.view_project_NGO, name='view_project_NGO'),
    path(r'^link_ngo_project/(?P<NGO_id>[0-9]+)/(?P<project_id>[0-9]+)/$',
        views.link_NGO_project, name='link_NGO_project'),
    path(r'^unlink_ngo_project/(?P<project_id>[0-9]+)/$', views.unlink_NGO_project,
        name='unlink_ngo_project'),
    path(r'^download/(?P<document_id>[0-9]+)/$', views.download, name='download_document'),
    path(r'^delete/(?P<project_id>[0-9]+)/$', views.delete_project, name='delete_project'),
    path(r'^delete/document/(?P<document_id>[0-9]+)/$', views.delete_document, name='delete_document'),
    path(r'^feedback/(?P<project_id>[0-9]+)/$', views.feedback, name='feedback'),

    # open for all
    path(r'^news/$', views.view_news, name='student_view_news_all'),
    path(r'^news/(?P<news_id>[0-9]*)/$', views.view_news, name='student_view_news'),
    path(r'^guidelines/$', views.guidelines, name='guidelines'),
    path(r'^bugs/$', views.bugs, name='bugs'),

    path(r'^update_batch_student/$', views.update_batch_student, name='update_batch_student'),

    path(r'^all_ngo/$', views.all_NGOs, name='all_NGO'),
    path(r'^suggest_ngo/$', views.suggest_NGO, name='suggest_ngo'),

    path(r'^allprojects/$',
        views.all_projects_open_to_public_year_select, name='all_projects_open_to_public_year_select'),
    path(r'^allprojects/(?P<year>[0-9]+)/$', views.all_projects_open_to_public,
        name='all_projects_open_to_public'),

    # example projects
    path(r'^examples/all/$', views.all_examples, name='student_all_examples'),
    path(r'^examples/(?P<example_id>[0-9]+)/$', views.view_example, name='view_example'),
    path(r'^like/(?P<example_id>[0-9]+)/$', views.like_project, name='like_project'),
    path(r'^unlike/(?P<example_id>[0-9]+)/$', views.unlike_project, name='unlike_project'),
    path(r'^comment/(?P<example_id>[0-9]+)/$', views.add_comment, name='add_comment'),
    path(r'^comment/delete/(?P<comment_id>[0-9]+)/$', views.delete_comment, name='delete_comment'),
)
