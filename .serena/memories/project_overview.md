# Stock Analysis Project Overview

## Project Purpose
Stock market analysis application with three user tiers (public, VIP/customer, admin).

## Tech Stack
**Frontend:**
- Vue 3 + TypeScript
- Vite
- Element Plus UI components
- Pinia (state management)
- Axios (HTTP client)

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite (dev) / PostgreSQL (prod)
- Pydantic (validation)

## Architecture
- Frontend: Three-tier routing system (public, client, admin pages)
- Backend: Service-oriented architecture (routers → services → models → database)
- Authentication: JWT token-based with role-based access control

## Key Features
- User management with role-based permissions (admin, vip, normal)
- Stock data and analysis
- Concept/sector analysis
- Rankings system
- Portfolio and performance analysis
- Subscription management system

## Database Key Tables
- users (with role-based access)
- subscriptions (with plans)
- stocks
- concepts
- rankings
