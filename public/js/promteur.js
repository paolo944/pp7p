let promptEventSrouce = null;

function setupPromptEventSource() {
    if(promptEventSrouce) promptEventSrouce.close();

    promptEventSource = new EventSource('/api/prompt');

    promptEventSource.onopen = () => {
        console.log('Connexion à /api/sub établie');
    };

    promptEventSource.onmessage = event => {
        try {
            const data = JSON.parse(event.data);
            handlePromptData(data);
        } catch (err) {
            console.error('Erreur parsing sub slide:', err);
        }
    };

    promptEventSource.onerror = event => {
        console.warn('Déconnecté de /api/prompt, tentative de reconnexion...');
        promptEventSource.close();
        setTimeout(setupPromptEventSource, 5000);
    };
}

function handlePromptData(data) {
    const prompteur = document.getElementById('prompteur'); // Ajouté ici
    const timeContainer = document.getElementById('time-container');
    const messageContainer = document.getElementById('stage-message-container');
    const clockContainer = document.getElementById('clock-container');
    const slideContainer = document.getElementById('slide-text-container');

    if (data["timer/system_time"]) {
        const date = new Date(data["timer/system_time"] * 1000);
        timeContainer.textContent = date.toLocaleTimeString('fr-FR', { hour12: false });
    }

    if (data["stage/message"]) {
        messageContainer.textContent = data["stage/message"] ? data["stage/message"] : "";
    }

    if (data["timers/current"]) {
        clockContainer.textContent = data["timers/current"][0]["time"];

        const timerState = data["timers/current"][0]["state"];
        if (timerState === "overrunning" || timerState === "overrunn") {
            clockContainer.classList.add('overtime');
        } else {
            clockContainer.classList.remove('overtime');
        }
    }

    if (data["status/slide"].subtitle !== undefined) {
        slideContainer.innerHTML = `${data["status/slide"].subtitle}`;

        if (data["status/slide"].subtitle.trim() !== '') {
            prompteur.classList.add('has-text');
            prompteur.classList.remove('no-text');
        } else {
            prompteur.classList.remove('has-text');
        }
    }
}

// Lancer au chargement de la page
setupPromptEventSource();