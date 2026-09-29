let deferredInstallPrompt = null;

function getInstallButtons() {
    return document.querySelectorAll("[data-install-app]");
}

function hideInstallButtons() {
    getInstallButtons().forEach(function (button) {
        button.classList.add("d-none");
    });
}

function showInstallButtons() {
    getInstallButtons().forEach(function (button) {
        button.classList.remove("d-none");
    });
}

function isStandaloneMode() {
    return (
        window.matchMedia("(display-mode: standalone)").matches ||
        window.navigator.standalone === true
    );
}

window.addEventListener("beforeinstallprompt", function (event) {
    event.preventDefault();

    deferredInstallPrompt = event;

    if (!isStandaloneMode()) {
        showInstallButtons();
    }
});

window.addEventListener("appinstalled", function () {
    deferredInstallPrompt = null;
    hideInstallButtons();
});

document.addEventListener("click", async function (event) {
    const button = event.target.closest("[data-install-app]");

    if (!button || !deferredInstallPrompt) {
        return;
    }

    deferredInstallPrompt.prompt();

    try {
        await deferredInstallPrompt.userChoice;
    } finally {
        deferredInstallPrompt = null;
        hideInstallButtons();
    }
});

window.addEventListener("load", function () {
    if (isStandaloneMode()) {
        hideInstallButtons();
    }

    if ("serviceWorker" in navigator) {
        navigator.serviceWorker
            .register("/service-worker.js")
            .catch(function (error) {
                console.error(
                    "Service worker registration failed:",
                    error
                );
            });
    }
});