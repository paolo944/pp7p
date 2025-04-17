import threading
import socket
import json
from .dispatcher import incoming_data_dict

def _read_api_stream(host, port, urls):
    try:
        with socket.create_connection((host, port)) as sock:
            buffer = ""

            msg = json.dumps({
                "url": "v1/status/updates",
                "method": "POST",
                "body": urls,
                "chunked": True
            }, separators=(',', ':')) + "\r\n"

            sock.send(msg.encode('utf-8'))
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

                        url = parsed.get("data").get("url")
                        data = parsed.get("data").get("data")

                        #print(f"{url}: {data}")

                        if url and data:
                            incoming_data_dict[url] = data
                            #print(f"incoming_data: {incoming_data_dict}\n\n")

                    except json.JSONDecodeError:
                        print(f"[TCP] JSON invalide: {line}")
                        continue

    except Exception as e:
        print(f"[TCP] Erreur de connexion: {e}")

def start_api_stream(host='localhost', port=9000):
    urls = [
        "stage/message",
        "timers/current",
        "timer/video_countdown",
        "timer/system_time",
        "status/slide",
        "presentation/active"
    ]
    thread = threading.Thread(target=_read_api_stream, args=(host, port, urls), daemon=True)
    thread.start()
