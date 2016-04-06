from rest_framework.test import APITestCase, APIClient
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from ..models import Color, FavoriteColor
from pprint import pprint  # noqa


class ApiClientTests(APITestCase):

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
        client = APIClient()
        response = client.get(reverse('color-list'))
        self.assertEqual(response.status_code, 200)
        colors = [item['name'] for item in response.data]
        self.assertListEqual(colors, self.color_names)

    def test_show_favorite_colors(self):
        FavoriteColor(user=self.user, color=self.colors[2]).save()
        FavoriteColor(user=self.user, color=self.colors[0]).save()
        # favs = FavoriteColor.objects.all()
        response = APIClient().get(reverse('favoritecolor-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertCountEqual(list(response.data[0].keys()), ['url', 'user', 'color', 'color_name'])

    def test_create_one_favorite_color_record(self):
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        user = reverse('user-detail', kwargs={'pk': self.user.id})
        color = reverse('color-detail', kwargs={'pk': self.colors[4].id})
        response = APIClient().post(reverse('favoritecolor-list'), {'user': user, 'color': color})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(FavoriteColor.objects.all()), 1)

    def test_stock_viewset_will_only_create_one_favorite_color_record(self):
        '''
        I submitted two color urls, bit I only got a record for the last one
        '''
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        user = reverse('user-detail', kwargs={'pk': self.user.id})
        color1 = reverse('color-detail', kwargs={'pk': self.colors[4].id})
        color2 = reverse('color-detail', kwargs={'pk': self.colors[2].id})
        response = APIClient().post(reverse('favoritecolor-list'),
                                    {'user': user, 'color': [color1, color2]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(FavoriteColor.objects.all()), 1)
        self.assertEqual(FavoriteColor.objects.all()[0].color_id, self.colors[2].id)

    def test_create_multiple_favorite_color_records(self):
        '''This test works fine - the getlist is in the view.'''
        self.assertEqual(len(FavoriteColor.objects.all()), 0)
        response = APIClient().post(reverse('favoritecolor-add-multiple'),
                                    {'username': self.user.username,
                                     'choices': [self.colors[2].id, self.colors[0].id]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(FavoriteColor.objects.all()), 2)
