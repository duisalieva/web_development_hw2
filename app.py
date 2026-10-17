"""Rate My Mort: a tiny Flask + PostgreSQL ratings app."""

import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from flask import Flask, jsonify, render_template, request

sabog_app = Flask(__name__)


@contextmanager
def db_connection():
    """Open a PostgreSQL connection, commit changes, and close it safely."""
    connection = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def create_table():
    """Create the ratings table automatically when the app starts."""
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ratings (
                    id SERIAL PRIMARY KEY,
                    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 10),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )


def get_statistics(connection):
    """Read votes from PostgreSQL and calculate public statistics."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT rating, COUNT(*) FROM ratings GROUP BY rating ORDER BY rating;"
        )
        rows = cursor.fetchall()

    distribution = {str(rating): 0 for rating in range(1, 11)}
    for rating, count in rows:
        distribution[str(rating)] = count

    total = sum(distribution.values())
    average = (
        round(sum(int(rating) * count for rating, count in distribution.items()) / total, 1)
        if total
        else None
    )
    most_popular = (
        max(range(1, 11), key=lambda rating: (distribution[str(rating)], rating))
        if total
        else None
    )
    voted_ratings = [int(rating) for rating, count in distribution.items() if count]

    return {
        "total_ratings": total,
        "average_rating": average,
        "highest_rating": max(voted_ratings) if total else None,
        "lowest_rating": min(voted_ratings) if total else None,
        "most_popular_rating": most_popular,
        "distribution": distribution,
    }


def get_mort_reaction(rating):
    if rating <= 3:
        return "Mort is crying... Why don't you love him?"
    if rating <= 6:
        return "Mort thinks he deserves better!"
    if rating <= 9:
        return "Mort is happy! Thank you!"
    return "MORT LOVES YOU!!!"


@sabog_app.get("/")
def home():

    image_name = "mort.jpeg" if (Path(sabog_app.static_folder) / "mort.jpeg").is_file() else "mort.svg"
    return render_template(
        "index.html",
        environment=os.environ.get("SABOG_ENV", "testing"),
        mort_image=image_name,
    )


@sabog_app.get("/api/stats")
def api_stats():
    try:
        with db_connection() as connection:
            stats = get_statistics(connection)
        return jsonify(stats)
    except psycopg2.Error:
        sabog_app.logger.exception("Could not read ratings")
        return jsonify({"error": "The database is temporarily unavailable."}), 503


@sabog_app.post("/api/rate")
def api_rate():
    payload = request.get_json(silent=True)
    rating = payload.get("rating") if isinstance(payload, dict) else None

    if type(rating) is not int or not 1 <= rating <= 10:
        return jsonify({"error": "Rating must be an integer from 1 to 10."}), 400

    try:
        with db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ratings (rating) VALUES (%s);", (rating,)
                )
            stats = get_statistics(connection)

        return jsonify({
            "message": get_mort_reaction(rating),
            "rating": rating,
            "stats": stats,
        }), 201
    except psycopg2.Error:
        sabog_app.logger.exception("Could not save rating")
        return jsonify({"error": "The database is temporarily unavailable."}), 503


if __name__ == "__main__":
    create_table()
    sabog_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
