from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
import re

from lists.views import home_page
from lists.models import Item, List

# Create your tests here.
class HomePageTest(TestCase):

	@staticmethod
	def remove_csrf(html_code):
		csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
		return re.sub(csrf_regex, '', html_code)

	def assertEqualExceptCSRF(self, html_code1, html_code2):
		return self.assertEqual(self.remove_csrf(html_code1), self.remove_csrf(html_code2))

	def test_root_url_resolves_to_home_page_view(self):
		found = resolve('/')
		self.assertEqual(found.func, home_page)

	def test_home_page_returns_correct_html(self):
		request = HttpRequest()
		response = home_page(request)
		expected_html = render_to_string('home.html', request=request)
		self.assertEqualExceptCSRF(response.content.decode(), expected_html)

class ListAndItemModelsTest(TestCase):

	def test_saving_and_retrieving_items(self):
		list_local = List()
		list_local.save()

		first_item = Item()
		first_item.text = 'The first (ever) list item'
		first_item.list = list_local
		first_item.save()

		second_item = Item()
		second_item.text = 'Item the second'
		second_item.list = list_local
		second_item.save()

		saved_list = List.objects.first()
		self.assertEqual(saved_list, list_local)

		saved_items = Item.objects.all()
		self.assertEqual(saved_items.count(), 2)

		first_saved_item = saved_items[0]
		second_saved_item = saved_items[1]
		self.assertEqual(first_saved_item.text, 'The first (ever) list item')
		self.assertEqual(first_saved_item.list, list_local)
		self.assertEqual(second_saved_item.text, 'Item the second')
		self.assertEqual(second_saved_item.list, list_local)

class ListViewTest(TestCase):

	def test_uses_list_template(self):
		response = self.client.get('/lists/the-only-list-in-the-world/')
		self.assertTemplateUsed(response, 'list.html')

	def test_displays_all_items(self):
		list_ = List.objects.create()
		Item.objects.create(text='itemey 1', list=list_)
		Item.objects.create(text='itemey 2', list=list_)

		response = self.client.get('/lists/the-only-list-in-the-world/')

		self.assertContains(response, 'itemey 1')
		self.assertContains(response, 'itemey 2')

class NewListTest(TestCase):

	def test_saving_a_POST_request(self):
		self.client.post('/lists/new', data={'item_text': 'A new list item'})
		self.assertEqual(Item.objects.count(), 1)
		new_item = Item.objects.first()
		self.assertEqual(new_item.text, 'A new list item')

	def test_redirects_after_POST(self):
		response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/lists/the-only-list-in-the-world/')
		# book says to use assertRedirects() above but this test passed on my machine so left as is
