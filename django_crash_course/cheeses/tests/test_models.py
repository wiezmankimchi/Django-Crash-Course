import pytest

from .factories import CheeseFactory
from ..models import Cheese

# connect the test with the database
pytestmark = pytest.mark.django_db

def test___str__():
    cheese = CheeseFactory()
    assert cheese.__str__() == cheese.name
    assert str(cheese)==cheese.name


