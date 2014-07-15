import itertools

from django.core.urlresolvers import reverse
from django.http import (
    Http404, HttpResponse, HttpResponseRedirect,
    HttpResponseForbidden, HttpResponseBadRequest
)
from django.views.generic import ListView, View
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from google.appengine.api import users

from core.models import Post, slugify
from core.forms import PostForm


class UserMixin(object):
    admin_required = False

    def get_context_data(self, **kwargs):
        context = kwargs

        context.update({
            "user_logged_in": users.get_current_user(),
            "is_admin": users.is_current_user_admin(),
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if self.admin_required and not users.is_current_user_admin():
            return HttpResponseForbidden()

        return super(UserMixin, self).dispatch(request, *args, **kwargs)


class PostListView(UserMixin, ListView):
    template_name = "post_list.html"
    queryset = Post.query().order(-Post.created_at)

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context["posts"] = self.object_list
        context["form"] = PostForm()

        return context


class HomeView(UserMixin, ListView):
    template_name = "home.html"
    queryset = Post.query().order(-Post.created_at)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["posts"] = self.object_list.fetch(3)
        context["form"] = PostForm()

        return context


class PostView(UserMixin, TemplateResponseMixin, View):
    template_name = "posts/view.html"

    def get_object(self):
        slug = self.kwargs.get("slug")
        return Post.get_by_slug(slug)

    def get_template_names(self):
        if self.request.method == "POST":
            return ["posts/post.html"]

        return super(PostView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        context.update({
            "post": kwargs.get("post"),
            "form": PostForm(),
        })

        return context

    def get(self, request, slug=None, *args, **kwargs):
        self.object = self.get_object()

        if not self.object:
            raise Http404()

        context = self.get_context_data(post=self.object)
        return self.render_to_response(context)

    def post(self, request, slug=None, *args, **kwargs):
        if not users.is_current_user_admin():
            return HttpResponseForbidden()

        post = self.get_object()
        if not post and slug:
            raise Http404()

        form = PostForm(request.POST)
        if not form.validate():
            error_msg = [
                "There are problems with the form:",
            ]
            error_msg = itertools.chain(error_msg, *form.errors.values())

            return HttpResponseBadRequest("<br/>".join(error_msg))

        # title has to exit at that point due to the validators
        new_slug = slugify(form.data["title"])
        if slug is None and Post.get_by_slug(new_slug):
            return HttpResponseBadRequest("Post with this title alread exit")

        created = False
        if not post:
            created = True
            post = Post()

        form.populate_obj(post)
        post.author = users.get_current_user().nickname()
        post.put()

        context = self.get_context_data(post=post, short=created)
        return self.render_to_response(context)

    def delete(self, request, slug, *args, **kwargs):
        if not users.is_current_user_admin():
            return HttpResponseForbidden()

        post = self.get_object()
        if not post:
            raise Http404()

        post.key.delete()
        post.key.delete(use_datastore=False)

        return HttpResponse(status=204)


class PostFormView(UserMixin, TemplateResponseMixin, View):
    template_name = "posts/form.html"
    admin_required = True

    http_method_names = ["get", "post"]

    def get_object(self):
        return Post.get_by_slug(self.kwargs.get("slug"))

    def get_context_data(self, **kwargs):
        context = super(PostFormView, self).get_context_data(**kwargs)

        form = PostForm(obj=kwargs.get("post"))

        context.update({
            "form": form,
        })

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(post=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        pass


class LoginView(View):
    admin_required = False

    def get(self, request, login):
        redirect_url = reverse('home')

        if login:
            url = users.create_login_url(redirect_url)
        else:
            url = users.create_logout_url(redirect_url)

        return HttpResponseRedirect(url)


class AboutMe(TemplateView):
    template_name = "about_me.html"
