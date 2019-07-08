#! /bin/sh

# Beim ersten Fehler das Skript beenden
set -e

# Skript aus overlay nach Desktop kopieren
sudo cp -r /boot/overlays/SmartWorkbench/ ~/Desktop/

# wechsle in das SmartWorkbench Verzeichnis
cd ~/Desktop/SmartWorkbench

# installiere benoetigte Biblliotheken
echo "Installiere die paho Bibliothek"
pip install paho-mqtt

# kopiere paho in das systemweite Verzeichnis, damit Python es auf Anhieb findet
sudo cp -r ~/.local/lib/python2.7/site-packages/paho /usr/lib/python2.7/dist-packages/
sudo cp -r ~/.local/lib/python2.7/site-packages/paho /usr/lib/python3/dist-packages/

# Skript ausführbar machen
sudo chmod +x start.py
