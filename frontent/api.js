const KanbaniteApi = (() => {
  const initialBoard = {
    columns: [
      {
        id: 'todo',
        title: 'To Do',
        cards: [
          {
            id: 'card-1',
            title: 'Plan onboarding sequence',
            description: 'Draft the first-run checklist for new customers.'
          },
          {
            id: 'card-2',
            title: 'Create design sprint brief',
            description: 'Capture scope, audience, and success metrics.'
          }
        ]
      },
      {
        id: 'progress',
        title: 'In Progress',
        cards: [
          {
            id: 'card-3',
            title: 'Build landing page copy',
            description: 'Write headline, supporting paragraphs, and calls to action.'
          }
        ]
      },
      {
        id: 'done',
        title: 'Done',
        cards: [
          {
            id: 'card-4',
            title: 'Validate backlog health',
            description: 'Review priorities and remove blocked work.'
          }
        ]
      }
    ]
  };

  let board = cloneBoard(initialBoard);

  function cloneBoard(input) {
    return JSON.parse(JSON.stringify(input));
  }

  function findCard(cardId) {
    for (const column of board.columns) {
      const card = column.cards.find((item) => item.id === cardId);
      if (card) {
        return { card, column };
      }
    }

    return null;
  }

  return {
    getBoard() {
      return cloneBoard(board);
    },

    createCard(columnId, title, description) {
      const column = board.columns.find((item) => item.id === columnId);
      if (!column) {
        return cloneBoard(board);
      }

      const id = `card-${Date.now()}-${Math.round(Math.random() * 1000)}`;
      column.cards.push({ id, title, description });

      return cloneBoard(board);
    },

    updateCard(cardId, title, description) {
      const found = findCard(cardId);
      if (!found) {
        return cloneBoard(board);
      }

      found.card.title = title;
      found.card.description = description;

      return cloneBoard(board);
    },

    deleteCard(cardId) {
      for (const column of board.columns) {
        const cardIndex = column.cards.findIndex((item) => item.id === cardId);
        if (cardIndex >= 0) {
          column.cards.splice(cardIndex, 1);
          break;
        }
      }

      return cloneBoard(board);
    },

    moveCard(cardId, targetColumnId, targetIndex) {
      const found = findCard(cardId);
      if (!found) {
        return cloneBoard(board);
      }

      const { card } = found;
      const sourceColumn = found.column;
      const sourceIndex = sourceColumn.cards.findIndex((item) => item.id === cardId);
      const targetColumn = board.columns.find((column) => column.id === targetColumnId);

      if (!targetColumn) {
        return cloneBoard(board);
      }

      sourceColumn.cards.splice(sourceIndex, 1);

      const sameColumnReorder = sourceColumn.id === targetColumn.id && sourceIndex < targetIndex;
      const normalizedIndex = sameColumnReorder
        ? Math.max(0, targetIndex - 1)
        : targetIndex;

      const safeIndex = Math.max(0, Math.min(normalizedIndex, targetColumn.cards.length));
      targetColumn.cards.splice(safeIndex, 0, card);

      return cloneBoard(board);
    },

    reset() {
      board = cloneBoard(initialBoard);
      return cloneBoard(board);
    }
  };
})();
