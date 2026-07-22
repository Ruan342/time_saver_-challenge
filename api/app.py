import itertools
import logging
import os

from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUIRED_FIELDS = ["paciente", "cpf", "medico", "especialidade", "data", "horario", "convenio", "status"]

AGENDAMENTOS = [
    {
        "paciente": "Maria Silva",
        "cpf": "123.456.789-00",
        "medico": "Dr. João Souza",
        "especialidade": "Cardiologia",
        "data": "2026-07-21",
        "horario": "09:00",
        "convenio": "Unimed",
        "status": "Confirmado",
    },
    {
        "paciente": "Carlos Pereira",
        "cpf": "234.567.890-11",
        "medico": "Dra. Ana Lima",
        "especialidade": "Dermatologia",
        "data": "2026-07-21",
        "horario": "10:30",
        "convenio": "Bradesco Saúde",
        "status": "Confirmado",
    },
    {
        "paciente": "Fernanda Costa",
        "cpf": "345.678.901-22",
        "medico": "Dr. João Souza",
        "especialidade": "Cardiologia",
        "data": "2026-07-21",
        "horario": "11:15",
        "convenio": "Particular",
        "status": "Cancelado",
    },
    {
        "paciente": "Roberto Alves",
        "cpf": "456.789.012-33",
        "medico": "Dr. Paulo Mendes",
        "especialidade": "Ortopedia",
        "data": "2026-07-22",
        "horario": "08:45",
        "convenio": "SulAmérica",
        "status": "Confirmado",
    },
    {
        "paciente": "Juliana Ramos",
        "cpf": "567.890.123-44",
        "medico": "Dra. Ana Lima",
        "especialidade": "Dermatologia",
        "data": "2026-07-22",
        "horario": "14:00",
        "convenio": "Unimed",
        "status": "Aguardando",
    },
    {
        "paciente": "Marcos Vinícius",
        "cpf": "678.901.234-55",
        "medico": "Dra. Beatriz Nunes",
        "especialidade": "Pediatria",
        "data": "2026-07-22",
        "horario": "15:30",
        "convenio": "Amil",
        "status": "Confirmado",
    },
    {
        "paciente": "Patrícia Gomes",
        "cpf": "789.012.345-66",
        "medico": "Dr. Paulo Mendes",
        "especialidade": "Ortopedia",
        "data": "2026-07-23",
        "horario": "09:30",
        "convenio": "Particular",
        "status": "Confirmado",
    },
    {
        "paciente": "Eduardo Martins",
        "cpf": "890.123.456-77",
        "medico": "Dra. Beatriz Nunes",
        "especialidade": "Pediatria",
        "data": "2026-07-23",
        "horario": "16:45",
        "convenio": "Bradesco Saúde",
        "status": "Cancelado",
    },
]

_id_counter = itertools.count(1)
for _agendamento in AGENDAMENTOS:
    _agendamento["id"] = next(_id_counter)


@app.route("/agendamentos", methods=["GET"])
def agendamentos():
    logger.info("Retornando %d agendamentos", len(AGENDAMENTOS))
    return jsonify(AGENDAMENTOS)


@app.route("/agendamentos", methods=["POST"])
def criar_agendamento():
    data = request.get_json(silent=True) or {}

    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing)}"}), 400

    novo_agendamento = {field: data[field] for field in REQUIRED_FIELDS}
    novo_agendamento["id"] = next(_id_counter)
    AGENDAMENTOS.append(novo_agendamento)

    logger.info("Agendamento criado: id=%s", novo_agendamento["id"])
    return jsonify(novo_agendamento), 201


@app.route("/agendamentos", methods=["DELETE"])
def excluir_agendamentos():
    global AGENDAMENTOS

    data = request.get_json(silent=True) or {}
    ids = data.get("ids")

    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "Informe uma lista de ids para exclusão."}), 400

    try:
        ids_set = {int(item) for item in ids}
    except (TypeError, ValueError):
        return jsonify({"error": "A lista de ids deve conter apenas números."}), 400

    tamanho_antes = len(AGENDAMENTOS)
    AGENDAMENTOS = [a for a in AGENDAMENTOS if a["id"] not in ids_set]
    removidos = tamanho_antes - len(AGENDAMENTOS)

    logger.info("Removidos %d agendamentos", removidos)
    return jsonify({"removed": removidos}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
