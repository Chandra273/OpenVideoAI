from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import auth, users
from .core.config import settings

# from .api.v1 import auth, users — imports routers so we can mount them under versioned prefixes.
# app = FastAPI(...) — constructs the FastAPI application instance.
# CORS middleware block — permits the React dev server to make requests (update origins for production).
# app.include_router(auth.router, prefix="/api/v1/auth") — mounts the auth routes at /api/v1/auth.
# @app.on_event("startup") + Base.metadata.create_all(bind=engine) — creates DB tables automatically in dev. In prod, use Alembic migrations instead (keeps DB schema evolution controlled).

app = FastAPI(title="OpenVideoAI Backend", version="0.1.0")

# Allow the local React dev server by default; update in production.
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "OpenVideoAI backend is running"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


@app.on_event("startup")
def on_startup():
    # Ensure database tables are created in development. In production, use Alembic migrations.
    from .db.session import Base, engine

    Base.metadata.create_all(bind=engine)
