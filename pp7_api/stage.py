import json
import socket

class Stage:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_msg(self, msg):
        if not isinstance(msg, str):
            print("Erreur, le message doit être une string")
            return False

        request = json.dumps({
            "url": "v1/stage/message",
            "method": "PUT",
            "body": msg
        }, separators=(',', ':')) + "\r\n"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((self.host, int(self.port)))
                except Exception as e:
                    print("Impossible de se connecter:", e)

                s.send(request.encode('utf-8'))
                response = s.recv(1024)

                print(f"rep: {response}")

                if response.decode():
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    #print(f"Message envoyé au prompteur: {msg}")
                    return True
        except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False

    def delete_msg(self):
        request = json.dumps({
            "url": "v1/stage/message",
            "method": "DELETE"
        }, separators=(',', ':')) + "\r\n"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((self.host, int(self.port)))
                except Exception as e:
                    print("Impossible de se connecter:", e)

                s.send(request.encode('utf-8'))
                response = s.recv(1024)

                if response.decode():
                    print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                    return False
                else:
                    #print("Message Supprimé du prompteur")
                    return True
        except Exception as e:
            print(f'Erreur lors de la suppression du message: {e}')
            return False
