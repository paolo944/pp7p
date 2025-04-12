# PP7P

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
Le Tuto est valable uniquement pour MacOS, pour un tuto sur un autre OS,
demandez le moi par mail.

1. Installer Nginx
    sur MacOS, pour ce faire, vous aurez besoin d'avoir [homebrew](https://brew.sh/)
    d'installé sur votre machine. Une fois homebrew installé, entrez cette 
    commande dans le terminal:  
    `brew install nginx`
2. Ouvrez un terminal et tapez cette commande pour récupérer l'application sur
    github:  
    `git clone https://github.com/paolo944/pp7p.git`
3. Une fois téléchargé, allez dans le dossier de l'application avec la commande suivante:  
    `cd pp7p`
4. Copiez le fichier de configuration de nginx dans son dossier:  
    `sudo cp ./proxy/pp7p.conf /usr/local/etc/nginx/servers/pp7p.conf`
5. Ensuite, installez les dépendances de l'application avec cette commande tout
    en restant dans le dossier de l'application:  
    `cd backend && pip3 install -r requirements.txt`
6. Vous pourrez finalement lancer l'application avec cette commande:  
    `python3 app.py`
7. Pour lancer nginx à chaque fois automatiquement à chaque démarrage de l'ordinateur
    tapez cette commande dans votre terminal:  
    `brew services start nginx`

## Bug report

Si vous rencontrez un bug ou quelconque souci, vous pouvez me contacter sur
mon adresse mail: [paul@mekhail.dev](mailto:paul@mekhail.dev).

## Anciennes versions

Vous pouvez également consulter en ligne le code d'autres versions de test.

[PP7P C version](https://github.com/paolo944/pp7p_c_version) est une version
écrite totalement en C sans dépedances autre que les libraires du système.
Elle est faite pour être rapide, sans grosse utilisation de la mémoire et sans
dépendances tel que nginx ou python. Elle a été abandonné pour le coût du
developpement d'un application pareil en bas niveau. Cependant elle fonctionne
mais il lui manque encore quelques fonctionnalités.  

[PP7 Client v1](https://github.com/paolo944/pp7_client) est la première version
écrite pour ce projet, elle fonctionne bien sur la plupart des systèmes. Elle utilise
un système de serveur écrit en python avec la libraire Flask.
