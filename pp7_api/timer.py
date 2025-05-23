import json
import socket

class Timer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
                    
    def play(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}/start", "method": "GET"}, separators=(',', ':')) + "\r\n"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(msg.encode('utf-8'))
                response = s.recv(1024)

                if response.decode('utf-8'):
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    print(f"Timer: {uuid} lancé")
                    return True
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False


    def pause(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}/stop", "method": "GET"}, separators=(',', ':')) + "\r\n"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(msg.encode('utf-8'))
                response = s.recv(1024)

                if response.decode('utf-8'):
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    print(f"Timer: {uuid} stoppé")
                    return True
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False

    def reset(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}/reset", "method": "GET"}, separators=(',', ':')) + "\r\n"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(msg.encode('utf-8'))
                response = s.recv(1024)

                if response.decode('utf-8'):
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    print(f"Timer: {uuid} lancé")
                    return True
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False

    def delete(self, uuid):
        msg = json.dumps({"url": f"v1/timer/{uuid}", "method": "DELETE"}, separators=(',', ':')) + "\r\n"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(msg.encode('utf-8'))
                response = s.recv(1024)

                if response.decode('utf-8'):
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    print(f"Timer: {uuid} supprimé")
                    return True
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False

    def post(self, data):
        headers = {
            'Content-Type': 'application/json',
            'accept': '*/*'
        }

        hours = data.get('hours')
        minutes = data.get('minutes')
        seconds = data.get('seconds')
        name = data.get('clock_name')

        try:
            seconds = int(seconds)
        except:
            seconds = 0
        try:
            seconds += int(minutes) * 60
        except:
            seconds += 0
        try:
            seconds += int(hours) * 3600
        except:
            seconds += 0

        data = {
            "allows_overrun": True,
            "countdown": {
                "duration": seconds
            },
            "name": name
        }

        msg = json.dumps({"url": f"v1/timers", "method": "POST", "body": data}, separators=(',', ':')) + "\r\n"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.send(msg.encode('utf-8'))
                response = s.recv(1024)
                print(response)

                if response.decode('utf-8'):
                    print(f"Timer: {name} ajouté")
                    return True
                else:
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False
    