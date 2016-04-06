# About

This is an example project containing a number of mostly failed
attempts to test a Django Rest Framework API (v 3.3.3). This project
was generated using Django 1.9 but my main Django project is using
Django 1.8 because of the long term support so I moved back to using
Django 1.8 for the majority of my testing. Please see the
requirements.txt file for the exact versions I tested on.


# Testing Serializers with Custom Validate and Save Methods

In my main Django project, I have some nested
HyperlinkModelSerializers that control CRUD operations for some
interrelated models. My React component displays a single form for
editing all the related data and then submits it to the update
endpoint for the parent model. That serializer has a custom validate
method that parses the nested data and a custom update method that
saves updates to the parent and multiple child objects. Since there
are multiple child objects, I need to use the .getlist method to pull
all the children out of the request. This works fine when I post data
using AJAX in my app. But in my tests, I get an error message that
'dict' doesn't have a getlist method. It doesn't - but I should have a
QueryDict when I get to my view.

I created this project to figure out why my test's data comes in as a
dict. Is it a bug in Django Rest Framework's APIClient? or the
underlying Django Client? Based on the tests in this project, it
doesn't seem to be either of those. It must be something I am doing
wrong.

I took the following steps to try to narrow this down.

## Test a Django view with Django's Client

I created a basic html form with multiple checkboxes - not a Django
form object, just a hand coded html form (see
example/templates/example/index.html). Submit that to a view that does
'getlist' on the submitted data (see the index method in
example/views.py) and display the data. Playing with this in the
browser works. So now, create tests that submit to the same endpoint
(see example/tests/test_html_form.py). They all pass. So it isn't
Django's TestCase or Client that are at fault.

  ./manage.py test -v 2 example.tests.test_html_form

## Test a DRFview with DRF's APIClient

So to make something very small that might plausibly have a custom
update method, I used the stock User model + a Color model + a mapping
model, FavoriteColor which relates the two. The models ar in
example/models.py and the HyperlinkedModelSerializers in
example/serializers.py, and I used DRF's ModelViewSets with a few
custom views added. In the most basic test, I posted color + user to
the favoritecolor-list url and it created a new record. But it will
only create one record at a time - even if you try to send
multiples. So I created a custom view method, add_multiple, as an
additional list_route within the FavoriteColorViewSet. That uses the
same getlist method I was having trouble with in my tests. But in this
project, they all pass.

  ./manage.py test -v 2 example.tests.test_favorite_color_views

So DRF's APITestCase and APIClient are creating requests that pass
data into my view as a QueryDict. In fact, I can add an assert inside
the view, and everything still works:

   assert isinstance(request.data, QueryDict), 'request.data was not a QueryDict'

## Test a view that needs to deserialize JSON

  ./manage.py test -v 2 example.tests.test_user_serializer


# Testing CSRF protection

I have found a number of references to the fact that the CSRF
production machinery is disabled by default when using any of Django's
testing tools. It is really easy to find out how to turn this back on:
Client(enforce_csrf_checks=True) but I have yet to find a working
example of how to set up the request if you want to test with CSRF
protection enabled.

To see what I have tried so far, please see
example/tests/test_csrf_param.py The first two classes point out that
the DRF APIClient produces rather misleading output - the client
always says 'enforce_csrf_checks': False no matter how you initialize
your client. However, the _handler within the client gets the correct
configuration.

The last 2 tests in that file show my attempt to configure my test
client to either pass the csrf_token in the cookie or in an
HTTP-X-CSRFTOKEN header. 

To run these tests use: ./manage.py test example.tests.test_csrf_param


