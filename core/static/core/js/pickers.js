document.addEventListener("DOMContentLoaded", () => {
    if (typeof flatpickr === "undefined") {
        return;
    }

    flatpickr(".js-date-picker", {
        altInput: true,
        altFormat: "d/m/Y",
        dateFormat: "Y-m-d",
        locale: "pt",
        allowInput: true,
    });

    flatpickr(".js-time-picker", {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true,
        allowInput: true,
    });
});
