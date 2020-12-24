from django.conf.urls import url

from . import views

# fixing width at 78/79 messes up with code readability.

urlpatterns = (
    # basic
    url(r'^home/', views.home, name='studenthome'),
    url(r'^$', views.index, name='index'),
    url(r'^profile/$', views.profile, name='studentprofile'),

    # projects and documents
    url(r'^add/$', views.addproject, name='addproject'),
    url(r'^project/(?P<project_id>[0-9]+)/edit/$', views.editproject, name='editproject'),
    url(r'^project/(?P<project_id>[0-9]+)/upload/$', views._upload, name='upload_document'),
    url(r'^project/(?P<project_id>[0-9]+)/$', views.viewproject, name='viewproject'),
    url(r'^project/(?P<project_id>[0-9]+)/submit/$', views.submitproject, name='submitproject'),
    url(r'^project/(?P<project_id>[0-9]+)/NGO/$', views.view_project_NGO, name='view_project_NGO'),
    url(r'^link_ngo_project/(?P<NGO_id>[0-9]+)/(?P<project_id>[0-9]+)/$',
        views.link_NGO_project, name='link_NGO_project'),
    url(r'^unlink_ngo_project/(?P<project_id>[0-9]+)/$', views.unlink_NGO_project,
        name='unlink_ngo_project'),
    url(r'^download/(?P<document_id>[0-9]+)/$', views.download, name='download_document'),
    url(r'^delete/(?P<project_id>[0-9]+)/$', views.delete_project, name='delete_project'),
    url(r'^delete/document/(?P<document_id>[0-9]+)/$', views.delete_document, name='delete_document'),
    url(r'^feedback/(?P<project_id>[0-9]+)/$', views.feedback, name='feedback'),

    # open for all
    url(r'^news/$', views.view_news, name='student_view_news_all'),
    url(r'^news/(?P<news_id>[0-9]*)/$', views.view_news, name='student_view_news'),
    url(r'^guidelines/$', views.guidelines, name='guidelines'),
    url(r'^bugs/$', views.bugs, name='bugs'),

    url(r'^update_batch/$', views.update_batch, name='update_batch'),

    url(r'^all_ngo/$', views.all_NGOs, name='all_NGO'),
    url(r'^suggest_ngo/$', views.suggest_NGO, name='suggest_ngo'),

    url(r'^allprojects/$',
        views.all_projects_open_to_public_year_select, name='all_projects_open_to_public_year_select'),
    url(r'^allprojects/(?P<year>[0-9]+)/$', views.all_projects_open_to_public,
        name='all_projects_open_to_public'),

    # example projects
    url(r'^examples/all/$', views.all_examples, name='student_all_examples'),
    url(r'^examples/(?P<example_id>[0-9]+)/$', views.view_example, name='view_example'),
    url(r'^like/(?P<example_id>[0-9]+)/$', views.like_project, name='like_project'),
    url(r'^unlike/(?P<example_id>[0-9]+)/$', views.unlike_project, name='unlike_project'),
    url(r'^comment/(?P<example_id>[0-9]+)/$', views.add_comment, name='add_comment'),
    url(r'^comment/delete/(?P<comment_id>[0-9]+)/$', views.delete_comment, name='delete_comment'),
)
