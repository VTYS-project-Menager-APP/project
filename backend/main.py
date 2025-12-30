from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Menager APP API", version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    from database import engine, Base
    from scheduler import start_scheduler
    
    # Ensure tables exist (Basic check, though seed script is better for this)
    Base.metadata.create_all(bind=engine)
    
    start_scheduler()

from routers import api, auth, etkinlik, market_analysis, transport, notifications, smart_transport, style
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(api.router, prefix="/api/v1")
app.include_router(etkinlik.router, prefix="/api/v1")
app.include_router(market_analysis.router, prefix="/api/v1")
app.include_router(transport.router, prefix="/api/v1")
app.include_router(smart_transport.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(style.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Menager APP API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
