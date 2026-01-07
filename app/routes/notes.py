from flask import Blueprint, render_template, request, redirect, url_for, g, abort
from models import Note
from app import db

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/")
def index():
    return redirect(url_for("notes.list_notes"))

def require_login():
    if not getattr(g, "current_user", None):
        return redirect(url_for("auth.login"))

@notes_bp.route("/notes")
def list_notes():
    if not getattr(g, "current_user", None):
        return redirect(url_for("auth.login"))
    notes = Note.query.filter_by(user_id=g.current_user.id).order_by(Note.created_at.desc()).all()
    return render_template("notes_list.html", notes=notes)

@notes_bp.route("/notes/<int:note_id>")
def view_note(note_id):
    if not getattr(g, "current_user", None):
        return redirect(url_for("auth.login"))
    note = Note.query.get_or_404(note_id)
    if note.user_id != g.current_user.id:
        abort(403)
    return render_template("notes_view.html", note=note)

@notes_bp.route("/notes/new", methods=["GET", "POST"])
def create_note():
    if not getattr(g, "current_user", None):
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        tags = request.form.get("tags", "").strip()
        if not title:
            return render_template("notes_form.html", error="Укажите заголовок", note={})
        n = Note(title=title, content=content, tags=tags, user_id=g.current_user.id)
        db.session.add(n)
        db.session.commit()
        return redirect(url_for("notes.view_note", note_id=n.id))
    return render_template("notes_form.html", note={})

@notes_bp.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def edit_note(note_id):
    if not getattr(g, "current_user", None):
        return redirect(url_for("auth.login"))
    note = Note.query.get_or_404(note_id)
    if note.user_id != g.current_user.id:
        abort(403)
    if request.method == "POST":
        note.title = request.form.get("title", note.title).strip()
        note.content = request.form.get("content", note.content).strip()
        note.tags = request.form.get("tags", note.tags).strip()
        db.session.commit()
        return redirect(url_for("notes.view_note", note_id=note.id))
    return render_template("notes_form.html", note=note)

@notes_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
def delete_note(note_id):
    if not getattr(g, "current_user", None):
        return redirect(url_for("auth.login"))
    note = Note.query.get_or_404(note_id)
    if note.user_id != g.current_user.id:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("notes.list_notes"))
