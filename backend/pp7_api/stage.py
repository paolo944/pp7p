import json
import socket

class Stage:
    def __init__(self):
        with open('info.json', 'r') as config_file:
            config = json.load(config_file)
            self.host = config["host"]
            self.port = config["port"]

    def send_msg(self, msg):
        if not isinstance(msg, str):
            print("Erreur, le message doit être une string")
            return False

        msg = json.dumps({"url": "v1/stage/message", "method": "PUT", "body": msg, "chunked": False}, separetors=(',', ':'))

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(msg.encode('utf-8'))
                response = s.recv(1024)

                if response.decode('utf-8'):
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    print(f"Message envoyé au prompteur: {msg}")
                    return True
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False

    def delete_msg(self):
        msg = json.dumps({"url": "v1/stage/message", "method": "DELETE"}, separetors=(',', ':'))

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(msg.encode('utf-8'))
                response = s.recv(1024)

                if response.decode('utf-8'):
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    print("Message Supprimé du prompteur")
                    return True
        except Exception as e:
            print(f'Erreur lors de la suppression du message: {e}')
            return False
