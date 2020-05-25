import pytest
from pytest_django.asserts import (assertContains, assertRedirects)
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

# imports fro the current project
from django_crash_course.users.models import User
from ..models import Cheese
from ..views import (
    CheeseCreateView,
    CheeseListView,
    CheeseDetailView,
    CheeseUpdateView
)
from .factories import CheeseFactory, cheese

# connecting the tests to the db
pytestmark = pytest.mark.django_db

# test the Cheese List View
def test_good_cheese_list_view_expanded(rf):
    # Determine the URL
    url = reverse("cheeses:list")
    # rf is pytest chortcut to django.test.RequestFacotry
    # we generate a request as if from a user accessing
    # the cheese list view
    request = rf.get(url)
    # Call as_view() to make a callable object
    # callable_obj is analogous to a function-based view
    callable_obj = CheeseListView.as_view()
    # Pass in the request into the callable_obj to get an
    #  HTTP response served up by Django
    response = callable_obj(request)
    # Test that the HTTP response has 'Cheese List' in the
    #  HTML and has a 200 response code
    assertContains(response, 'Cheese List')

# A sherter version of the test above
def test_good_cheese_list_view(rf):
    # get the request
    request = rf.get(reverse("cheeses:list"))
    # Use the request to get the response
    response = CheeseListView.as_view()(request)
    # Test the response
    assertContains(response, 'Cheese List')

# to test the detail view, we create a new cheese, and then
# call the detail view with the new create cheese as a slug
# then check if the new name exists on the result
def test_good_cheese_detail_view(rf, cheese):
    # order some cheese from the CheeseFactory
    # cheese = CheeseFactory()
    # we are using the cheese fixture that is defined in 'factories.py'
    # make a request for our new cheese
    url = reverse('cheeses:detail', kwargs={'slug':cheese.slug})
    request =rf.get(url)

    # use the request to get the response
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # Test that the response is valid
    assertContains(response, cheese.name)

# To test the create new cheese we need to create a new user
# then login with that user, as the create cheese is restricted
def test_good_cheese_create_view(rf, admin_user, cheese):
    #order some cheese from the CheeseFactory
     # cheese = CheeseFactory()
    # we are using the cheese fixture that is defined in 'factories.py'
    # make a request for the new cheese
    request = rf.get(reverse("cheeses:add"))
    # add an authenticated user
    request.user = admin_user
    # use the request to get the response
    response = CheeseCreateView.as_view()(request)
    #Test the response
    assert response.status_code == 200

# test the cheese list view for more than one cheese added
def test_cheese_list_contains_2_cheeses(rf):
    # create a couple of cheeses
    cheese1 = CheeseFactory()
    cheese2 = CheeseFactory()
    # create a request and then a response for a list of cheeses
    request = rf.get(reverse('cheeses:list'))
    response = CheeseListView.as_view()(request)
    # Assert that the response contains both cheeses
    assertContains(response, cheese1.name)
    assertContains(response, cheese2.name)

# test the detail view for 1 object and the content it contains
def test_detail_contains_cheese_data(rf, cheese):
     # cheese = CheeseFactory()
    # we are using the cheese fixture that is defined in 'factories.py'
    # make a request to the new cheese
    url = reverse('cheeses:detail', kwargs={'slug':cheese.slug})
    request = rf.get(url)
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # check the cheese details
    assertContains(response, cheese.name)
    assertContains(response, cheese.get_firmness_display())
    assertContains(response, cheese.country_of_origin.name)

# test the create view: upon POST the view should redirect to the
# detail page of the created cheese. The creator of the cheese should
# be a user who has logged in and the submitted the cheese
def test_cheese_create_form_valid(rf, admin_user):
    # submit the cheese add for
    form_data = {
        'name':'Paski Sir',
        'description': 'A salty hard cheese',
        'firmness': Cheese.Firmness.HARD
    }
    request = rf.post(reverse('cheeses:add'), form_data)
    request.user = admin_user
    response = CheeseCreateView.as_view()(request)

    # get the cheese based on the name
    cheese = Cheese.objects.get(name='Paski Sir')

    # test that the cheese matches the form
    assert cheese.description == 'A salty hard cheese'
    assert cheese.firmness == Cheese.Firmness.HARD
    assert cheese.creator == admin_user

# Test the update/add form for both options
# This test checks that the web page corresponding to
# CheeseCreateView contains the string Add Cheese.
def test_cheese_create_correct_title(rf, admin_user):
    # Page title or CheeseCreateView shuld be Add Cheese
    request = rf.get(reverse('cheeses:add'))
    request.user = admin_user
    response = CheeseCreateView.as_view()(request)
    assertContains(response, 'Add Cheese')

# Test that CreateUpdateView is a good view
def test_good_cheese_update_view(rf, admin_user, cheese):
    url=reverse('cheeses:update', kwargs={'slug':cheese.slug})
    # make a request for the new cheese
    request = rf.get(url)
    # add an authenticated user
    request.user = admin_user
    # use the request to get the response
    callable_obj=CheeseUpdateView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # Test that the response is valid
    assertContains(response, 'Update Cheese')

# Test that the update was done correctly
def test_cheesse_update(rf, admin_user, cheese):
    # POST request to CheeseUpdateView updates a cheese and redirects
    # Make  request for the new cheese
    form_data = {
        'name': cheese.name,
        'description': 'Somthing New', # this is the updated value
        'firmness': cheese.firmness
    }
    url = reverse('cheeses:update', kwargs={'slug':cheese.slug})
    request = rf.post(url, form_data)
    request.user = admin_user
    callable_obj = CheeseUpdateView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # check that the cheese have been changed
    cheese.refresh_from_db()
    assert cheese.description=='Somthing New'
