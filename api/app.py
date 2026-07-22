import logging
import os

from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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


@app.route("/agendamentos")
def agendamentos():
    logger.info("Retornando %d agendamentos", len(AGENDAMENTOS))
    return jsonify(AGENDAMENTOS)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
