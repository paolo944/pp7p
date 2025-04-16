import threading
import json

incoming_data_dict = {
            "v1/stage/message": "",
            "v1/timers/current": "",
            "v1/timer/video_countdown": "",
            "v1/timer/system_time": 0,
            "v1/status/slide": "",
            "v1/presentation/active": ""
            }

ready_data = {'prompt': {}, 'sub': {}, 'status': {}}

def safe_parse(data):
    if isinstance(data, str):
        stripped = data.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                print(f"[WARNING] JSON mal formé: {data}")
                return {}
        else:
            return data
    return data

def process_slide(data):
    text = data["current"]["text"]
    data_final = {}
    data_final["type"] = "versets" if any(char.isdigit() for char in text) else "louanges"
    
    if data_final["type"] == "louanges":
        paroles = text.split('\n')
        paroles = [paroles[i] for i in range(0, len(paroles), 2)]
        paroles = '\n'.join(paroles)
        data_final["subtitle"] = paroles
    elif data_final["type"] == "versets":
        text = text.split('\r')
        ref = text[-1]
        versets = text[0]
        data_final["ref"] = ref
        data_final["versets"] = versets
    
    data = {'prompt': data_final, 'sub': data_final, 'status': data_final}
    return data

url_handlers = {
    'v1/timer/system_time': lambda data: {'prompt': data, 'sub': data, 'status': data},
    'v1/stage/message': lambda data: {'status': data},
    'v1/timer/video_countdown': lambda data: {'status': data},
    'v1/timers/current': lambda data: {'status': data},
    'v1/presentation/active': lambda data: {
        'status': (
            data.get("presentation", {}).get("id", {}).get("name")
            if isinstance(data, dict) else None
        )
    },    
    'v1/status/slide': process_slide,
}

def process_data():
    timer = 0
    while True:
        if incoming_data_dict:
            if timer == incoming_data_dict["v1/timer/system_time"]:
                continue
            timer = incoming_data_dict["v1/timer/system_time"]
            for url, data in incoming_data_dict.items():
                parsed_data = safe_parse(data)
                handler = url_handlers.get(url)
                if handler:
                    try:
                        processed_data = handler(parsed_data)
                        for key, value in processed_data.items():
                            ready_data[key][url] = value
                    except Exception as e:
                        print(f"[ERROR] Handler failed for {url} with data: {parsed_data} -> {e}")


def start_dispatcher():
    dispatcher_thread = threading.Thread(target=process_data)
    dispatcher_thread.daemon = True
    dispatcher_thread.start()
