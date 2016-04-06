from django.test import TestCase, Client
from django.middleware import csrf
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from ..models import Color
from pprint import pprint  # noqa


class ApiTestCaseTests(APITestCase):

    def test_csrf_setup(self):
        '''
        Note the weirdness of what is reported for enforce_csrf_checks. If you inspect the client,
        it ALWAYS says 'False', whether or not you pass 'enforce_csrf_checks=True'. But if you inspect
        the handler that it creates, that changes depending on the value of 'enforce_csrf_checks'.
        '''
        thisClient = APIClient(enforce_csrf_checks=True)  # noqa
        # print('Client:')
        # pprint(thisClient.__dict__)
        # print('Handler:')
        # pprint(thisClient.handler.__dict__)

        # ## output is:
        #
        # Client:
        # {'_credentials': {},
        #  'cookies': <SimpleCookie: >,
        #  'defaults': {},
        #  'enforce_csrf_checks': False,
        #  'errors': <_io.BytesIO object at 0x1038fc7d8>,
        #  'exc_info': None,
        #  'handler': <rest_framework.test.ForceAuthClientHandler object at 0x103908ba8>,
        #  'renderer_classes': {'json': <class 'rest_framework.renderers.JSONRenderer'>,
        #                       'multipart': <class 'rest_framework.renderers.MultiPartRenderer'>}}
        # Handler:
        # {'_exception_middleware': None,
        #  '_force_token': None,
        #  '_force_user': None,
        #  '_request_middleware': None,
        #  '_response_middleware': None,
        #  '_template_response_middleware': None,
        #  '_view_middleware': None,
        #  'enforce_csrf_checks': True}

        # #####################################
        # clientWoCSRF = APIClient()
        # print('Client:')
        # pprint(clientWoCSRF.__dict__)
        # print('Handler:')
        # pprint(clientWoCSRF.handler.__dict__)

        # Client:
        # {'_credentials': {},
        #  'cookies': <SimpleCookie: >,
        #  'defaults': {},
        #  'enforce_csrf_checks': False,
        #  'errors': <_io.BytesIO object at 0x10f9fa938>,
        #  'exc_info': None,
        #  'handler': <rest_framework.test.ForceAuthClientHandler object at 0x10fa04e10>,
        #  'renderer_classes': {'json': <class 'rest_framework.renderers.JSONRenderer'>,
        #                       'multipart': <class 'rest_framework.renderers.MultiPartRenderer'>}}
        # Handler:
        # {'_exception_middleware': None,
        #  '_force_token': None,
        #  '_force_user': None,
        #  '_request_middleware': None,
        #  '_response_middleware': None,
        #  '_template_response_middleware': None,
        #  '_view_middleware': None,
        #  'enforce_csrf_checks': False}


class DjangoTests(TestCase):

    def test_csrf_setup(self):
        '''
        In the Django client, the Client doesn't have an attribute for enforce_csrf_checks,
        it only appears in the handler.
        '''
        djangoClient = Client(enforce_csrf_checks=True)  # noqa
        # print('Client:')
        # pprint(djangoClient.__dict__)
        # print('Handler:')
        # pprint(djangoClient.handler.__dict__)

        # ## output is:
        #
        # Client:
        # {'cookies': <SimpleCookie: >,
        #  'defaults': {},
        #  'errors': <_io.BytesIO object at 0x10810af10>,
        #  'exc_info': None,
        #  'handler': <django.test.client.ClientHandler object at 0x106f9c588>}
        # Handler:
        # {'_exception_middleware': None,
        #  '_request_middleware': None,
        #  '_response_middleware': None,
        #  '_template_response_middleware': None,
        #  '_view_middleware': None,
        #  'enforce_csrf_checks': True}

    def create_color(self, color_name):
        c = Color(name=color_name)
        c.full_clean()
        c.save()
        return c

    def get_or_create_csrf_token(request):
        token = request.META.get('CSRF_COOKIE', None)
        if token is None:
            token = csrf._get_new_csrf_key()
            request.META['CSRF_COOKIE'] = token
        request.META['CSRF_COOKIE_USED'] = True
        return token

    def test_enforce_csrf_works_with_token_in_cookie(self):
        '''
        I can't figure out how to set up a request with a proper CSRF token.
        I think I need the same token in the posted data AND in either a request
        header or in the cookies.

        In this test I am trying to set it in the cookie for the authorized session.
        I do see it in client.cookies - but I am NOT seeing authenication info
        in the cookie, which makes me doubt the validity of the code. And it doesn't work.
        '''
        # first set up some model instances we need
        user = User.objects.create_user(username='someone', password='password')
        for name in ['blue', 'green', 'yellow', 'orange', 'red']:
            self.create_color(name)

        client = Client(enforce_csrf_checks=True)
        print('before login')
        print(self.client.cookies)
        client.login(username=user.username, password='password')

        print('after login')
        print(self.client.cookies)

        token = csrf._get_new_csrf_key()
        self.client.cookies['csrftoken'] = token
        print('after setting token')
        print(self.client.cookies)

        response = client.post('/', {'username': user.username, 'choice': 2, 'csrfmiddlewaretoken': token})
        self.assertEqual(response.status_code, 200)

    def test_enforce_csrf_works_with_token_in_header(self):
        '''
        I can't figure out how to set up a request with a proper CSRF token.
        I think I need the same token in the posted data AND in either a request
        header or in the cookies.

        In this test I am trying to set it in the request headers per the docs:
        https://docs.djangoproject.com/en/1.8/ref/csrf/#ajax
        '''
        # first set up some model instances we need
        user = User.objects.create_user(username='someone', password='password')
        for name in ['blue', 'green', 'yellow', 'orange', 'red']:
            self.create_color(name)

        token = csrf._get_new_csrf_key()
        client = Client(enforce_csrf_checks=True, HTTP_X_CSRFTOKEN=token)
        pprint(client.__dict__)
        response = client.post('/', {'username': user.username, 'choice': 2, 'csrfmiddlewaretoken': token})
        pprint(response.__dict__)
        self.assertEqual(response.status_code, 200)
