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
        const formattedTime = date.toLocaleTimeString('fr-FR', { hour12: false });
        timeContainer.textContent = "Heure: " + formattedTime;
    }

    if (data["stage/message"]) {
        const msg = data["stage/message"];
        messageContainer.textContent = msg ? "Message prompteur: " + msg : "";
    }

    if (data["timers/current"]) {
        data["timers/current"].forEach(updateOrCreateClock);
    }

    if (data["timer/video_countdown"]) {
        videoContainer.innerHTML = "";
        const vTimer = data["timer/video_countdown"];
        if (vTimer !== "0:00:00") {
            const span = document.createElement('span');
            span.textContent = vTimer;
            if (parseInt(vTimer.slice(-2)) < 11) {
                span.classList.add('blinking');
            }
            videoContainer.appendChild(document.createTextNode("Temps restant vidéo: "));
            videoContainer.appendChild(span);
        }
    }

    if (data["status/slide"]) {
        slideContainer.innerHTML = "";
        const slide = data["status/slide"];
        if (slide?.subtitle) {
            const current = document.createElement('h3');
            current.textContent = `Slide actuelle: ${slide.subtitle}`;
            slideContainer.appendChild(current);
        }
    }

    if (data["presentation/active"]) {
        presentationContainer.textContent = `titre presentation: ${data["presentation/active"]}`;
    }
}

function updateOrCreateClock(timer) {
    let clock = document.getElementById(timer.id.name);
    const container = document.getElementById('clock-container');

    if (!clock) {
        clock = document.createElement('div');
        clock.id = timer.id.name;
        clock.classList.add('clock-container');

        const h3 = document.createElement('h3');
        h3.textContent = `${timer.id.name}: `;

        const time = document.createElement('span');
        time.className = 'time';
        time.textContent = timer.time;
        h3.appendChild(time);

        const pauseBtn = createControlButton(timer, 'pause');
        const resetBtn = createControlButton(timer, 'reset');
        const deleteBtn = createControlButton(timer, 'delete');

        const btns = document.createElement('div');
        btns.classList.add('buttons-container');
        btns.append(pauseBtn, resetBtn, deleteBtn);

        clock.append(h3, btns);
        container.appendChild(clock);
        existingClocks.set(timer.id.name, clock);
    } else {
        clock.querySelector('.time').textContent = timer.time;
    }

    const time = clock.querySelector('.time');
    time.className = 'time';
    switch (timer.state) {
        case 'running': time.classList.add('status-running'); break;
        case 'overrunning':
        case 'overran': time.classList.add('status-overrun'); break;
        case 'stopped': time.classList.add('status-stopped'); break;
    }
}

function createControlButton(timer, type) {
    const btn = document.createElement('button');
    btn.classList.add('button-container');
    const icon = document.createElement('i');

    switch (type) {
        case 'pause':
            icon.classList.add('fa-solid', timer.state === 'stopped' ? 'fa-play' : 'fa-stop');
            btn.onclick = () => (timer.state === 'stopped' ? playTimer(timer.id.uuid) : pauseTimer(timer.id.uuid));
            break;
        case 'reset':
            icon.classList.add('fa-solid', 'fa-rotate');
            btn.onclick = () => resetTimer(timer.id.uuid);
            break;
        case 'delete':
            icon.classList.add('fa-solid', 'fa-trash');
            btn.onclick = () => deleteTimer(timer.id.uuid, timer.id.name);
            break;
    }

    btn.appendChild(icon);
    return btn;
}

// Timer API actions
function pauseTimer(uuid) {
    fetchWithLoader(`/api/timer/pause/${uuid}`, { method: 'GET' });
}

function playTimer(uuid) {
    fetchWithLoader(`/api/timer/play/${uuid}`, { method: 'GET' });
}

function resetTimer(uuid) {
    fetchWithLoader(`/api/timer/reset/${uuid}`, { method: 'GET' });
}

function deleteTimer(uuid, id) {
    fetchWithLoader(`/api/timer/${uuid}`, { method: 'DELETE' })
    .then(() => removeClock(id));
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
