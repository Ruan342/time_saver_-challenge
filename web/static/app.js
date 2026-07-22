const feedback = document.getElementById("feedback");

const table = new Tabulator("#agenda-table", {
  layout: "fitColumns",
  placeholder: "Nenhum agendamento encontrado",
  columns: [
    { title: "Data", field: "data" },
    { title: "Horário", field: "horario" },
    { title: "Paciente", field: "paciente" },
    { title: "CPF", field: "cpf" },
    { title: "Médico", field: "medico" },
    { title: "Especialidade", field: "especialidade" },
    { title: "Convênio", field: "convenio" },
    { title: "Status", field: "status" },
  ],
});

function showFeedback(message) {
  feedback.textContent = message || "";
}

function loadAgendamentos(query) {
  const url = query ? `/api/agendamentos?q=${encodeURIComponent(query)}` : "/api/agendamentos";

  fetch(url)
    .then((response) => response.json().then((data) => ({ status: response.status, data })))
    .then(({ status, data }) => {
      if (status !== 200) {
        showFeedback(data.error || "Não foi possível carregar os agendamentos.");
        table.setData([]);
        return;
      }
      showFeedback("");
      table.setData(data);
    })
    .catch(() => {
      showFeedback("Erro ao comunicar com o servidor. Tente novamente.");
      table.setData([]);
    });
}

document.getElementById("search-btn").addEventListener("click", () => {
  loadAgendamentos(document.getElementById("search-input").value.trim());
});

document.getElementById("search-input").addEventListener("keyup", (event) => {
  if (event.key === "Enter") {
    loadAgendamentos(event.target.value.trim());
  }
});

document.getElementById("clear-btn").addEventListener("click", () => {
  document.getElementById("search-input").value = "";
  loadAgendamentos("");
});

loadAgendamentos("");
