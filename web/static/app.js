const feedback = document.getElementById("feedback");
const deleteBtn = document.getElementById("delete-btn");
const addBtn = document.getElementById("add-btn");
const modal = document.getElementById("agendamento-modal");
const form = document.getElementById("agendamento-form");
const modalFeedback = document.getElementById("modal-feedback");
const modalCancelBtn = document.getElementById("modal-cancel-btn");

const table = new Tabulator("#agenda-table", {
  layout: "fitColumns",
  placeholder: "Nenhum agendamento encontrado",
  selectableRows: true,
  columns: [
    { formatter: "rowSelection", titleFormatter: "rowSelection", hozAlign: "center", headerSort: false, width: 40 },
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

table.on("rowSelectionChanged", (data) => {
  deleteBtn.disabled = data.length === 0;
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

deleteBtn.addEventListener("click", () => {
  const selected = table.getSelectedData();
  if (selected.length === 0) {
    return;
  }

  const confirmMessage = selected.length === 1
    ? "Deseja excluir o agendamento selecionado?"
    : `Deseja excluir os ${selected.length} agendamentos selecionados?`;

  if (!window.confirm(confirmMessage)) {
    return;
  }

  const ids = selected.map((row) => row.id);

  fetch("/api/agendamentos", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  })
    .then((response) => response.json().then((data) => ({ status: response.status, data })))
    .then(({ status, data }) => {
      if (status !== 200) {
        showFeedback(data.error || "Não foi possível excluir os agendamentos selecionados.");
        return;
      }
      showFeedback("");
      loadAgendamentos(document.getElementById("search-input").value.trim());
    })
    .catch(() => {
      showFeedback("Erro ao comunicar com o servidor. Tente novamente.");
    });
});

function openModal() {
  form.reset();
  modalFeedback.textContent = "";
  modal.showModal();
}

function closeModal() {
  modal.close();
}

addBtn.addEventListener("click", openModal);
modalCancelBtn.addEventListener("click", closeModal);

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  fetch("/api/agendamentos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json().then((data) => ({ status: response.status, data })))
    .then(({ status, data }) => {
      if (status !== 201) {
        modalFeedback.textContent = data.error || "Não foi possível criar o agendamento.";
        return;
      }
      closeModal();
      showFeedback("");
      loadAgendamentos(document.getElementById("search-input").value.trim());
    })
    .catch(() => {
      modalFeedback.textContent = "Erro ao comunicar com o servidor. Tente novamente.";
    });
});

loadAgendamentos("");
