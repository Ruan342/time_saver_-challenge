import logging
import os
import sqlite3
from functools import wraps

import requests
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from db import get_connection, init_db
from seed import seed_test_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

API_URL = os.environ.get("API_URL", "http://localhost:5001")
REQUIRED_FIELDS = ["paciente", "cpf", "medico", "especialidade", "data", "horario", "convenio", "status"]

with app.app_context():
    init_db()
    seed_test_user()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("agenda"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier or not password:
            flash("Informe usuário/e-mail e senha.")
            return render_template("login.html")

        try:
            conn = get_connection()
            user = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (identifier,),
            ).fetchone()
            conn.close()
        except sqlite3.Error:
            logger.exception("Erro ao conectar ao banco de dados durante o login")
            flash("Erro ao acessar o sistema. Tente novamente em instantes.")
            return render_template("login.html")

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Usuário ou senha inválidos.")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("agenda"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/agenda")
@login_required
def agenda():
    return render_template("agenda.html", username=session.get("username"))


@app.route("/api/agendamentos")
@login_required
def api_agendamentos():
    query = request.args.get("q", "").strip().lower()

    try:
        response = requests.get(f"{API_URL}/agendamentos", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Falha ao consultar o serviço de agendamentos")
        return jsonify({"error": "Serviço de agendamentos indisponível no momento. Tente novamente mais tarde."}), 503

    try:
        data = response.json()
    except ValueError:
        logger.exception("Resposta inválida (não é JSON) do serviço de agendamentos")
        return jsonify({"error": "Resposta inválida do serviço de agendamentos."}), 502

    if not isinstance(data, list):
        logger.error("Formato inesperado recebido da API de agendamentos: %r", data)
        return jsonify({"error": "Resposta inválida do serviço de agendamentos."}), 502

    valid_records = []
    for record in data:
        if not isinstance(record, dict):
            logger.warning("Registro ignorado por não ser um objeto válido: %r", record)
            continue
        missing = [field for field in REQUIRED_FIELDS if not record.get(field)]
        if missing:
            logger.warning("Registro descartado por campos obrigatórios ausentes %s: %r", missing, record)
            continue
        valid_records.append(record)

    if query:
        valid_records = [
            r for r in valid_records
            if query in r["paciente"].lower()
            or query in r["cpf"].lower()
            or query in r["medico"].lower()
        ]

    return jsonify(valid_records)


@app.route("/api/agendamentos", methods=["POST"])
@login_required
def api_criar_agendamento():
    data = request.get_json(silent=True) or {}

    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

    try:
        response = requests.post(f"{API_URL}/agendamentos", json=data, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Falha ao criar agendamento no serviço de agendamentos")
        return jsonify({"error": "Serviço de agendamentos indisponível no momento. Tente novamente mais tarde."}), 503

    try:
        criado = response.json()
    except ValueError:
        logger.exception("Resposta inválida (não é JSON) do serviço de agendamentos")
        return jsonify({"error": "Resposta inválida do serviço de agendamentos."}), 502

    return jsonify(criado), 201


@app.route("/api/agendamentos", methods=["DELETE"])
@login_required
def api_excluir_agendamentos():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids")

    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "Informe ao menos um agendamento para exclusão."}), 400

    try:
        response = requests.delete(f"{API_URL}/agendamentos", json={"ids": ids}, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Falha ao excluir agendamentos no serviço de agendamentos")
        return jsonify({"error": "Serviço de agendamentos indisponível no momento. Tente novamente mais tarde."}), 503

    try:
        resultado = response.json()
    except ValueError:
        logger.exception("Resposta inválida (não é JSON) do serviço de agendamentos")
        return jsonify({"error": "Resposta inválida do serviço de agendamentos."}), 502

    return jsonify(resultado), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
