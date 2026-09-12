const KanbaniteApi = (() => {
  const API_BASE = 'http://127.0.0.1:8001';

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json'
      },
      ...options
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(payload.detail || 'Request failed');
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  return {
    async getBoard() {
      return request('/board');
    },

    async createCard(columnId, title, description) {
      return request('/board', {
        method: 'POST',
        body: JSON.stringify({
          column_id: columnId,
          title,
          description
        })
      });
    },

    async updateCard(cardId, title, description) {
      return request(`/cards/${cardId}`, {
        method: 'PUT',
        body: JSON.stringify({
          title,
          description
        })
      });
    },

    async deleteCard(cardId) {
      return request(`/cards/${cardId}`, {
        method: 'DELETE'
      });
    },

    async moveCard(cardId, targetColumnId, targetIndex) {
      return request(`/cards/${cardId}/move`, {
        method: 'PATCH',
        body: JSON.stringify({
          column_id: targetColumnId,
          position: targetIndex
        })
      });
    },

    async reset() {
      return request('/board/reset', {
        method: 'PATCH'
      });
    }
  };
})();
