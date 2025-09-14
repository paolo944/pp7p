import threading
import json
import time
import asyncio

incoming_data_dict = {
    "stage/message": "",
    "timers/current": "",
    "timer/video_countdown": "",
    "timer/system_time": 0,
    "status/slide": "",
    "presentation/active": "",
}

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
        paroles = text.splitlines()
        print(text)
        paroles = [paroles[i] for i in range(0, len(paroles), 2)]
        data_final["subtitle"] = "\n".join(paroles)
    elif data_final["type"] == "versets":
        text = text.split("\r")
        ref = text[-1]
        versets = text[0]
        data_final["ref"] = ref
        data_final["versets"] = versets
    
    return {"prompt": data_final, "sub": data_final, "status": data_final}

url_handlers = {
    "timer/system_time": lambda data: {"prompt": data, "sub": data, "status": data},
    "stage/message": lambda data: {"prompt": data, "status": data},
    "timer/video_countdown": lambda data: {"status": data},
    "timers/current": lambda data: {"prompt": data, "status": data},
    "presentation/active": lambda data: {
        "status": (
            data.get("presentation", {}).get("id", {}).get("name")
            if isinstance(data, dict) and data.get("presentation") is not None
            else None
        )
    },
    "status/slide": process_slide,
}

def process_data(queues: dict, loop):
    timer_val = 0
    while True:
        if incoming_data_dict:
            if timer_val == incoming_data_dict["timer/system_time"]:
                time.sleep(0.01)
                continue
            timer_val = incoming_data_dict["timer/system_time"]

            for url, data in incoming_data_dict.items():
                parsed_data = safe_parse(data)
                handler = url_handlers.get(url)
                if handler:
                    try:
                        processed_data = handler(parsed_data)
                        for key, value in processed_data.items():
                            if key in queues and value is not None:
                                asyncio.run_coroutine_threadsafe(
                                    queues[key].put({url: value}), loop
                                )
                    except Exception as e:
                        print(f"[ERROR] Handler failed for {url} with data: {parsed_data} -> {e}")
        else:
            time.sleep(0.01)


def start_dispatcher(queues: dict, loop):
    dispatcher_thread = threading.Thread(
        target=process_data, args=(queues, loop)
    )
    dispatcher_thread.daemon = True
    dispatcher_thread.start()
