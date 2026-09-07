"""FastAPI backend: stores workout sessions (SQLite) and serves the frontend."""
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(__file__).resolve().parent / "trainer.db"

app = FastAPI(title="Personal AI Trainer")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


with db() as c:
    c.execute(
        """CREATE TABLE IF NOT EXISTS workouts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise TEXT NOT NULL,
            reps INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
    )


class Workout(BaseModel):
    exercise: str = Field(pattern="^(curl|squat|pushup)$")
    reps: int = Field(ge=0, le=10000)
    duration_sec: int = Field(ge=0, le=86400)


@app.post("/api/workouts", status_code=201)
def add_workout(w: Workout):
    with db() as c:
        cur = c.execute(
            "INSERT INTO workouts(exercise, reps, duration_sec) VALUES (?,?,?)",
            (w.exercise, w.reps, w.duration_sec),
        )
    return {"id": cur.lastrowid}


@app.get("/api/workouts")
def list_workouts(limit: int = 20):
    with db() as c:
        rows = c.execute(
            "SELECT * FROM workouts ORDER BY id DESC LIMIT ?", (min(limit, 200),)
        ).fetchall()
    return [dict(r) for r in rows]


@app.delete("/api/workouts/{wid}")
def delete_workout(wid: int):
    with db() as c:
        cur = c.execute("DELETE FROM workouts WHERE id=?", (wid,))
    if cur.rowcount == 0:
        raise HTTPException(404, "Workout not found")
    return {"deleted": wid}


@app.get("/api/stats")
def stats():
    with db() as c:
        t = c.execute(
            "SELECT COUNT(*) n, COALESCE(SUM(reps),0) reps, COALESCE(SUM(duration_sec),0) secs FROM workouts"
        ).fetchone()
        by_ex = c.execute(
            "SELECT exercise, SUM(reps) reps FROM workouts GROUP BY exercise"
        ).fetchall()
        week = c.execute(
            """SELECT date(created_at) day, SUM(reps) reps FROM workouts
               WHERE date(created_at) >= date('now','-6 days')
               GROUP BY day ORDER BY day"""
        ).fetchall()
    return {
        "total_workouts": t["n"],
        "total_reps": t["reps"],
        "total_seconds": t["secs"],
        "by_exercise": {r["exercise"]: r["reps"] for r in by_ex},
        "last7": [dict(r) for r in week],
    }


app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
