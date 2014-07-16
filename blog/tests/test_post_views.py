from django.core.urlresolvers import reverse
from ndbtestcase import AppEngineTestCase

from blog.models import Post


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
