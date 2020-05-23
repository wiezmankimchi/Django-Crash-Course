import pytest

from django.urls import reverse, resolve
from .factories import CheeseFactory

@pytest.fixture
def cheese():
    return CheeseFactory()

pytestmark  = pytest.mark.django.db

# when testing URL patterns, it's good to test forward and backwards:
# reversing the view name should giv the absolute URL
# resolving the absolute URL should give the view name

def test_list_reverse():
    # cheeses:list should revrese to '/cheeses/.'
    assert reverse('cheeses:list') == '/cheeses/'

def test_list_resolve():
    # '/cheeses/' should resolve to 'cheeses:list'
    assert resolve('/cheeses/').view_name == 'cheeses:list'

# test URL patterns
def test_add_reverse():
    # 'cheeses:add' should reverse to '/cheeses/add'
    assert resolve('/cheeses/add').view_name == 'cheeses:add'

# test the cheese detail URL pattern
# we will use the cheese fixture we have defined
def test_detail_reverse(cheese):
    # 'cheeses:detail' should reverse to '/cheese/cheeseslug/'
    url = reverse('cheeses:detail', kwargs={'slug': cheese.slug})
    assert url == f'/cheeses/{cheese.slug}/'

def test_details_resolve(cheese):
    # 'cheese/cheeseslug/' should resolve to 'cheeses:detail'
    url = f'/cheeses/{cheese.slug}'
    assert resolve(url).view_name = 'cheeses:detail'
