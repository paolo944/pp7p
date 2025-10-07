# PP7+

C'est un client, une sur-couche logiciel pour [ProPresenter 7](https://renewedvision.com/propresenter)
Il permet d'avoir des fonctionnalités en plus en utilisant l'api officielle de
pp7. Parmi ces fonctionnalités il y a:

- Un site de sous-titres en direct avec un format spécifique qui permet par exemple,
    de sauter certaines lignes ou d'avoir un format différent en fonction du texte.

## Installation de l'application

Voici un simple tuto pour installer l'application et la lancer sur votre machine.
Le Tuto est valable uniquement pour MacOS et linux, pour un tuto sur un autre OS,
demandez le moi par mail.

1. Ouvrez un terminal et tapez cette commande pour récupérer l'application sur
    github:  
    ```bash
    cd && git clone https://github.com/paolo944/pp7p.git
    ```
2. Une fois téléchargé, allez dans le dossier de l'application avec la commande suivante:  
    ```bash
    cd pp7p
    ```
3. Allez dans les paramètres de l'application ProPresenter dans la rubrique réseaux/network  
    Activez l'option TCP/IP tout en bas et l'option network tout en haut, une adresse ip apparaîtra en haut et vous pouvez choisir un numéro de port tout en bas sous l'option TCP/IP.  
    Choissisez un numéro de port entre 40000 et 65000 pour éviter d'avoir des erreurs.  
    Notez l'adresse ip, qui est de la forme: 192.168.0.0 et le port que vous avez choisi sous l'option TCP/IP.
    Si vous allez utiliser l'application sur la même machine où propresenter est utilisé, vous pouvez simplement
    remplacer l'adresse ip par 127.0.0.1 ou localhost.

4. Ouvrez ce fichier avec un éditeur de texte normal et remplissez le comme-ceci:
    ```json
    {
        "host": "{adresse ip}",
        "port": "{port}"
    }
    ```
    Notez bien les guillements qui sont importants et remplacez {adresse ip} par celle qui vous avez noté  
    et {port} par celui que vous avez noté.
5. Vous pouvez lancer l'application avec la comande
    ```bash
    bash start_app.sh
    ```
    L'application se lancera automatiquement et fera les mise à jour nécessaires si y en a.

## Utilisation

Il vous faut d'abord vous munir de l'adresse qui apparaîtra dans le terminal
au moment du lancement de l'application, par exemple:
```bash
 * Running on http://127.0.0.1:5000
 * Running on http://10.192.8.80:5000
```

Il faut pas utiliser l'adresse commençant par 127 mais l'autre.
La première adresse est locale, elle peut-être utilisé uniquement
si vous êtes sur la même machine que celle sur laquelle vous avez lancé
l'application.

La seule adresse qui vous sera utile est celle des sous-titres:
- {adresse}/

Où {adresse} est l'adresse que vous avez trouvé plus haut.
Dans l'exemple, les adresses seraient:
- http://10.192.8.80:5000/

La page  contient les sous-titres actuels avec un format spécifique
à Hillsong Paris, de façon à sauter une ligne sur deux.
Il y a également 2 formats différents en fonction de si c'est pour une slide
de louange ou de verset.

Le programme reconnaît un verset simplement si le texte contient des nombres à un moment.
Dans le futur une expression plus compliqué pour reconnaître les versets pourra être utilisé pour être plus exact.

Pour l'instant pour éviter d'afficher par exemple les prières et les remerciements, nous suppoussons qu'ils ne contiennent pas
de chiffres et que donc si la slide contient plus de 4 lignes(plus que celles de louanges habituelles), alors le texte ne sera pas affiché.

## Configuration OBS

Voici les étapes pour utiliser les sous-titres avec OBS

1. Lancer OBS

2. Ajoutez comme nouvelle source un navigateur.

3. renseignez dans la case URL l'adresse que vous avez eu plus haut. Par exemple http://10.192.8.80:5000/

4. Pour le width et le height vous pouvez utiliser ce qui vous semble le plus adequat.

5. appuyez sur OK

A présent, les sous-titres s'afficheront de façon dynamique sur le live. Vous pouvez aussi rafraichir la page s'il faut
en faisant un clique droit sur la source.

## Bug report

Si vous rencontrez un bug ou quelconque souci, vous pouvez me contacter.