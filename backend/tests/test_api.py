import pytest
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    client.patch('/board/reset')
    yield
    client.patch('/board/reset')


def test_get_board_returns_seed_board():
    response = client.get('/board')

    assert response.status_code == 200
    data = response.json()
    assert 'columns' in data
    assert [column['id'] for column in data['columns']] == ['todo', 'progress', 'done']
    assert [len(column['cards']) for column in data['columns']] == [2, 1, 1]


def test_create_card_returns_201_and_updates_board():
    payload = {
        'column_id': 'todo',
        'title': 'New Card',
        'description': 'A created card'
    }

    response = client.post('/board', json=payload)

    assert response.status_code == 201
    data = response.json()
    created_column = next(column for column in data['columns'] if column['id'] == 'todo')
    assert any(card['title'] == 'New Card' and card['description'] == 'A created card' for card in created_column['cards'])


def test_get_card_returns_existing_card():
    response = client.get('/cards/card-1')

    assert response.status_code == 200
    data = response.json()
    assert data['id'] == 'card-1'
    assert data['title'] == 'Plan onboarding sequence'


def test_update_card_rewrites_title_and_description():
    response = client.put('/cards/card-1', json={
        'title': 'Updated title',
        'description': 'Updated description'
    })

    assert response.status_code == 200
    data = response.json()
    updated = next(card for column in data['columns'] for card in column['cards'] if card['id'] == 'card-1')
    assert updated['title'] == 'Updated title'
    assert updated['description'] == 'Updated description'


def test_move_card_returns_updated_board_with_new_column_and_position():
    response = client.patch('/cards/card-1/move', json={
        'column_id': 'progress',
        'position': 0
    })

    assert response.status_code == 200
    data = response.json()

    progress = next(column for column in data['columns'] if column['id'] == 'progress')
    assert progress['cards'][0]['id'] == 'card-1'

    todo = next(column for column in data['columns'] if column['id'] == 'todo')
    assert [card['id'] for card in todo['cards']] == ['card-2']


def test_delete_card_returns_204_and_removes_card():
    response = client.delete('/cards/card-2')

    assert response.status_code == 204

    board = client.get('/board')
    card_ids = [card['id'] for column in board.json()['columns'] for card in column['cards']]
    assert 'card-2' not in card_ids
