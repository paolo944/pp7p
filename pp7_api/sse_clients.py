import threading
import socket
import json
from .dispatcher import incoming_data_dict

def _read_api_stream(host, port):
    urls = [
            "stage/message",
            "timers/current",
            "timer/video_countdown",
            "timer/system_time",
            "status/slide",
            "presentation/active"
    ]
    try:
        with socket.create_connection((host, port)) as sock:
            buffer = ""

            msg = json.dumps({
                "url": "v1/status/updates",
                "method": "POST",
                "body": urls,
                "chunked": True
            }, separators=(',', ':'))

            sock.sendall(msg.encode('utf-8'))

            while True:
                chunk = sock.recv(1024).decode('utf-8')
                if not chunk:
                    break

                buffer += chunk

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        parsed = json.loads(line)

                        if 'error' in parsed:
                            print(f"[API Error] {parsed['error']}")
                            continue

                        url = parsed.get("url")
                        data = parsed.get("data")

                        if url and data:
                            if url in incoming_data_dict:
                                incoming_data_dict.move_to_end(url)
                                incoming_data_dict[url] = data
                            else:
                                incoming_data_dict[url] = data

                            if len(incoming_data_dict) > MAX_URLS:
                                incoming_data_dict.popitem(last=False)
                    except json.JSONDecodeError:
                        print(f"[TCP] JSON invalide: {line}")
                        continue

    except Exception as e:
        print(f"[TCP] Erreur de connexion: {e}")

def start_api_stream(host='localhost', port=9000):
    thread = threading.Thread(target=_read_api_stream, args=(host, port), daemon=True)
    thread.start()
