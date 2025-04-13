const eventSource = new EventSource('/api/sub');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const subtitleElement = document.getElementById("subtitle");
    subtitleElement.innerHTML = ""
    if(data.type == "louanges"){
        document.body.classList.remove('light-mode');
        subtitleElement.classList.add("louanges");
        const louanges = document.createElement('p');
        louanges.textContent = data.subtitle;
        subtitleElement.appendChild(louanges);
    }
    else if(data.type == "versets"){
        document.body.classList.add('light-mode');
        subtitleElement.classList.remove('louanges');
        const refContainer = document.createElement('p');
        const versetsContainer = document.createElement('p');
        refContainer.classList.add('refs');
        refContainer.textContent = data.ref;
        versetsContainer.textContent = data.versets
        subtitleElement.appendChild(versetsContainer);
        subtitleElement.appendChild(refContainer);
    }
    else{
        console.error(data);
    }
};

eventSource.onerror = function(event) {
    console.error('EventSource failed:', event);
};