import threading
import json
import time
import asyncio

incoming_data_dict = {
    "timer/system_time": 0,
    "status/slide": ""
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
    text = text.splitlines()

    if data_final["type"] == "louanges":
        paroles = [text[i] for i in range(0, len(text), 2)]
        if len(paroles) > 2:
            return ""
        data_final["subtitle"] = "\n".join(paroles)
    elif data_final["type"] == "versets":
        ref = text[-1]
        versets = text[0]
        data_final["ref"] = ref
        data_final["versets"] = versets
    
    return data_final

def process_data(queues, loop):
    timer_val = 0
    while True:
        if incoming_data_dict:
            if timer_val == incoming_data_dict["timer/system_time"]:
                time.sleep(0.01)
                continue
            timer_val = incoming_data_dict["timer/system_time"]

            parsed_data = safe_parse(incoming_data_dict["status/slide"])
            try:
                processed_data = process_slide(parsed_data)
                for key, value in processed_data.items():
                    if key in queues and value is not None:
                        asyncio.run_coroutine_threadsafe(
                            queues.put({"status/slide": value}), loop
                        )
            except Exception as e:
                print(f"[ERROR] Handler failed for status/slide with data: {parsed_data} -> {e}")
        else:
            time.sleep(0.01)


def start_dispatcher(queues: dict, loop):
    dispatcher_thread = threading.Thread(
        target=process_data, args=(queues, loop)
    )
    dispatcher_thread.daemon = True
    dispatcher_thread.start()
