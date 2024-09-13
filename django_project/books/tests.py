from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import Book, Review


class BookTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            username="review_user", email="review_user@email.com", password="Qwe123!@#"
        )

        cls.special_permission = Permission.objects.get(codename="special_status")

        cls.book = Book.objects.create(
            title="Harry Potter",
            author="JK Rowling",
            price="25.00",
        )

        cls.review = Review.objects.create(
            book=cls.book,
            author=cls.user,
            review="Should work",
        )

    def test_book_listing(self):
        self.assertEqual(self.book.title, "Harry Potter")
        self.assertEqual(self.book.price, "25.00")
        self.assertEqual(self.book.author, "JK Rowling")

    def test_book_list_view_for_logged_in_user(self):
        self.client.login(email="review_user@email.com", password="Qwe123!@#")
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Harry Potter")
        self.assertTemplateUsed(response, "books/book_list.html")

    def test_book_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "%s?next=/books/" % (reverse("account_login")))
        response = self.client.get("%s?next=/books/" % (reverse("account_login")))
        self.assertContains(response, "Log In")

    def test_book_detail_view(self):
        self.client.login(email="review_user@email.com", password="Qwe123!@#")
        self.user.user_permissions.add(self.special_permission)
        response = self.client.get(self.book.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        no_response = self.client.get("/books/12345/")
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Harry Potter")
        self.assertContains(response, "Should work")
        self.assertTemplateUsed(response, "books/book_detail.html")
