import pytest
from django.test import Client


@pytest.mark.django_db()
def test_index():
    c = Client()
    response = c.get("/")
    assert response.status_code == 200
