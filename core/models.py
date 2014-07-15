from django.core.urlresolvers import reverse
from google.appengine.ext import ndb

try:
    # Slugify in Django 1.5+
    from django.utils.text import slugify
except ImportError:
    # Local copy
    from lib.slugify import slugify


class Post(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    author = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    slug = ndb.ComputedProperty(lambda self: slugify(self.title))

    @property
    def url(self):
        return reverse("blog_post", args=[self.slug])

    @classmethod
    def get_by_slug(cls, slug):
        if not slug:
            return None

        posts = cls.query(cls.slug == slug)
        if posts.count() != 1:
            return None

        return posts.fetch(1)[0]
