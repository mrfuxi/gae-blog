from django.conf.urls.defaults import url, patterns
from blog.views import HomeView, PostListView, PostView, LoginView, AboutMe


urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), {"login": True}, name='login'),
    url(r'^logout/$', LoginView.as_view(), {"login": False}, name='logout'),
    url(r'^blog/$', PostListView.as_view(), name='blog'),
    url(r'^blog/post/$', PostView.as_view(), name='new_post'),
    url(r'^blog/post/(?P<slug>[\w-]+)/$', PostView.as_view(), name='blog_post'),
    url(r'^about_me/$', AboutMe.as_view(), name='about_me'),
)
