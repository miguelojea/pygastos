import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test to check that the main page can be loaded / and that it returns 200.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Lista de usuarios' in response.data
