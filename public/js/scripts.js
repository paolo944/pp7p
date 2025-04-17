let editor_mode = true;
const existingClocks = new Map();
let eventSource = null;

// Loader Utils
function showLoader(show) {
    const loader = document.getElementById('loader');
    if (loader) loader.style.display = show ? 'block' : 'none';
}

function fetchWithLoader(url, options) {
    showLoader(true);
    return fetch(url, options).finally(() => showLoader(false));
}

function removeClock(id) {
    existingClocks.delete(id);
    const element = document.getElementById(id);
    if (element) element.remove();
}

document.getElementById("stage_msg").addEventListener('submit', function(event) {
    event.preventDefault();

    const userInput = document.getElementById('user-stage-msg').value;
    const buttonId = event.submitter ? event.submitter.id : event.target.id;

    const resultContainer = document.getElementById('result-container');

    if(buttonId === "send") {
        fetchWithLoader('/api/stage/msg', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_input: userInput })
        })
        .then(res => res.json())
        .then(data => {
            resultContainer.innerHTML = data.result ? "" : "Erreur, message non envoyé";
        })
        .catch(err => console.error('Erreur:', err));
    }
    else if(buttonId === "delete") {
        fetchWithLoader('/api/stage/msg', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if(data.result) {
                resultContainer.innerHTML = '';
                document.getElementById('user-stage-msg').placeholder = 'Envoyer msg prompteur';
            } else {
                resultContainer.innerHTML = "Erreur, message non supprimé";
            }
        })
        .catch(err => console.error('Erreur:', err));
    }
});

document.getElementById('submit-button').addEventListener('click', () => {
    const timeData = {
        clock_name: document.getElementById('clock_name').value,
        hours: document.getElementById('hours').value,
        minutes: document.getElementById('minutes').value,
        seconds: document.getElementById('seconds').value
    };

    fetchWithLoader('/api/timer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(timeData)
    })
    .then(res => res.json())
    .then(data => console.log('Clock ajoutée:', data))
    .catch(err => console.error('Erreur:', err));
});

function setupEventSource() {
    if (eventSource) eventSource.close();

    eventSource = new EventSource('/api/status');

    eventSource.onopen = () => console.log('EventSource ouvert');

    eventSource.onmessage = event => {
        try {
            const data = JSON.parse(event.data);
            updateUIFromData(data);
        } catch (e) {
            console.error('Erreur de parsing:', e);
        }
    };

    eventSource.onerror = () => {
        console.warn('Déconnecté, tentative de reconnexion...');
        eventSource.close();
        setTimeout(setupEventSource, 5000); // retry
    };
}

function updateUIFromData(data) {
    const timeContainer = document.getElementById('time-container');
    const messageContainer = document.getElementById('stage-message-container');
    const videoContainer = document.getElementById('video-container');
    const slideContainer = document.getElementById('slide-text-container');
    const presentationContainer = document.getElementById('presentation-container');

    if (data["timer/system_time"]) {
        const date = new Date(data["timer/system_time"] * 1000);
        timeContainer.textContent = "Heure: " + date.toLocaleTimeString('fr-FR', { hour12: false });
    }

    if (data["stage/message"]) {
        messageContainer.textContent = data["stage/message"] ? "Message prompteur: " + data["stage/message"] : "";
    }

    const timers = data["timers/current"] || [];

    // SUPPRESSION des clocks qui n'existent plus
    const serverClocks = new Set(timers.map(t => t.id.name));
    for (const [name, clock] of existingClocks.entries()) {
        if (!serverClocks.has(name)) {
            clock.remove();
            existingClocks.delete(name);
        }
    }

    // CREATION ou MISE À JOUR des clocks existantes
    timers.forEach(updateOrCreateClock);

    if (data["timer/video_countdown"]) {
        const vTimer = data["timer/video_countdown"];
        videoContainer.innerHTML = vTimer !== "0:00:00" ? `
            Temps restant vidéo: <span class="${parseInt(vTimer.slice(-2)) < 11 ? 'blinking' : ''}">${vTimer}</span>
        ` : '';
    }

    if (data["status/slide"]?.subtitle) {
        slideContainer.innerHTML = `<h3>Slide actuelle: ${data["status/slide"].subtitle}</h3>`;
    }

    if (data["presentation/active"]) {
        presentationContainer.textContent = `titre presentation: ${data["presentation/active"]}`;
    }
}


function updateOrCreateClock(timer) {
    let clock = existingClocks.get(timer.id.name);
    const container = document.getElementById('clock-container');

    if (!clock) {
        clock = document.createElement('div');
        clock.id = timer.id.name;
        clock.classList.add('clock-container');

        const h3 = document.createElement('h3');
        h3.innerHTML = `${timer.id.name}: <span class="time"></span>`;

        const pauseBtn = createControlButton(timer, 'pause');
        const resetBtn = createControlButton(timer, 'reset');
        const deleteBtn = createControlButton(timer, 'delete');

        const btns = document.createElement('div');
        btns.classList.add('buttons-container');
        btns.append(pauseBtn, resetBtn, deleteBtn);

        clock.append(h3, btns);
        container.appendChild(clock);
        existingClocks.set(timer.id.name, clock);
    }

    // Toujours mettre à jour le texte et les classes
    const timeSpan = clock.querySelector('.time');
    timeSpan.textContent = timer.time;
    timeSpan.className = 'time'; // reset classes
    switch (timer.state) {
        case 'running': timeSpan.classList.add('status-running'); break;
        case 'overrunning':
        case 'overran': timeSpan.classList.add('status-overrun'); break;
        case 'stopped': timeSpan.classList.add('status-stopped'); break;
    }

    // Mettre à jour bouton play/pause existant
    const pauseBtn = clock.querySelector('.pause-btn');
    if (pauseBtn) {
        const icon = pauseBtn.querySelector('i');
        if (timer.state === 'running') {
            icon.className = 'fa-solid fa-stop';
            pauseBtn.dataset.state = 'running';
        } else {
            icon.className = 'fa-solid fa-play';
            pauseBtn.dataset.state = 'stopped';
        }
    }
}

function createControlButton(timer, type) {
    const btn = document.createElement('button');
    btn.classList.add('button-container');
    const icon = document.createElement('i');

    switch (type) {
        case 'pause':
            icon.classList.add('fa-solid', timer.state === 'stopped' ? 'fa-play' : 'fa-stop');
            btn.appendChild(icon);
            btn.classList.add('pause-btn'); // utile pour le retrouver plus tard
            btn.dataset.uuid = timer.id.uuid;
            btn.dataset.state = timer.state; // sauvegarde l'état localement
            btn.onclick = () => toggleTimerState(btn);
            break;
        case 'reset':
            icon.classList.add('fa-solid', 'fa-rotate');
            btn.onclick = () => resetTimer(timer.id.uuid);
            btn.appendChild(icon);
            break;
        case 'delete':
            icon.classList.add('fa-solid', 'fa-trash');
            btn.onclick = () => deleteTimer(timer.id.uuid, timer.id.name);
            btn.appendChild(icon);
            break;
    }

    return btn;
}

// Timer API actions
function toggleTimerState(btn) {
    const icon = btn.querySelector('i');
    const uuid = btn.dataset.uuid;
    const currentState = btn.dataset.state;

    if (currentState === 'stopped') {
        // On est stoppé, donc on veut jouer
        fetchWithLoader(`/api/timer/play/${uuid}`, { method: 'GET' })
            .then(() => {
                icon.className = 'fa-solid fa-stop';
                btn.dataset.state = 'running';
            });
    } else {
        // On est en cours, donc on veut pause
        fetchWithLoader(`/api/timer/pause/${uuid}`, { method: 'GET' })
            .then(() => {
                icon.className = 'fa-solid fa-play';
                btn.dataset.state = 'stopped';
            });
    }
}

function resetTimer(uuid) {
    fetchWithLoader(`/api/timer/reset/${uuid}`, { method: 'GET' });
}

function deleteTimer(uuid, id) {
    fetchWithLoader(`/api/timer/${uuid}`, { method: 'DELETE' })
    .then(res => {
        if (res.ok) {
            removeClock(id);
        } else {
            console.error("Erreur lors de la suppression du timer");
        }
    });
}

// UI toggles
document.getElementById('toggle-dark-mode').addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    const icon = document.getElementById('toggle-dark-mode').querySelector('i');
    icon.classList.toggle('fa-sun');
    icon.classList.toggle('fa-moon');
});

document.getElementById('toggle-language').addEventListener('click', () => {
    const btn = document.getElementById('toggle-language');
    if (btn.textContent === 'Français') {
        btn.textContent = 'English';
        changeLanguageToEnglish();
    } else {
        btn.textContent = 'Français';
        changeLanguageToFrench();
    }
});

document.getElementById('toggle-editor-mode').addEventListener('click', () => {
    document.getElementById('clock-editor').classList.toggle('invisible');
    document.getElementById('clock-container').classList.toggle('invisible-clock');
    editor_mode = !editor_mode;
});

document.getElementById('joke').addEventListener('click', () => {
    fetchWithLoader(`/api/joke`, { method: 'GET' })
    .then(res => res.json())
    .then(() => alert('Very funny!'))
    .catch(() => console.error('your joke didn\'t work'));
});

function changeLanguageToEnglish() {
    document.querySelector('h1').textContent = 'Client PP7 Hillsong Paris';
    document.getElementById('user-stage-msg').placeholder = 'Send prompt message';
    document.getElementById('send').textContent = 'Send';
    document.getElementById('delete').textContent = 'Delete';
    document.querySelector('.form-container h2').textContent = 'Add Clock';
    document.querySelector('label[for="clock_name"]').textContent = 'Name';
    document.querySelector('label[for="hours"]').textContent = 'Hours:';
    document.querySelector('label[for="minutes"]').textContent = 'Minutes:';
    document.querySelector('label[for="seconds"]').textContent = 'Seconds:';
    document.getElementById('submit-button').textContent = 'Add';
}

function changeLanguageToFrench() {
    document.querySelector('h1').textContent = 'Client PP7 Hillsong Paris';
    document.getElementById('user-stage-msg').placeholder = 'Envoyer msg prompteur';
    document.getElementById('send').textContent = 'Envoyer';
    document.getElementById('delete').textContent = 'Supprimer';
    document.querySelector('.form-container h2').textContent = 'Ajouter Clock';
    document.querySelector('label[for="clock_name"]').textContent = 'Nom';
    document.querySelector('label[for="hours"]').textContent = 'Heures:';
    document.querySelector('label[for="minutes"]').textContent = 'Minutes:';
    document.querySelector('label[for="seconds"]').textContent = 'Secondes:';
    document.getElementById('submit-button').textContent = 'Ajouter';
}

setupEventSource();
