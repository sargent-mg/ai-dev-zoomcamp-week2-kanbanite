const board = document.getElementById('kanban-board');
const modal = document.getElementById('card-modal');
const modalTitle = document.getElementById('modal-title');
const modalKicker = document.getElementById('modal-kicker');
const cardForm = document.getElementById('card-form');
const cardTitleInput = document.getElementById('card-title');
const cardDescriptionInput = document.getElementById('card-description');
const closeModalButton = document.getElementById('close-modal');
const cancelModalButton = document.getElementById('cancel-modal');
const deleteCardButton = document.getElementById('delete-card');
const resetBoardButton = document.getElementById('reset-board');

let currentBoard = KanbaniteApi.getBoard();
let currentCardId = null;
let currentColumnId = null;
let draggedCardId = null;

function createColumnMarkup(column) {
  const cards = column.cards.map(createCardMarkup).join('');

  return `<section class="column" data-column-id="${column.id}">
    <div class="column-header">
      <div class="column-title-wrap">
        <span class="column-title">${column.title}</span>
        <span class="column-count">${column.cards.length}</span>
      </div>
      <button class="add-card-button" data-add-card="${column.id}" aria-label="Create a card in ${column.title}">
        <span aria-hidden="true">+</span>
      </button>
    </div>
    <div class="cards" data-column-list="${column.id}">
      ${cards}
    </div>
  </section>`;
}

function createCardMarkup(card) {
  return `<article class="card" draggable="true" data-card-id="${card.id}" data-card-title="${escapeHtml(card.title)}">
    <div class="card-toolbar">
      <span class="card-grip" aria-label="Drag card">⋮⋮</span>
      <div class="card-actions">
        <button class="card-button edit-card" data-edit-card="${card.id}" aria-label="Edit card">Edit</button>
        <button class="card-button delete-card" data-delete-card="${card.id}" aria-label="Delete card">Delete</button>
      </div>
    </div>
    <div class="card-content">
      <h3>${escapeHtml(card.title)}</h3>
      <p>${escapeHtml(card.description || 'No description added yet.')}</p>
    </div>
  </article>`;
}

function renderBoard() {
  board.innerHTML = currentBoard.columns.map(createColumnMarkup).join('');
}

function openCreateCardModal(columnId) {
  currentCardId = null;
  currentColumnId = columnId;

  modalTitle.textContent = 'Create card';
  modalKicker.textContent = 'New card';
  deleteCardButton.classList.add('hidden');

  cardTitleInput.value = '';
  cardDescriptionInput.value = '';
  modal.classList.add('show');
  cardTitleInput.focus();
}

function openEditCardModal(cardId) {
  const card = findCard(cardId);
  if (!card) {
    return;
  }

  currentCardId = cardId;
  currentColumnId = findCardColumn(cardId).id;

  modalTitle.textContent = 'Edit card';
  modalKicker.textContent = 'Update card';
  deleteCardButton.classList.remove('hidden');

  cardTitleInput.value = card.title;
  cardDescriptionInput.value = card.description || '';
  modal.classList.add('show');
  cardTitleInput.focus();
}

function closeModal() {
  modal.classList.remove('show');
  currentCardId = null;
  currentColumnId = null;
}

function findCard(cardId) {
  for (const column of currentBoard.columns) {
    const card = column.cards.find((item) => item.id === cardId);
    if (card) {
      return card;
    }
  }

  return null;
}

function findCardColumn(cardId) {
  for (const column of currentBoard.columns) {
    const found = column.cards.find((item) => item.id === cardId);
    if (found) {
      return column;
    }
  }

  return null;
}

function saveCard(event) {
  event.preventDefault();

  const title = cardTitleInput.value.trim();
  const description = cardDescriptionInput.value.trim();

  if (!title) {
    cardTitleInput.focus();
    return;
  }

  if (currentCardId) {
    currentBoard = KanbaniteApi.updateCard(currentCardId, title, description);
  } else {
    currentBoard = KanbaniteApi.createCard(currentColumnId, title, description);
  }

  renderBoard();
  closeModal();
}

function deleteCardById(cardId) {
  const card = findCard(cardId);
  if (!card) {
    return;
  }

  currentBoard = KanbaniteApi.deleteCard(cardId);
  renderBoard();
  closeModal();
}

board.addEventListener('click', (event) => {
  const addButton = event.target.closest('[data-add-card]');
  if (addButton) {
    openCreateCardModal(addButton.dataset.addCard);
    return;
  }

  const editButton = event.target.closest('[data-edit-card]');
  if (editButton) {
    openEditCardModal(editButton.dataset.editCard);
    return;
  }

  const deleteButton = event.target.closest('[data-delete-card]');
  if (deleteButton) {
    deleteCardById(deleteButton.dataset.deleteCard);
  }
});

board.addEventListener('dragstart', (event) => {
  const card = event.target.closest('.card');
  if (!card) {
    return;
  }

  draggedCardId = card.dataset.cardId;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', draggedCardId);

  card.classList.add('dragging');
});

board.addEventListener('dragend', (event) => {
  const card = event.target.closest('.card');
  if (card) {
    card.classList.remove('dragging');
  }

  clearDropMarkers();
  draggedCardId = null;
});

board.addEventListener('dragover', (event) => {
  const list = event.target.closest('[data-column-list]');
  if (!list) {
    return;
  }

  event.preventDefault();
  clearDropMarkers();

  const cards = Array.from(list.querySelectorAll('.card'));
  const afterElement = getDragAfterElement(list, event.clientY, cards);
  const marker = createDropMarker();

  if (afterElement) {
    list.insertBefore(marker, afterElement);
  } else {
    list.appendChild(marker);
  }
});

board.addEventListener('drop', (event) => {
  const list = event.target.closest('[data-column-list]');
  if (!list) {
    return;
  }

  event.preventDefault();

  const targetColumnId = list.dataset.columnList;
  const cardId = draggedCardId || event.dataTransfer.getData('text/plain');
  const targetColumn = currentBoard.columns.find((column) => column.id === targetColumnId);
  const visibleCards = Array.from(list.querySelectorAll('.card'));

  let targetIndex = targetColumn.cards.length;

  for (const card of visibleCards) {
    const cardIndex = targetColumn.cards.findIndex((item) => item.id === card.dataset.cardId);
    if (cardIndex < 0) {
      continue;
    }

    const rect = card.getBoundingClientRect();

    if (event.clientY < rect.top + rect.height / 2) {
      targetIndex = cardIndex;
      break;
    }

    if (event.clientY < rect.bottom) {
      targetIndex = cardIndex + 1;
      break;
    }
  }

  currentBoard = KanbaniteApi.moveCard(cardId, targetColumnId, targetIndex);

  renderBoard();
  clearDropMarkers();
  draggedCardId = null;
});

cardForm.addEventListener('submit', saveCard);
closeModalButton.addEventListener('click', closeModal);
cancelModalButton.addEventListener('click', closeModal);

deleteCardButton.addEventListener('click', () => {
  if (currentCardId) {
    deleteCardById(currentCardId);
  }
});

resetBoardButton.addEventListener('click', () => {
  currentBoard = KanbaniteApi.reset();
  renderBoard();
});

function getDragAfterElement(list, y, cards) {
  let cardAfter = null;

  for (const card of cards) {
    const rect = card.getBoundingClientRect();
    if (y <= rect.top + rect.height / 2) {
      cardAfter = card;
      break;
    }
  }

  return cardAfter;
}

function createDropMarker() {
  const marker = document.createElement('div');
  marker.className = 'drop-marker';
  return marker;
}

function clearDropMarkers() {
  const markers = board.querySelectorAll('.drop-marker');
  markers.forEach((marker) => marker.remove());
}

function escapeHtml(value) {
  return String(value).replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

renderBoard();
