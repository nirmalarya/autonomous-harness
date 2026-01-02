---
name: project-patterns
description: Framework-specific patterns for common stacks. Use when implementing features in Next.js, FastAPI, Express, or React projects. Covers project structure, data fetching, state management, and API design patterns.
---

# Project-Specific Patterns

Framework conventions for autonomous coding sessions.

## Next.js 15 (App Router)

**Project Structure:**
```
app/
├── (auth)/
│   ├── login/page.tsx
│   └── register/page.tsx
├── dashboard/
│   ├── page.tsx
│   └── layout.tsx
├── api/
│   └── users/route.ts
└── layout.tsx
```

**Server Components (Default):**
```typescript
// app/dashboard/page.tsx
export default async function DashboardPage() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'no-store' // or 'force-cache'
  });

  return <div>{/* Render data */}</div>;
}
```

**Client Components (Interactive):**
```typescript
'use client';

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**Server Actions (Mutations):**
```typescript
// app/actions.ts
'use server';

export async function createUser(formData: FormData) {
  const email = formData.get('email');
  // Validate and save to DB
  return { success: true };
}

// app/register/page.tsx
import { createUser } from '../actions';

export default function RegisterPage() {
  return (
    <form action={createUser}>
      <input name="email" type="email" />
      <button type="submit">Register</button>
    </form>
  );
}
```

**API Routes:**
```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const users = await db.users.findMany();
  return NextResponse.json(users);
}

export async function POST(request: Request) {
  const body = await request.json();
  // Validate with Zod
  const user = await db.users.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}
```

## FastAPI (Python)

**Project Structure:**
```
app/
├── main.py
├── models.py
├── schemas.py
├── routes/
│   ├── users.py
│   └── auth.py
└── database.py
```

**Main Application:**
```python
# app/main.py
from fastapi import FastAPI
from app.routes import users, auth

app = FastAPI()

app.include_router(users.router, prefix="/api/users")
app.include_router(auth.router, prefix="/api/auth")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

**Routes with Validation:**
```python
# app/routes/users.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import UserCreate, UserResponse
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db = Depends(get_db)):
    # UserCreate validates input automatically
    db_user = await db.users.create(user.dict())
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db = Depends(get_db)):
    user = await db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Pydantic Schemas:**
```python
# app/schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True  # Formerly orm_mode
```

## Express.js + Prisma

**Project Structure:**
```
src/
├── index.ts
├── routes/
│   └── users.ts
├── middleware/
│   └── auth.ts
└── prisma/
    └── schema.prisma
```

**Express Server:**
```typescript
// src/index.ts
import express from 'express';
import usersRouter from './routes/users';

const app = express();

app.use(express.json());
app.use('/api/users', usersRouter);

app.listen(3000, () => console.log('Server running on port 3000'));
```

**Routes with Prisma:**
```typescript
// src/routes/users.ts
import { Router } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

router.get('/', async (req, res) => {
  try {
    const users = await prisma.user.findMany();
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

router.post('/', async (req, res) => {
  try {
    const user = await prisma.user.create({
      data: req.body
    });
    res.status(201).json(user);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create user' });
  }
});

export default router;
```

## React (Client-Side Data Fetching)

**With TanStack Query:**
```typescript
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function Users() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await fetch('/api/users');
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    }
  });

  const createUser = useMutation({
    mutationFn: async (userData) => {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    }
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading users</div>;

  return (
    <div>
      {data.map(user => <div key={user.id}>{user.name}</div>)}
    </div>
  );
}
```

## Database Patterns

**Prisma Schema:**
```prisma
// prisma/schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  createdAt DateTime @default(now())
}
```

**Migrations:**
```bash
# Create migration
npx prisma migrate dev --name add_posts_table

# Apply migrations
npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate
```

## Common Patterns

**Environment Variables:**
```typescript
// .env.local (Next.js)
DATABASE_URL="postgresql://..."
NEXT_PUBLIC_API_URL="https://api.example.com"

// Access in code
const dbUrl = process.env.DATABASE_URL;  // Server-side only
const apiUrl = process.env.NEXT_PUBLIC_API_URL;  // Client + server
```

**Error Boundaries (React):**
```typescript
'use client';

import { Component, ReactNode } from 'react';

class ErrorBoundary extends Component<{children: ReactNode}> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

**Middleware (Next.js):**
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/dashboard/:path*'
};
```

## Best Practices

**Next.js:**
- Use Server Components by default
- Add `'use client'` only when needed (interactivity, hooks)
- Use Server Actions for mutations
- Validate with Zod schemas

**FastAPI:**
- Use Pydantic models for validation
- Dependency injection for database
- Async/await for database operations
- Proper HTTP status codes

**Express:**
- Middleware for auth/validation
- Error handling middleware at end
- Use Prisma for type-safe queries
- Environment variables for config

**React:**
- TanStack Query for server state
- useState for local state
- Error boundaries for graceful failures
- Loading states for better UX

For detailed examples, see [examples/](examples/) directory.
