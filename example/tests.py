from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from django.core.urlresolvers import reverse
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
        

class ApiTests(APITestCase):

    def create_color(self, color_name):
        c = Color(name=color_name)
        c.full_clean()
        c.save()
        return c

    def setUp(self):
        self.user = User(username='someone')
        self.user.save()
        self.color_names = ['blue', 'green', 'yellow', 'orange', 'red']
        self.colors = [self.create_color(name) for name in self.color_names]
    
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
        
    def test_create_one_favorite_color_record_returns_that_record(self):
        user = reverse('user-detail', kwargs={'pk': self.user.id})
        color = reverse('color-detail', kwargs={'pk': self.colors[4].id})
        response = Client().post('/api/favs/', {'user': user, 'color': color})
        self.assertEqual(response.status_code, 201)
        self.assertCountEqual(list(response.data.keys()), ['url', 'user', 'color'])
        
    def test_create_multiple_favorite_color_records(self):
        '''This test works fine - the getlist is in the view.'''
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        response = APIClient().post('/api/favs/add_multiple/', {'username': self.user.username,
                                                                'choice': [self.colors[2].id, self.colors[0].id]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(FavoriteColor.objects.all()), 2)

        
class ApiWSaveMethodTests(APITestCase):

    def create_color(self, color_name):
        c = Color(name=color_name)
        c.full_clean()
        c.save()
        return c

    def setUp(self):
        self.user = User(username='someone', password='password')
        self.user.save()
        self.color_names = ['blue', 'green', 'yellow', 'orange', 'red']
        self.colors = [self.create_color(name) for name in self.color_names]
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.login(username=self.user.username, password='password')

        
    def test_create_multiple_favorite_color_records(self):
        '''This test hints an endpoint that uses a custom serializer save method.'''
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        response = self.client.post('/api/favs/record_favorites/', data={'username': self.user.username,
                                                                         'choice': [self.colors[2].id,
                                                                                    self.colors[0].id]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(FavoriteColor.objects.all()), 2)

