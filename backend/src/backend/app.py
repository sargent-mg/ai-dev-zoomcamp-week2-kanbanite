from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .mock_store import database

app = FastAPI(title='Kanbanite API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class Card(BaseModel):
    id: str
    title: str
    description: str


class Column(BaseModel):
    id: str
    title: str
    cards: list[Card]


class Board(BaseModel):
    columns: list[Column]


class CreateCardRequest(BaseModel):
    column_id: str
    title: str
    description: str = ''


class UpdateCardRequest(BaseModel):
    title: str
    description: str = ''


class MoveCardRequest(BaseModel):
    column_id: str
    position: int


@app.get('/board', response_model=Board)
def get_board():
    return database.get_board()


@app.patch('/board/reset', response_model=Board)
def reset_board():
    return database.reset()


@app.post('/board', response_model=Board, status_code=status.HTTP_201_CREATED)
def create_card(payload: CreateCardRequest):
    board = database.create_card(payload.column_id, payload.title, payload.description)
    if board is None:
        raise HTTPException(status_code=404, detail='Column not found')

    return board


@app.get('/cards/{card_id}', response_model=Card)
def get_card(card_id: str):
    card = database.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail='Card not found')

    return card


@app.put('/cards/{card_id}', response_model=Board)
def update_card(card_id: str, payload: UpdateCardRequest):
    board = database.update_card(card_id, payload.title, payload.description)
    if board is None:
        raise HTTPException(status_code=404, detail='Card not found')

    return board


@app.patch('/cards/{card_id}/move', response_model=Board)
def move_card(card_id: str, payload: MoveCardRequest):
    board = database.move_card(card_id, payload.column_id, payload.position)
    if board is None:
        raise HTTPException(status_code=404, detail='Card or column not found')

    return board


@app.delete('/cards/{card_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: str):
    removed = database.delete_card(card_id)
    if not removed:
        raise HTTPException(status_code=404, detail='Card not found')

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def main() -> None:
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8001)
