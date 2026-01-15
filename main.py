from fastapi import FastAPI, HTTPException
from typing import Any
import requests
import sqlite3


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/sum")
def sum(x: int = 0, y: int = 10):
    return x + y


@app.get("/geocode")
def sum(lat: float, lon: float):
    url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}'
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()


@app.get('/movies')
def get_movies():
    output = []
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM movies")
    for movie in cursor:
        movie = {'id': movie[0], 'title': movie[1], 'year': movie[2], 'actors': movie[3]}
        output.append(movie)
    return output

@app.get('/movies/{movie_id}')
def get_single_movie(movie_id:int):
    db = sqlite3.connect('movies.db')
    cursor = db.cursor()
    movie = cursor.execute("SELECT * FROM movies WHERE id=?", (movie_id,)).fetchone()
    if movie is None:
        return {"message": "Movie  not found"}
    return {'id': movie[0], 'title': movie[1], 'year': movie[2], 'actors': movie[3]}

@app.post("/movies")
def add_movie(params: dict[str, Any]):
    try:
        if 'title' not in params or 'year' not in params or 'actors' not in params:
            raise HTTPException(status_code=400, detail="Please provide all of the parameters: title, year lub actors")
        
        with sqlite3.connect('movies.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO movies (title, year, actors) VALUES (?, ?, ?)",
                   (params['title'], params['year'], params['actors']))
            db.commit()
            return {"message": "Movie " + str(cursor.lastrowid) + " added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    with sqlite3.connect('movies.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM movies WHERE id=?", (movie_id,))
        db.commit()
        return {"message": "Movie " + str(movie_id) + " deleted successfully"}
    
@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, params: dict[str, Any]):
    with sqlite3.connect('movies.db') as db:
        cursor = db.cursor()
        cursor.execute("UPDATE movies SET title=?, year=?, actors=? WHERE id=?",
                   (params['title'], params['year'], params['actors'], movie_id))
        db.commit()
        return {"message": "Movie " + str(movie_id) + " updated successfully"}
    
@app.delete("/movies")
def delete_all_movies():
    with sqlite3.connect('movies.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM movies")
        moviesDeleted = cursor.rowcount
        db.commit()
        return {"message": str(moviesDeleted) + " movies deleted successfully"}