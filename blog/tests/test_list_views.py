from django.core.urlresolvers import reverse
from ndbtestcase import AppEngineTestCase

from blog.models import Post


class TestHomePage(AppEngineTestCase):

    @classmethod
    def setUpClass(cls):
        cls.url = reverse("home")

    def test_visible_posts(self):
        """
        On home page we need only latests posts
        """

        Post(title=u"Oldest post").put()
        Post(title=u"Post 2").put()
        Post(title=u"Post 3").put()
        Post(title=u"Post 4").put()

        response = self.client.get(self.url)

        self.assertNotContains(response, "Oldest post")
        self.assertContains(response, "Post 2")
        self.assertContains(response, "Post 3")
        self.assertContains(response, "Post 4")

    def test_body_of_post_is_truncated(self):
        post = Post(title=u"Long post")
        post.body = "ABC " * 123
        post.put()
        expected_body = (
            "ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC "
            "ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC "
            "ABC ABC A..."
        )

        response = self.client.get(self.url)
        self.assertContains(response, expected_body)

    def test_author_is_visible(self):
        Post(title=u"Post 1", author="Blog Owner").put()
        Post(title=u"Post 2", author="Blog Other Owner").put()

        response = self.client.get(self.url)

        self.assertContains(response, "Written by Blog Owner")
        self.assertContains(response, "Blog Other Owner")

    def test_link_to_post_present(self):
        post = Post(title=u"Post 1")
        post.put()

        response = self.client.get(self.url)

        self.assertContains(response, post.url)

    def test_no_user(self):
        Post(title=u"Post 1").put()

        response = self.client.get(self.url)

        self.assertNotContains(response, "Add post")
        self.assertNotContains(response, "Logout")
        self.assertNotContains(response, "form")
        self.assertContains(response, "Login")

    def test_loggedin_user(self):
        self.users_login('someone@localhost', is_admin=False)
        Post(title=u"Post 1").put()

        response = self.client.get(self.url)

        self.assertNotContains(response, "Add post")
        self.assertNotContains(response, "Login")
        self.assertNotContains(response, "form")
        self.assertContains(response, "Logout")

    def test_loggedin_admin(self):
        self.users_login('owner@localhost', is_admin=True)
        Post(title=u"Post 1").put()
        new_post_action = 'action="{}"'.format(reverse("new_post"))

        response = self.client.get(self.url)

        self.assertContains(response, "Add post")
        self.assertContains(response, "Logout")
        self.assertContains(response, "form")
        self.assertNotContains(response, "Login")

        # form has correct action
        self.assertContains(response, new_post_action)


class TestBlogPage(TestHomePage):
    """
    Blog page is very similar to home page,
    it should show more than just latest posts

    Remaining functionality should be the same
    """

    @classmethod
    def setUpClass(cls):
        cls.url = reverse("blog")

    def test_visible_posts(self):
        """
        On blog page show all posts
        """

        # choose titles that are predictible and easy to verify
        # ie not. "Post 1" because it would match "Post 10"
        titles = [
            u"Post -{}-".format(x) for x in xrange(15)
        ]

        for title in titles:
            Post(title=title).put()

        response = self.client.get(self.url)

        for title in titles:
            self.assertContains(response, title)
