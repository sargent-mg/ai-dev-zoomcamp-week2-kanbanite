from __future__ import annotations

import os
from typing import Protocol, Iterable

from sqlalchemy import create_engine, ForeignKey, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


class StoreProtocol(Protocol):
    def get_board(self) -> dict:
        ...

    def get_card(self, card_id: str):
        ...

    def create_card(self, column_id: str, title: str, description: str):
        ...

    def update_card(self, card_id: str, title: str, description: str):
        ...

    def delete_card(self, card_id: str) -> bool:
        ...

    def move_card(self, card_id: str, column_id: str, position: int):
        ...

    def reset(self):
        ...


class Base(DeclarativeBase):
    pass


class ColumnORM(Base):
    __tablename__ = 'columns'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cards: Mapped[list['CardORM']] = relationship(back_populates='column', cascade='all, delete-orphan')


class CardORM(Base):
    __tablename__ = 'cards'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default='')
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    column_id: Mapped[str] = mapped_column(String, ForeignKey('columns.id'), nullable=False)
    column: Mapped['ColumnORM'] = relationship(back_populates='cards')


class SQLAlchemyKanbanStore:
    """SQLAlchemy-backed repository for the Kanban API. The public API stays
    database-agnostic by matching the same methods as the previous mock store."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv('KANBANITE_DATABASE_URL', 'sqlite:///:memory:')
        self._is_sqlite_memory = self.database_url.startswith('sqlite:///:memory:')
        connect_args = {'check_same_thread': False} if self._is_sqlite_memory else {}
        poolclass = StaticPool if self._is_sqlite_memory else None
        self.engine = create_engine(self.database_url, connect_args=connect_args, poolclass=poolclass)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.next_card_id = 5
        self.seed()

    def seed(self):
        self.next_card_id = 5
        with self.session_factory() as session:
            session.query(CardORM).delete()
            session.query(ColumnORM).delete()
            session.commit()

            columns = [
                ColumnORM(id='todo', title='To Do', position=0),
                ColumnORM(id='progress', title='In Progress', position=1),
                ColumnORM(id='done', title='Done', position=2),
            ]
            session.add_all(columns)
            session.flush()

            cards = [
                CardORM(id='card-1', title='Plan onboarding sequence', description='Draft the first-run checklist for new customers.', position=0, column_id='todo'),
                CardORM(id='card-2', title='Create design sprint brief', description='Capture scope, audience, and success metrics.', position=1, column_id='todo'),
                CardORM(id='card-3', title='Build landing page copy', description='Write headline, supporting paragraphs, and calls to action.', position=0, column_id='progress'),
                CardORM(id='card-4', title='Validate backlog health', description='Review priorities and remove blocked work.', position=0, column_id='done'),
            ]
            session.add_all(cards)
            session.commit()

    def _board_from_session(self, session):
        columns = session.execute(select(ColumnORM).order_by(ColumnORM.position)).scalars().all()
        payload_columns = []
        for column in columns:
            cards = session.execute(select(CardORM).where(CardORM.column_id == column.id).order_by(CardORM.position)).scalars().all()
            payload_cards = [
                {
                    'id': card.id,
                    'title': card.title,
                    'description': card.description,
                }
                for card in cards
            ]
            payload_columns.append({
                'id': column.id,
                'title': column.title,
                'cards': payload_cards,
            })
        return {'columns': payload_columns}

    def get_board(self):
        with self.session_factory() as session:
            return self._board_from_session(session)

    def get_card(self, card_id: str):
        with self.session_factory() as session:
            card = session.get(CardORM, card_id)
            if card is None:
                return None
            return {
                'id': card.id,
                'title': card.title,
                'description': card.description,
            }

    def create_card(self, column_id: str, title: str, description: str):
        with self.session_factory() as session:
            column = session.get(ColumnORM, column_id)
            if column is None:
                return None

            card_id = f'card-{self.next_card_id}'
            self.next_card_id += 1
            card = CardORM(
                id=card_id,
                title=title,
                description=description,
                position=len(column.cards),
                column_id=column.id,
            )
            session.add(card)
            session.commit()
            return self._board_from_session(session)

    def update_card(self, card_id: str, title: str, description: str):
        with self.session_factory() as session:
            card = session.get(CardORM, card_id)
            if card is None:
                return None
            card.title = title
            card.description = description
            session.commit()
            return self._board_from_session(session)

    def delete_card(self, card_id: str) -> bool:
        with self.session_factory() as session:
            card = session.get(CardORM, card_id)
            if card is None:
                return False
            session.delete(card)
            session.commit()
            # Re-index positions in the same column after delete.
            column = session.get(ColumnORM, card.column_id)
            cards = session.execute(select(CardORM).where(CardORM.column_id == column.id).order_by(CardORM.position)).scalars().all()
            for index, item in enumerate(cards):
                item.position = index
            session.commit()
            return True

    def move_card(self, card_id: str, column_id: str, position: int):
        with self.session_factory() as session:
            card = session.get(CardORM, card_id)
            if card is None:
                return None
            target = session.get(ColumnORM, column_id)
            if target is None:
                return None

            source_column = session.get(ColumnORM, card.column_id)
            if source_column is None:
                return None

            source_cards = session.execute(select(CardORM).where(CardORM.column_id == source_column.id).order_by(CardORM.position)).scalars().all()
            target_cards = session.execute(select(CardORM).where(CardORM.column_id == target.id).order_by(CardORM.position)).scalars().all()

            # Remove from source list order in memory only via card.column_id change.
            card.column_id = target.id

            # Filter out the moving card from target ordering, then insert at requested position.
            remaining = [item for item in target_cards if item.id != card.id]
            safe_position = max(0, min(position, len(remaining)))
            remaining.insert(safe_position, card)

            # Reassign the new positions of the target column.
            for idx, item in enumerate(remaining):
                item.position = idx

            # Re-index source column positions after removal of the moved card.
            source_remaining = [item for item in source_cards if item.id != card.id]
            for idx, item in enumerate(source_remaining):
                item.position = idx

            session.commit()
            return self._board_from_session(session)

    def reset(self):
        self.seed()
        return self.get_board()


database = SQLAlchemyKanbanStore()
