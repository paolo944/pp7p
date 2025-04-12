import threading

incoming_data_dict = {
            "stage/message": "",
            "timers/current": "",
            "timer/video_countdown": "",
            "timer/system_time": 0,
            "status/slide": "",
            "presentation/active": ""
            }
ready_data = {'prompt': {}, 'sub': {}, 'status': {}}

def process_slide(data):
    data_final = {}
    text = data["current"]["text"]
    data_final["type"] = "versets" if any(char.isdigit() for char in text) else "louanges"
    
    if data_final["type"] == "louanges":
        paroles = text.split('\n')
        paroles = [paroles[i] for i in range(0, len(paroles), 2)]
        paroles = '\n'.join(paroles)
        data_final["subtitle"] = paroles
    elif data_final["type"] == "versets":
        text = text.split('\r')
        ref = text[3]
        versets = text[0]
        data_final["ref"] = ref
        data_final["versets"] = versets
    
    data = {'prompt': data_final, 'sub': data_final, 'status': data_final}
    return data

url_handlers = {
    'timer/system_time': lambda data: {'prompt': data, 'sub': data, 'status': data},
    'stage/message': lambda data: {'status': data},
    'timer/video_countdown': lambda data: {'status': data},
    'timers/current': lambda data: {'status': data},
    'presentation/active': lambda data: {'status': data["presentation"]["id"]["name"] if data is not None else None},
    'status/slide': process_slide,
}

def process_data():
    timer = 0
    while True:
        if incoming_data_dict:
            new_timer = int(incoming_data_dict.get('timer/system_time', timer))
            if new_timer == timer:
                continue
            timer = new_timer

            for url, data in incoming_data_dict.items():
                handler = url_handlers.get(url)
                if handler:
                    processed_data = handler(data)
                    for key, value in processed_data.items():
                        ready_data[key][url] = value

def start_dispatcher():
    dispatcher_thread = threading.Thread(target=process_data)
    dispatcher_thread.daemon = True
    dispatcher_thread.start()
