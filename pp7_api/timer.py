import json
import socket

class Timer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _send_request(self, msg, success_msg=None, fail_msg=None):
        """Envoie un message JSON au serveur et ne renvoie que si échec."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)  # timeout 200ms
                s.connect((self.host, self.port))
                s.sendall(msg.encode('utf-8'))

                try:
                    response = s.recv(1024)
                    if response:
                        print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                        return False
                except socket.timeout:
                    # Pas de réponse → succès
                    pass

                if success_msg:
                    print(success_msg)
                return True

        except Exception as e:
            if fail_msg:
                print(f"{fail_msg}: {e}")
            else:
                print(f'Erreur lors de l\'envoi du message: {e}')
            return False

    def play(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}/start", "method": "GET"}, separators=(',', ':')) + "\r\n"
        return self._send_request(msg, success_msg=f"Timer: {uuid} lancé")

    def pause(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}/stop", "method": "GET"}, separators=(',', ':')) + "\r\n"
        return self._send_request(msg, success_msg=f"Timer: {uuid} stoppé")

    def reset(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}/reset", "method": "GET"}, separators=(',', ':')) + "\r\n"
        return self._send_request(msg, success_msg=f"Timer: {uuid} réinitialisé")

    def delete(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}", "method": "DELETE"}, separators=(',', ':')) + "\r\n"
        return self._send_request(msg, success_msg=f"Timer: {uuid} supprimé")

    def post(self, data):
        hours = int(data.get('hours', 0))
        minutes = int(data.get('minutes', 0))
        seconds = int(data.get('seconds', 0))
        name = data.get('clock_name', '')

        total_seconds = hours * 3600 + minutes * 60 + seconds

        body = {
            "allows_overrun": True,
            "countdown": {"duration": total_seconds},
            "name": name
        }

        msg = json.dumps({"url": "v1/timers", "method": "POST", "body": body}, separators=(',', ':')) + "\r\n"
        return self._send_request(msg, success_msg=f"Timer: {name} ajouté")
