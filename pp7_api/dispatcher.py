import threading
import json
import time
import asyncio
import re

incoming_data_dict = {
    "timer/system_time": 0,
    "status/slide": "",
    "media/playlist/active": ""
}

media_playing = False
playing_media_name = ""

# How to play video to declink: ffmpeg -i test.avi -f decklink -pix_fmt uyvy422 'DeckLink Mini Monitor'
# How to stream an image: ffmpeg -loop 1 -re -i input.jpg -f decklink -pix_fmt uyvy422 -s 1920x1080 -r 25 "DeckLink Duo (1)"
# To stream on the screen: SDL_VIDEO_FULLSCREEN_DISPLAY=1 ffplay -loop 1 -framerate 25 -i input.jpg -fs -noborder

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
    data_final["type"] = "versets" if re.search(r'\b\d{1,3}:\d{1,3}', text) else "louanges"
    text = text.splitlines()

    if len(text) > 4:
        return ""

    if data_final["type"] == "louanges":
        paroles = [text[i] for i in range(0, len(text), 2)]
        data_final["subtitle"] = "\n".join(paroles)
    elif data_final["type"] == "versets":
        ref = text[-1]
        versets = text[0]
        data_final["ref"] = ref
        data_final["versets"] = versets
    
    return data_final

def process_data(queues, loop, media):
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
                asyncio.run_coroutine_threadsafe(
                    queues.put({"status/slide": processed_data}), loop
                )
            except Exception as e:
                print(f"[ERROR] Handler failed for status/slide with data: {parsed_data} -> {e}")

            # for lookup in media:
            #     if lookup["lookUp"] == incoming_data_dict["media/playlist/active"]["item"]["name"]:
            #         if media_playing:
            #             continue
            #         else:
            #             #Jouer media avec ffmpeg
                
        else:
            time.sleep(0.01)


def start_dispatcher(queues: dict, loop, media):
    dispatcher_thread = threading.Thread(
        target=process_data, args=(queues, loop, media)
    )
    dispatcher_thread.daemon = True
    dispatcher_thread.start()
