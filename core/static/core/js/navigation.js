const navigation = document.querySelector(".navbar");
const navigationToggle = document.querySelector(".nav-toggle");

if (navigation && navigationToggle) {
    const setMenuState = (isOpen) => {
        navigation.classList.toggle("is-menu-open", isOpen);
        navigationToggle.setAttribute("aria-expanded", String(isOpen));
    };

    navigationToggle.addEventListener("click", () => {
        setMenuState(!navigation.classList.contains("is-menu-open"));
    });

    navigation.addEventListener("click", (event) => {
        const triggerLink = event.target.closest("a");

        if (triggerLink && navigation.classList.contains("is-menu-open")) {
            setMenuState(false);
        }
    });

    document.addEventListener("click", (event) => {
        if (
            navigation.classList.contains("is-menu-open") &&
            !navigation.contains(event.target)
        ) {
            setMenuState(false);
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && navigation.classList.contains("is-menu-open")) {
            setMenuState(false);
        }
    });
}
