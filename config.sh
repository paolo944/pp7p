#!/bin/bash

# Chemin vers le projet (actuel)
PROJECT_DIR=$(pwd)

echo "Création de l'environnement virtuel..."
python3 -m venv .env

if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances..."
    source .env/bin/activate
    pip install -r requirements.txt
    deactivate
else
    echo "Aucun fichier requirements.txt trouvé."
fi



echo "Création du LaunchAgent..."

cat << EOF > ~/Library/LaunchAgents/com.monnom.startapp.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "https://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monnom.startapp</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/start_app.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>StandardOutPath</key>
    <string>/tmp/startapp.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/startapp.err</string>
</dict>
</plist>
EOF

echo "Chargement de l'agent Launch..."
launchctl load ~/Library/LaunchAgents/com.monnom.startapp.plist

echo "Création des clés"
mkdir keys
mkdir keys/pending
mkdir keys/authorized
openssl genpkey -algorithm ed25519 -out keys/ed25519.pem
openssl pkey -in ed25519.pem -pubout -out keys/25519_public.pem
echo "ATTENTION!! NE JAMAIS PARTAGER CES CLES!!!"

echo "Configuration terminée !"
