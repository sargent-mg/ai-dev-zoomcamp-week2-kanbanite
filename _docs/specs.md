# Kanbanite — Mini Kanban Board Spec

## Overview
A single-user Kanban board web app with drag-and-drop card management across a fixed set of columns, built for AI Dev Tools Zoomcamp 2026 Week 2 (spec → frontend prototype → FastAPI backend → SQLite).

## Users
- **Single user**, no login/authentication required for v1

## Data Model
Three-level hierarchy:
- **Board** → **Columns** → **Cards**

### Columns
- Fixed set (not user-creatable/renamable/deletable in v1), e.g.: `To Do`, `In Progress`, `Done`

### Cards
- **Fields**: title, description
- **Operations**: create, edit, delete
- **Position**: manual reordering within a column (drag to reorder)
- **Movement**: drag-and-drop between columns

## Core Interactions
- Create a card in a column
- Edit a card's title/description
- Delete a card
- Drag a card to reorder it within its column
- Drag a card to move it to a different column

## Persistence
- Backend + database (not in-browser-only state)
- Board state survives across sessions/page refreshes

## Explicitly Out of Scope (v1)
- Multi-user / multi-board support
- User authentication/login
- Custom columns (create/rename/delete)
- Labels, tags, due dates
- Card comments/attachments

## Tech Stack
- **Backend**: FastAPI + SQLAlchemy (database-agnostic), swapped from mock store to SQLite per course workflow
- **Frontend**: Next.js + Tailwind CSS
- **Drag-and-drop**: `@dnd-kit` (modern, accessible, actively maintained)

## Naming
- **App name**: Kanbanite
- **Repo name**: `kanbanite-zoomcamp`
