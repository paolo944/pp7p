let subEventSource = null;

function setupSubEventSource() {
    if (subEventSource) subEventSource.close();

    subEventSource = new EventSource('/api/sub');

    subEventSource.onopen = () => {
        console.log('Connexion à /api/sub établie');
    };

    subEventSource.onmessage = event => {
        try {
            const data = JSON.parse(event.data);
            handleSubSlideData(data['status/slide']);
        } catch (err) {
            console.error('Erreur parsing sub slide:', err);
        }
    };

    subEventSource.onerror = event => {
        console.warn('Déconnecté de /api/sub, tentative de reconnexion...');
        subEventSource.close();
        setTimeout(setupSubEventSource, 5000);
    };
}

function handleSubSlideData(slide) {
    const subtitleElement = document.getElementById("subtitle");
    subtitleElement.innerHTML = "";

    if (!slide || !slide.type) {
        console.warn("Aucun slide valide:", slide);
        return;
    }

    if (slide.type === "louanges") {
        document.body.classList.remove('light-mode');
        subtitleElement.classList.add("louanges");

        const louanges = document.createElement('p');
        louanges.textContent = slide.subtitle;
        subtitleElement.appendChild(louanges);

    } else if (slide.type === "versets") {
        document.body.classList.add('light-mode');
        subtitleElement.classList.remove("louanges");

        const versetsContainer = document.createElement('p');
        versetsContainer.textContent = slide.versets;

        const refContainer = document.createElement('p');
        refContainer.classList.add('refs');
        refContainer.textContent = slide.ref;

        subtitleElement.appendChild(versetsContainer);
        subtitleElement.appendChild(refContainer);

    } else {
        console.warn("Type de slide non reconnu:", slide.type);
    }
}

// Lancer au chargement de la page
setupSubEventSource();