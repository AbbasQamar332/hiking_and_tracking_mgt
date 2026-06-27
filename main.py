from fastapi import FastAPI

from app.database import Base, engine
from app.routers import admin, athentication, bookings, events, reviews


app = FastAPI(title="Hiking System API")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(athentication.router)
app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(reviews.router)
app.include_router(admin.router)



@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hiking System API is running"}