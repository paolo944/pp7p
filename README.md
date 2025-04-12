# PP7+

C'est un client, une sur-couche logiciel pour [ProPresenter 7](https://renewedvision.com/propresenter)
Il permet d'avoir des fonctionnalités en plus en utilisant l'api officielle de
pp7. Parmi ces fonctionnalités il y a:

- L'accès à une application web qui permet de consulter les compteurs configurés,
    de voir les paroles actuellement à l'écran, le titre de la présentation actuelle
    et d'envoyer ou supprimer des messages sur le prompteur.

- Un site de sous-titres en direct avec un format spécifique qui permet par exemple,
    de sauter certaines lignes ou d'avoir un format différent en fonction du texte.

- L'accès à un prompteur en direct qui est accessible sur le réseau.

## Installation de l'application

Voici un simple tuto pour installer l'application et la lancer sur votre machine.
Le Tuto est valable uniquement pour MacOS et linux, pour un tuto sur un autre OS,
demandez le moi par mail.

1. Ouvrez un terminal et tapez cette commande pour récupérer l'application sur
    github:  
    ```bash
    git clone https://github.com/paolo944/pp7p.git
    ```
2. Une fois téléchargé, allez dans le dossier de l'application avec la commande suivante:  
    ```bash
    cd pp7p
    ```
3. Il faut créer un environement pour simplifier l'installation avec cette commande:  
    ```bash
    python3 -m venv env && source env/bin/activate
    ```
4. Ensuite, installez les dépendances de l'application avec cette commande tout
    en restant dans le dossier de l'application:  
    ```bash
    pip3 install -r requirements.txt
    ```
5. Allez dans les paramètres de l'application ProPresenter dans la rubrique réseaux/network  
    Activez l'option ??, une adresse ip apparaîtra et vous pouvez choisir un numéro de port.  
    Choissisez un numéro de port entre 40000 et 65000 pour éviter d'avoir des erreurs.  
    Notez l'adresse ip, qui est de la forme: 192.168.0.0 et le port.  
    utilisez la commande suivante dans votre terminal pour créer le fichier de configuration:  
    ```bash
    touch info.json
    ```
6. Ouvrez ce fichier avec un éditeur de texte normal et remplissez le comme-ceci:
    ```json
    {
        "host": "{adresse ip}",
        "port": "{port}"
    }
    ```
    Notez bien les guillements qui sont importants et remplacez {adresse ip} par celle qui vous avez noté  
    et {port} par celui que vous avez noté.
5. Vous pourrez finalement lancer l'application avec cette commande:  
    ```bash
    python3 app.py
    ```

## Bug report

Si vous rencontrez un bug ou quelconque souci, vous pouvez me contacter sur
mon adresse mail: [paul@mekhail.dev](mailto:paul@mekhail.dev).

# For Others

# Web client for ProPresenter

Web client for ProPresenter 7 with important informations like clock and Stage live messages.

To run the web app, the server (this app) must be running on the same network as the ProPresenter app.
The server is not required to be on the same machin as the ProPresenter app.

## ⚠️ **IMPORTANT: PLEASE READ CAREFULLY** ⚠️
This app is still under developpement and can very likely crash.
Please don't use it in critical situations. Only in training and
just for testing for now.
If you have any question ou improvemnts, feel free to sumbit
an issue on github or a pull request and i will to try to
answer fastly or review your pull requests.

## Requirements
- python3
- pip3
- git

## Installation
Open a terminal and run the following commands
```bash
git clone https://github.com/paolo944/pp7_client.git
cd pp7_client
pip3 install -r requirements.txt
```
## Configuration
You have to first enable network on ProPresenter by going into Settings->Network then Enable Network.
The ip adress should appear should under. Write down also the port number of the ProPresenter app.
Make sure that your machine is visible on your local network, so that other clients like your phone or the server
if it's not on the same machine as the ProPresenter app could communicate with it's API.

After you have written down the ip adress and made sure the ProPresenter computer is visible on the local 
network, go in the file pp7_client/info.json and add this line
```json
{
    "host": "{adresse ip}",
    "port": "{port}"
}
```
Replace  {ip adress} by the ip adress of the machine on which ProPresenter is running and {port} by the port number 
of ProPresenter.

If the server runs on the same machien as the ProPresenter app, just replace {ip adress} by 127.0.0.1 .

## Running the app
To run the app, launch the script app.py.

On Mac-GNU/Linux:
```bash
# Make sure to be located in the project directory
python3 app.py
```

On Windows PowerShell:
```
python app.py
```

A url wil appear in the terminal, go to it on any client which is on the same network to get the main client.

If you want the subtitles page which updates automaticly, go to the url/subtitles .

The subtitles are well suited for OBS if you create a scene using a web brower.

## ⚠️ **DISCLAIMER** ⚠️
The subtitles format is suited for my church's specific formats, so will very probably have to adapt it to your format.

## Older test versions

You can also look at other versions that I tried making

[PP7P C version](https://github.com/paolo944/pp7p_c_version) is a version completely
written in C without any dependencies other than POSIX.
It was meant to be fast and light. I abandonned this version because it took too much
time to develop and was a little unecessary. It would be useful if you want to run it
on something like raspberry pi pico, eventhough you would need to adapt it to the raspberry's lib
It works well but lacks some functionnalities like SSE management.  

[PP7 Client v1](https://github.com/paolo944/pp7_client) It was the first version and is
very similar to this one, but it uses http to communicate with the propresenter api instead
of just tcp/ip and doesn't manage SSE clients as good as this one.

## Bug report

If there's any issue, you can open an issue on github.  
If needed, my email adress if: [paul@mekhail.dev](mailto:paul@mekhail.dev).