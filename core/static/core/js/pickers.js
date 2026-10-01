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
    const servicoInput = document.querySelector("#id_servico");
    const message = document.querySelector("#availability-message");
    if (!dateInput || !timeInput) return;

    function setAvailabilityMessage(text, state = "info") {
        if (!message) return;
        message.textContent = text;
        message.classList.remove("is-info", "is-success", "is-error");
        message.classList.add(`is-${state}`);
    }

    async function loadAvailableTimes() {
        const selectedDate = dateInput.value;
        const selectedServico = servicoInput ? servicoInput.value : "";

        timeInput.innerHTML = '<option value="">Carregando horários...</option>';
        timeInput.disabled = true;
        setAvailabilityMessage("Carregando horários disponíveis...", "info");

        if (!selectedDate) {
            timeInput.innerHTML = '<option value="">Escolha uma data primeiro</option>';
            setAvailabilityMessage("Escolha uma data para ver os horários disponíveis.", "info");
            return;
        }

        try {
            const params = new URLSearchParams({ data: selectedDate });
            if (selectedServico) {
                params.set("servico", selectedServico);
            }

            const response = await fetch(`/horarios-disponiveis/?${params.toString()}`);
            const result = await response.json();
            timeInput.innerHTML = '<option value="">Selecione um horário</option>';
            result.horarios.forEach((horario) => {
                const option = new Option(horario, horario);
                timeInput.add(option);
            });
            timeInput.disabled = result.horarios.length === 0;
            const state = result.horarios.length ? "success" : "error";
            setAvailabilityMessage(result.mensagem || `${result.horarios.length} horário(s) disponível(is) para esta data.`, state);
        } catch {
            timeInput.innerHTML = '<option value="">Não foi possível carregar os horários</option>';
            setAvailabilityMessage("Não foi possível carregar os horários. Tente novamente em instantes.", "error");
        }
    }

    // Initialize the time input with a placeholder even if no date is selected
    if (dateInput.value) {
        loadAvailableTimes();
    } else {
        timeInput.innerHTML = '<option value="">Escolha uma data primeiro</option>';
        timeInput.disabled = true;
        setAvailabilityMessage("Escolha uma data para ver os horários disponíveis.", "info");
    }

    dateInput.addEventListener("change", loadAvailableTimes);

    // Recarrega os horários também quando o serviço muda, já que
    if (servicoInput) {
        servicoInput.addEventListener("change", loadAvailableTimes);
    }

    const bookingForm = document.querySelector(".js-booking-form");
    if (bookingForm) {
        bookingForm.addEventListener("submit", () => {
            const submitButton = bookingForm.querySelector('button[type="submit"]');
            if (!submitButton) return;

            submitButton.disabled = true;
            submitButton.textContent = "AGENDANDO...";
        });
    }
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePickersAndHorario);
} else {
    // DOM is already loaded
    initializePickersAndHorario();
}
