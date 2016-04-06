from rest_framework.test import APITestCase, APIClient
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ..models import Color, FavoriteColor
from pprint import pprint


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
        self.myClient = APIClient(enforce_csrf_checks=True)
        self.myClient.login(username=self.user.username, password='password')

    def test_create_multiple_favorite_color_records(self):
        '''This test hints an endpoint that uses a custom serializer save method.'''
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        before = self.myClient.get('/api/users/{}/'.format(self.user.id))
        self.assertCountEqual(before.data['favorite_colors'], [])

        response = self.myClient.post('/api/users/record_favorite_colors/',
                                      data={'username': self.user.username,
                                            'first_name': 'Sheila',
                                            'choice': [self.colors[2].id, self.colors[0].id]})
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertCountEqual(response.data['favorite_colors'],
                              ['http://testserver/api/favs/1/', 'http://testserver/api/favs/3/'])
        # and edit
        response = self.myClient.post('/api/users/record_favorite_colors/',
                                      data={'username': self.user.username,
                                            'first_name': 'Sheila',
                                            'choice': [self.colors[3].id, self.colors[1].id]})
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertCountEqual(response.data['favorite_colors'],
                              ['http://testserver/api/favs/2/', 'http://testserver/api/favs/4/'])

    def test_api_view(self):
        '''This test hints an endpoint that uses a custom serializer save method.'''
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        before = self.myClient.get('/api/users/{}/'.format(self.user.id))
        self.assertCountEqual(before.data['favorite_colors'], [])
        url = reverse('update_favorite_colors')
        response = self.myClient.post(url, {'username': self.user.username,
                                            'first_name': 'Sheila',
                                            'choice': [self.colors[2].id, self.colors[0].id]})
        self.assertEqual(response.status_code, 200)
        pprint(response.data)
        self.assertCountEqual(response.data['favorite_colors'],
                                           ['http://testserver/api/favs/1/', 'http://testserver/api/favs/3/'])
