from django.test import TestCase, Client
from ..models import Color


class ExampleTestsWithDjangoClient(TestCase):

    def setUp(self):
        for color in ['blue', 'green', 'yellow', 'orange', 'red']:
            c = Color(name=color)
            c.full_clean()
            c.save()

    def test_request_without_form_data(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['data'], None)
        self.assertEqual(response.context['choices'], None)

    def test_request_with_form_submission(self):
        client = Client()
        response = client.post('/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['data'], None)
        self.assertEqual(response.context['choices'], None)

    def test_request_with_form_submitting_one_choice(self):
        client = Client()
        response = client.post('/', {'choice': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['choices'], ['2'])

    def test_request_with_form_submitting_three_choices_in_one_group(self):
        client = Client()
        response = client.post('/', {'choice': [2, 3, 4]})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['choices'], ['2', '3', '4'])

    def test_request_with_form_submitting_choices_in_two_groups_only_sees_the_last_one(self):
        client = Client()
        response = client.post('/', {'choice': 2, 'choice': 3})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['choices'], ['3'])
