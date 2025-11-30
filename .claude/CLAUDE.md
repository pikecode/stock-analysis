# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Frontend (Vue 3 + Vite + Element Plus)
```bash
cd frontend
npm install                    # First time setup
npm run dev                    # Start dev server (http://127.0.0.1:3000)
npm run build                  # Production build
npm run preview               # Preview built app
npm run lint                  # Fix ESLint issues
```

### Backend (FastAPI + SQLAlchemy)
```bash
cd backend
pip install -r requirements.txt    # First time setup
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# API documentation: http://127.0.0.1:8000/docs (Swagger)

# Database initialization (first time)
python scripts/init_db.py
python scripts/admin_setup.py

# Run tests
pytest
pytest tests/test_auth.py::test_login  # Single test

# Code formatting
black .
isort .
flake8 .
```

### Celery Async Tasks (Optional)
```bash
# Start Redis (required for Celery)
redis-server

# Start Celery worker
celery -A tasks.celery_app worker --loglevel=info
```

## Production Deployment

### 🚀 When User Says: "部署生产环境" or "更新代码到服务器"

Execute the following automated deployment process:

#### Quick Update (Most Common)
```bash
cd deploy/scripts
./update-production.sh
```

This script automatically:
- ✅ Backs up database and current code
- ✅ Uploads latest code to server
- ✅ Updates Python/Node dependencies
- ✅ Rebuilds frontend
- ✅ Restarts all services
- ✅ Verifies deployment success

**Estimated time:** 2-3 minutes

#### Partial Updates
```bash
# Backend only (30-60 seconds)
./update-backend.sh

# Frontend only (30-60 seconds)
./update-frontend.sh
```

### Production Environment Info
- **URL:** https://qwquant.com
- **API Docs:** https://qwquant.com/api/docs
- **Server:** 82.157.28.35 (Ubuntu 20.04)
- **User:** ubuntu
- **Password:** chen_188_8_8
- **Project Path:** /var/www/stock-analysis
- **Database:** stock_analysis (PostgreSQL)

### Deployment Triggers
Recognize these user phrases and execute deployment:
- "部署生产环境" / "部署到生产环境"
- "更新代码到服务器" / "更新生产环境"
- "执行生产部署" / "发布到线上"
- "deploy to production" / "update production"

### Critical: Python 3.8 Compatibility
Server runs Python 3.8. Update scripts automatically fix type annotations:
```python
# ❌ Won't work on Python 3.8
def get_items() -> list[Item]: pass

# ✅ Auto-converted to
from __future__ import annotations
from typing import List
def get_items() -> List[Item]: pass
```

### Quick Rollback (If Issues Occur)
```bash
ssh ubuntu@82.157.28.35
cd /var/www/stock-analysis

# Rollback backend
sudo systemctl stop stock-analysis-backend
rm -rf backend && mv backend.backup backend
sudo systemctl start stock-analysis-backend

# Rollback frontend
cd frontend
rm -rf dist && mv dist.backup dist
sudo systemctl reload nginx
```

### Deployment Documentation
- **Quick Reference:** `deploy/QUICK-START.md` ⭐ Most useful
- **Complete Guide:** `deploy/docs/DEPLOYMENT.md`
- **Update Guide:** `deploy/docs/UPDATE-GUIDE.md`
- **Deployment History:** `deploy/docs/DEPLOYMENT-SUMMARY.md`

### Service Management Commands
```bash
# Check status
ssh ubuntu@82.157.28.35
sudo systemctl status stock-analysis-backend
sudo systemctl status nginx

# View logs
sudo journalctl -u stock-analysis-backend -f
sudo tail -f /var/log/nginx/qwquant_error.log

# Restart services
sudo systemctl restart stock-analysis-backend
sudo systemctl reload nginx
```

## Project Architecture

### Frontend: Three-Tier Routing System

The frontend has three separate user tiers with different permissions:

```
Public Pages (no login required)
  ├── Home page (HomePage.vue)
  ├── Stock list/detail (PublicStockList.vue, PublicStockDetail.vue)
  ├── Concept analysis (PublicConceptList.vue, PublicConceptDetail.vue)
  ├── Rankings (PublicRankingView.vue)
  └── Login/Admin login pages

Client Pages (customer login required)
  ├── Reports (Dashboard.vue, ConceptStockRanking.vue, etc.)
  ├── Analysis (PortfolioAnalysis.vue, PerformanceAnalysis.vue)
  └── Profile (UserProfile.vue, UserSettings.vue)

Admin Pages (admin role required)
  ├── Dashboard
  ├── Stock management
  ├── Concept management
  ├── User management
  ├── Data import
  └── System settings
```

**Router Location:** `frontend/src/router/index.ts` (contains authentication guard and role validation)

### Backend: Service-Oriented Architecture

```
API Routes (app/routers/)
    ↓
Services (app/services/) - Business logic
    ↓
Models (app/models/) - SQLAlchemy ORM
    ↓
Database (SQLite for dev, PostgreSQL for production)
```

**Key Layers:**
- **Models** (`app/models/`) - User, Stock, Concept, Ranking, Role, Permission
- **Schemas** (`app/schemas/`) - Pydantic validation models
- **Services** (`app/services/`) - Business logic (stock_service, user_service, etc.)
- **Routers** (`app/routers/`) - API endpoints under `/api/v1/`
- **Auth** (`app/core/security.py`) - JWT token management, password hashing

### Authentication & Authorization

**Flow:**
1. User logs in → `POST /api/v1/auth/login` returns JWT token
2. Token stored in localStorage (frontend)
3. Frontend includes token in Authorization header for all API requests
4. Backend validates JWT in dependency injection (`dependencies/auth.py`)
5. Routes check user role using `get_current_user()` or `has_permission()`

**Roles:**
- `admin` - Full system access
- `customer` - Access to client features (reports, analysis, portfolio)
- Public users - Read-only access to public pages

## Mobile-First Responsive Design

Frontend uses **mobile-first approach** with CSS Media Queries:

```css
/* Mobile (default, < 768px) */
.element { font-size: 14px; padding: 16px; }

/* Tablet (768px+) */
@media (min-width: 768px) {
  .element { font-size: 15px; padding: 20px; }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .element { font-size: 16px; padding: 24px; }
}
```

**Recent Changes (H5 Adaptation):**
- ClientLayout.vue: Hamburger menu on mobile, sidebar on desktop
- PublicStockList.vue: Card view on mobile, table view on desktop
- HomePage.vue: Responsive typography and grid layouts
- All public pages follow mobile-first pattern

**Responsive Components in Use:**
- Element Plus components handle responsiveness natively
- Custom media queries for layout adjustments
- Window resize listener for dynamic viewport detection (`isMobile` ref)

## Key Implementation Patterns

### Frontend

**State Management (Pinia):**
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const fetchUser = async () => { /* ... */ }
  return { user, isAdmin, fetchUser }
})
```

**API Calls (Axios):**
```typescript
// api/stock.ts
import axios from 'axios'
const client = axios.create({ baseURL: '/api/v1' })
export const stockApi = {
  list: (params) => client.get('/stocks', { params }),
  detail: (code) => client.get(`/stocks/${code}`),
}
```

**Component Structure:**
```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed, onMounted } from 'vue'
// 2. State
const items = ref([])
// 3. Computed
const filtered = computed(() => items.value.filter(...))
// 4. Lifecycle
onMounted(async () => { /* fetch data */ })
// 5. Methods
const handleSubmit = () => { /* ... */ }
</script>
```

**Naming Convention:**
- Components: `PascalCase` (HomePage.vue, UserCard.vue)
- Functions/variables: `camelCase` (fetchData, isLoading)
- Constants: `UPPER_SNAKE_CASE` (API_BASE_URL)

### Backend

**API Route Pattern:**
```python
# routers/stocks.py
router = APIRouter(prefix="/api/v1/stocks", tags=["stocks"])

@router.get("/", response_model=List[StockSchema])
async def list_stocks(db: Session = Depends(get_db)):
    return stock_service.get_stocks(db)

@router.get("/{code}", response_model=StockSchema)
async def get_stock(code: str, db: Session = Depends(get_db)):
    return stock_service.get_stock_by_code(db, code)
```

**Service Layer Pattern:**
```python
# services/stock_service.py
def get_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Stock).offset(skip).limit(limit).all()

def get_stock_by_code(db: Session, code: str):
    return db.query(Stock).filter(Stock.code == code).first()
```

**Naming Convention:**
- Modules/files: `snake_case` (stock_service.py, user_models.py)
- Classes: `PascalCase` (StockService, UserModel)
- Functions: `snake_case` (get_stock, validate_data)
- Constants: `UPPER_SNAKE_CASE` (DATABASE_URL)

## Database Schema Highlights

**Core Tables:**
- `users` - User accounts (username, email, password_hash, status)
- `roles` - Role definitions (admin, customer)
- `permissions` - Fine-grained permissions
- `user_roles` - Many-to-many mapping
- `stocks` - Stock data (code, name, price, industry)
- `concepts` - Concept categories (板块分类)
- `concept_stocks` - Stock-concept relationships
- `rankings` - Rankings data (涨幅, 跌幅, etc.)

**Key Relationships:**
- User ↔ Roles (many-to-many via user_roles)
- Stock ↔ Concepts (many-to-many via concept_stocks)
- Role ↔ Permissions (many-to-many via role_permissions)

⚠️ **详细说明**：见 `.spec-workflow/database-schema.md`
- 所有表的完整字段定义和含义
- 数据流向和计算逻辑（排名、汇总）
- 关键概念解释（trade_value、概念vs行业等）
- 常见查询示例

## Important Configuration Notes

### Frontend Proxy
- **Critical:** Proxy uses `127.0.0.1:8000` (not `localhost`)
- Reason: Avoid IPv6 resolution issues on macOS
- Location: `frontend/vite.config.ts` (line 17)
- If you change backend port, update this proxy target

### Environment Setup
**Frontend (.env):**
```
VITE_API_BASE_URL=/api/v1
```

**Backend (.env):**
```
DATABASE_URL=sqlite:///./data.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Development vs Production
- **Dev:** SQLite database, hot reload enabled, CORS open
- **Prod:** PostgreSQL recommended, CORS restricted, HTTPS required

## Reference Documents

For detailed information, consult:

- **`.spec-workflow/steering/product.md`** - Product vision, features, and user goals
- **`.spec-workflow/steering/tech.md`** - Technology decisions, architecture, known limitations
- **`.spec-workflow/steering/structure.md`** - Directory structure, naming conventions, module boundaries

## Common Development Tasks

### Adding a New API Endpoint

1. Create schema in `backend/app/schemas/`
2. Create service method in `backend/app/services/`
3. Add route in `backend/app/routers/`
4. Add route file to `app/main.py` if new module
5. Test via Swagger UI at http://127.0.0.1:8000/docs

### Adding a New Frontend Page

1. Create Vue component in `frontend/src/views/`
2. Add route to `frontend/src/router/index.ts`
3. Set appropriate `requiresAuth` and `requiredRole` in meta
4. Follow responsive design pattern (mobile-first media queries)
5. Use Element Plus components for UI consistency

### Implementing Mobile Adaptation

1. Add `isMobile` ref with window resize listener (onMounted/onUnmounted)
2. Use `v-if="isMobile"` to conditionally render mobile/desktop versions
3. Apply three breakpoint media queries (768px, 1024px)
4. Test at actual mobile dimensions (375px width minimum)
5. Update parent component styles if needed

### Authentication Flow

1. User submits login credentials to `/api/v1/auth/login`
2. Backend returns JWT token and user info
3. Frontend stores token in localStorage
4. Axios interceptor adds token to all requests
5. Backend `get_current_user()` validates token and returns user
6. Route guards check role and redirect unauthorized users

## Known Limitations & Technical Debt

See `.spec-workflow/steering/tech.md` for:
- SQLite single-file storage limitation (upgrade to PostgreSQL needed for scale)
- Missing WebSocket implementation (currently using polling)
- File upload size limits and lack of progress tracking
- No centralized logging system (add ELK Stack for production)
- Missing rate limiting on API endpoints

## Tips for Productivity

- **Hot Reload:** Both frontend (Vite HMR) and backend (--reload flag) support hot reload
- **API Documentation:** Access Swagger UI at http://127.0.0.1:8000/docs during development
- **Database Queries:** Use `db.session.query()` syntax, not raw SQL
- **Component Testing:** Use Element Plus's built-in components rather than custom implementations
- **Type Safety:** Always define TypeScript types for API responses (use Pydantic schemas as source of truth)
