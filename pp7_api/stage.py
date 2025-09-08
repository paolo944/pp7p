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
                s.settimeout(0.2)
                try:
                    s.connect((self.host, int(self.port)))
                except Exception as e:
                    print("Impossible de se connecter:", e)
                    return False

                s.sendall(request.encode('utf-8'))

                try:
                    response = s.recv(1024)
                    if response:
                        # Si le serveur renvoie quelque chose, c’est une erreur
                        print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                        return False
                except socket.timeout:
                    # Pas de réponse → tout va bien
                    pass

                # Si on arrive ici, c’est envoyé correctement
                print(f"Message envoyé au prompteur: {msg}")
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
                s.settimeout(0.2)
                try:
                    s.connect((self.host, int(self.port)))
                except Exception as e:
                    print("Impossible de se connecter:", e)
                    return False

                s.sendall(request.encode('utf-8'))

                try:
                    response = s.recv(1024)
                    if response:
                        print(f'Échec de la requête. Réponse : {response.decode("utf-8")}')
                        return False
                except socket.timeout:
                    pass

                print("Message supprimé du prompteur")
                return True

        except Exception as e:
            print(f'Erreur lors de la suppression du message: {e}')
            return False
