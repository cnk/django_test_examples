from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Color, FavoriteColor


class ExampleTests(TestCase):

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

    def test_request_with_form_submitting_two_choices_in_one_group(self):
        client = Client()
        response = client.post('/', {'choice': [2, 3, 4]})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['choices'], ['2', '3', '4'])

    def test_request_with_form_submitting_choices_in_two_groups_only_sees_the_last_one(self):
        client = Client()
        response = client.post('/', {'choice': 2, 'choice': 3})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['choices'], ['3'])
        

class ApiTests(TestCase):

    def setUp(self):
        self.user = User(username='someone')
        self.user.save()
        self.colors = []
        self.color_names = ['blue', 'green', 'yellow', 'orange', 'red']
        for color in self.color_names:
            c = Color(name=color)
            c.full_clean()
            c.save()
            self.colors.append(c)
    
    def test_color_list_shows_all_colors(self):
        client = Client()
        response = client.get('/api/colors/')
        self.assertEqual(response.status_code, 200)
        colors = [item['name'] for item in response.data]
        self.assertListEqual(colors, self.color_names)

    def test_show_favorite_colors(self):
        FavoriteColor(user=self.user, color=self.colors[2]).save()
        FavoriteColor(user=self.user, color=self.colors[0]).save()
        favs = FavoriteColor.objects.all()
        response = Client().get('/api/favs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertCountEqual(list(response.data[0].keys()), ['url', 'user', 'color'])
        
