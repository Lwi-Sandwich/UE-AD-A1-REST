# UE-AD-A1-REST

Ce TP met en place une architecture REST composée de quatre micro-services.
Chacun d'entre eux a un swagger à l'endpoint `/docs`.

## Auteurs
- Marc Blanchet
- Louis Bruneteau

## Installation

### Création d'un environnement virtuel
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Lancement des micro-services
```bash
chmod +x launch.sh
./launch.sh
```

Chaque micro-service peut également être lancé individuellement en utilisant la commande `python3 <nom_du_micro_service>.py` depuis son répertoire.

## Ports
- User: 3203
- Movie: 3200
- Booking: 3201
- Showtime: 3202

