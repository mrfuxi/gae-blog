from django.core.urlresolvers import reverse
from ndbtestcase import AppEngineTestCase

from core.models import Post
# import unittest
from google.appengine.ext import ndb


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


class TestPostPage(AppEngineTestCase):

    def test_basic_post_data(self):
        post = Post()
        post.title = u"Some interesting post"
        post.body = "ABC" * 1000
        post.author = "Owner of blog"
        post.put()

        response = self.client.get(post.url)

        self.assertContains(response, post.title)
        self.assertContains(response, post.body)
        self.assertContains(response, "Written by Owner of blog")

    def test_unexitsing_post(self):
        response = self.client.get(reverse("blog_post", args=["a-slug"]))

        self.assertEquals(response.status_code, 404)

    def test_loggedin_user(self):
        self.users_login('someone@localhost', is_admin=False)
        post = Post(title=u"Post 1")
        post.put()

        response = self.client.get(post.url)

        self.assertNotContains(response, "Edit post")
        self.assertNotContains(response, "Delete")
        self.assertNotContains(response, "form")

    def test_loggedin_admin(self):
        self.users_login('owner@localhost', is_admin=True)
        post = Post(title=u"Post 1")
        post.put()

        response = self.client.get(post.url)

        self.assertContains(response, "Edit post")
        self.assertContains(response, "Delete")

        # form has no action url - post to it self
        self.assertNotContains(response, "action")


class TestCreatePostApi(AppEngineTestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = reverse("new_post")

    def test_admin_user(self):
        """
        Happy path:
        - Owner logged in
        - Short version of article in response (truncated body)
        - Post created as owner
        - Post actually saved :)
        """

        self.users_login('owner@localhost', is_admin=True)
        data = {
            "title": "some title",
            "body": "ABC " * 123,  # long body
        }

        expected_body = (
            "ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC "
            "ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC ABC "
            "ABC ABC A..."
        )

        response = self.client.post(self.url, data)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "some title")
        self.assertContains(response, expected_body)
        self.assertContains(response, "Written by owner@localhost")
        self.assertNotEquals(Post.get_by_slug("some-title"), None)

    def test_no_user(self):
        data = {
            "title": "some title",
            "body": "some body",
        }

        response = self.client.post(self.url, data)

        self.assertEquals(response.status_code, 403)

    def test_some_user(self):
        self.users_login('someone@localhost', is_admin=False)
        data = {
            "title": "some title",
            "body": "some body",
        }

        response = self.client.post(self.url, data)

        self.assertEquals(response.status_code, 403)

    def test_missing_title(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            "body": "some body",
        }

        response = self.client.post(self.url, data)

        self.assertContains(response, "Title is required", status_code=400)

    def test_missing_body(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            "title": "some title",
        }

        response = self.client.post(self.url, data)

        self.assertContains(response, "Body is required", status_code=400)

    def test_values_empty(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            "title": "",
            "body": "",
        }

        response = self.client.post(self.url, data)

        self.assertContains(response, "Title is required", status_code=400)
        self.assertContains(response, "Body is required", status_code=400)

    def test_values_missing(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            # Empty data
        }

        response = self.client.post(self.url, data)

        self.assertContains(response, "Title is required", status_code=400)
        self.assertContains(response, "Body is required", status_code=400)


class TestUpdatePostApi(AppEngineTestCase):

    def setUp(self):
        self.post = Post()
        self.post.title = u"Some interesting post"
        self.post.body = "some body"
        self.post.author = "Owner of blog"
        self.post.put()

    def test_no_user(self):
        data = {
            "title": "new title",
            "body": "new body",
        }

        response = self.client.post(self.post.url, data)

        self.assertEquals(response.status_code, 403)

    def test_some_user(self):
        self.users_login('someone@localhost', is_admin=False)
        data = {
            "title": "new title",
            "body": "new body",
        }

        response = self.client.post(self.post.url, data)

        self.assertEquals(response.status_code, 403)

    def test_admin_user(self):
        """
        Happy path:
        - Owner logged in
        - Full version of article in response
        - Post created as owner
        - Post actually updated (same timestamps)
        """

        self.users_login('owner2@localhost', is_admin=True)
        data = {
            "title": "new title",
            "body": "ABC" * 100,
        }

        response = self.client.post(self.post.url, data)
        updated_post = Post.get_by_slug("new-title")

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "new title")
        self.assertContains(response, "ABC" * 100)
        self.assertContains(response, "Written by owner2@localhost")
        self.assertEquals(updated_post.created_at, self.post.created_at)

    def test_admin_user_incorrect_url(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            "title": "new title",
            "body": "ABC",
        }

        response = self.client.post(
            reverse("blog_post", args=["some-slug"]), data)

        self.assertEquals(response.status_code, 404)

    def test_missing_body(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            "title": "some title",
        }

        response = self.client.post(self.post.url, data)

        self.assertContains(response, "Body is required", status_code=400)

    def test_values_empty(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            "title": "",
            "body": "",
        }

        response = self.client.post(self.post.url, data)

        self.assertContains(response, "Title is required", status_code=400)
        self.assertContains(response, "Body is required", status_code=400)

    def test_values_missing(self):
        self.users_login('owner@localhost', is_admin=True)
        data = {
            # Empty data
        }

        response = self.client.post(self.post.url, data)

        self.assertContains(response, "Title is required", status_code=400)
        self.assertContains(response, "Body is required", status_code=400)


class TestDeletePostApi(AppEngineTestCase):

    def setUp(self):
        self.post = Post(title=u"Some interesting post")
        self.post.put()

    def test_no_user(self):
        response = self.client.delete(self.post.url)

        self.assertEquals(response.status_code, 403)

    def test_some_user(self):
        self.users_login('someone@localhost', is_admin=False)

        response = self.client.delete(self.post.url)

        self.assertEquals(response.status_code, 403)

    def test_admin_user(self):
        """
        Happy path:
        - Owner logged in
        """

        self.users_login('owner@localhost', is_admin=True)

        del_response = self.client.delete(self.post.url)
        get_response = self.client.get(self.post.url)

        self.assertEquals(del_response.status_code, 204)
        self.assertEquals(get_response.status_code, 404)

    def test_admin_user_incorrect_url(self):
        self.users_login('owner@localhost', is_admin=True)

        response = self.client.delete(reverse("blog_post", args=["some-slug"]))

        self.assertEquals(response.status_code, 404)
