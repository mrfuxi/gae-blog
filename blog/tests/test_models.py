from ndbtestcase import AppEngineTestCase

from blog.models import Post


class TestPostModel(AppEngineTestCase):

    def test_post_by_slug(self):
        post = Post(title=u"New post")
        post.put()

        by_slug = Post.get_by_slug("new-post")

        self.assertEquals(by_slug, post)

    def test_post_by_slug_no_slug(self):
        by_slug = Post.get_by_slug(None)

        self.assertEquals(by_slug, None)

    def test_post_by_slug_incorrect_slug(self):
        by_slug = Post.get_by_slug("some-slug")

        self.assertEquals(by_slug, None)

    def test_post_by_slug_duplidate_post(self):
        Post(title=u"New post").put()
        Post(title=u"New post").put()

        by_slug = Post.get_by_slug("new-post")

        self.assertEquals(by_slug, None)
