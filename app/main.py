from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from .db import Base, engine, SessionLocal
from . import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Note Manager")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    notes = crud.get_notes(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "notes": notes}
    )

@app.post("/")
def add_note(
    title: str = Form(...),
    content: str = Form(""),
    db: Session = Depends(get_db),
):
    crud.create_note(db, schemas.NoteIn(title=title, content=content))
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    crud.delete_note(db, note_id)
    return RedirectResponse("/", status_code=303)