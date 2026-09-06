const initializePickersAndHorario = () => {
    // Initialize flatpickr if available
    if (typeof flatpickr !== "undefined") {
        flatpickr(".js-date-picker", {
            altInput: true,
            altFormat: "d/m/Y",
            dateFormat: "Y-m-d",
            locale: "pt",
            allowInput: true,
        });
    }

    const dateInput = document.querySelector("#id_data");
    const timeInput = document.querySelector("#id_horario");
    const message = document.querySelector("#availability-message");
    if (!dateInput || !timeInput) return;

    async function loadAvailableTimes() {
        const selectedDate = dateInput.value;
        timeInput.innerHTML = '<option value="">Carregando horários...</option>';
        timeInput.disabled = true;
        if (!selectedDate) {
            timeInput.innerHTML = '<option value="">Escolha uma data primeiro</option>';
            if (message) message.textContent = "Escolha uma data para ver os horários disponíveis.";
            return;
        }
        try {
            const response = await fetch(`/horarios-disponiveis/?data=${encodeURIComponent(selectedDate)}`);
            const result = await response.json();
            timeInput.innerHTML = '<option value="">Selecione um horário</option>';
            result.horarios.forEach((horario) => {
                const option = new Option(horario, horario);
                timeInput.add(option);
            });
            timeInput.disabled = result.horarios.length === 0;
            if (message) message.textContent = result.mensagem || `${result.horarios.length} horário(s) disponível(is) para esta data.`;
        } catch {
            timeInput.innerHTML = '<option value="">Não foi possível carregar os horários</option>';
            if (message) message.textContent = "Tente novamente em instantes.";
        }
    }

    // Initialize the time input with a placeholder even if no date is selected
    if (dateInput.value) {
        loadAvailableTimes();
    } else {
        timeInput.innerHTML = '<option value="">Escolha uma data primeiro</option>';
        timeInput.disabled = true;
        if (message) message.textContent = "Escolha uma data para ver os horários disponíveis.";
    }

    dateInput.addEventListener("change", loadAvailableTimes);
};

// Run initialization when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePickersAndHorario);
} else {
    // DOM is already loaded
    initializePickersAndHorario();
}