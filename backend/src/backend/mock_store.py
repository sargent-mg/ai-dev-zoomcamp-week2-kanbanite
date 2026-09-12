from copy import deepcopy


class MockKanbanStore:
    def __init__(self):
        self.board = {
            'columns': [
                {
                    'id': 'todo',
                    'title': 'To Do',
                    'cards': [
                        {'id': 'card-1', 'title': 'Plan onboarding sequence', 'description': 'Draft the first-run checklist for new customers.'},
                        {'id': 'card-2', 'title': 'Create design sprint brief', 'description': 'Capture scope, audience, and success metrics.'},
                    ],
                },
                {
                    'id': 'progress',
                    'title': 'In Progress',
                    'cards': [
                        {'id': 'card-3', 'title': 'Build landing page copy', 'description': 'Write headline, supporting paragraphs, and calls to action.'},
                    ],
                },
                {
                    'id': 'done',
                    'title': 'Done',
                    'cards': [
                        {'id': 'card-4', 'title': 'Validate backlog health', 'description': 'Review priorities and remove blocked work.'},
                    ],
                },
            ]
        }
        self.next_card_id = 5

    def get_board(self):
        return deepcopy(self.board)

    def get_card(self, card_id):
        for column in self.board['columns']:
            for card in column['cards']:
                if card['id'] == card_id:
                    return deepcopy(card)
        return None

    def create_card(self, column_id, title, description):
        column = next((item for item in self.board['columns'] if item['id'] == column_id), None)
        if column is None:
            return None

        card = {
            'id': f'card-{self.next_card_id}',
            'title': title,
            'description': description,
        }
        self.next_card_id += 1
        column['cards'].append(card)
        return deepcopy(self.board)

    def update_card(self, card_id, title, description):
        for column in self.board['columns']:
            for card in column['cards']:
                if card['id'] == card_id:
                    card['title'] = title
                    card['description'] = description
                    return deepcopy(self.board)
        return None

    def delete_card(self, card_id):
        for column in self.board['columns']:
            for index, card in enumerate(column['cards']):
                if card['id'] == card_id:
                    del column['cards'][index]
                    return True
        return False

    def move_card(self, card_id, column_id, position):
        card = None
        source_column = None
        source_index = -1

        for column in self.board['columns']:
            for index, item in enumerate(column['cards']):
                if item['id'] == card_id:
                    card = item
                    source_column = column
                    source_index = index
                    break
            if source_column:
                break

        if card is None:
            return None

        target_column = next((item for item in self.board['columns'] if item['id'] == column_id), None)
        if target_column is None:
            return None

        source_column['cards'].pop(source_index)
        safe_position = max(0, min(position, len(target_column['cards'])))
        target_column['cards'].insert(safe_position, card)

        return deepcopy(self.board)

    def reset(self):
        self.__init__()
        return deepcopy(self.board)


database = MockKanbanStore()
