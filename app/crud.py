from sqlalchemy.orm import Session
from .models import Note
from .schemas import NoteIn

def get_notes(db: Session):
    return db.query(Note).all()

def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def create_note(db: Session, note: NoteIn):
    obj = Note(**note.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_note(db: Session, note_id: int):
    note = get_note(db, note_id)
    if note:
        db.delete(note)
        db.commit()
    return note