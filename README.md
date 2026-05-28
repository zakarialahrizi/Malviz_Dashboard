# malviz_dashboard

Interface web Streamlit pour la détection de malware par visualisation de fichiers binaires.

Le modèle (ResNet-18, format ONNX) convertit chaque fichier en image niveaux de gris
et prédit si le fichier est **Benign** ou appartient à une famille de **malware**.

---

## Prérequis

- Python 3.10+
- Le package `malviz` installé (contient le modèle ONNX et les noms de classes)

---

## Installation

```bash
# 1. Cloner ou copier ce dossier
cd malviz_dashboard

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. S'assurer que le package malviz est installé
pip install -e /chemin/vers/malviz
```

---

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

---

## Structure

```
malviz/
├── app.py                  # Point d'entrée, redirige vers Home
├── scanner.py              # Logique ML (inchangée)
├── pages/
│   ├── 1_Home.py           # Upload + scan + métriques
│   ├── 2_History.py        # Historique + graphiques
│   └── 3_Settings.py       # Seuil de confiance + dossier logs
├── config/
│   └── config.json         # Paramètres persistants
├── data/
│   └── scan_history.csv    # Historique des scans
├── utils/
│   ├── config_manager.py   # Lecture/écriture config.json
│   ├── csv_manager.py      # Lecture/écriture scan_history.csv
│   └── charts.py           # Graphiques Plotly
├── assets/
│   └── logo.png            # Logo affiché dans la sidebar
├── requirements.txt
└── README.md
```

---

## Pages

### Home
- Upload d'un fichier binaire
- Lancement du scan via `scanner.py`
- Affichage du résultat : Benign / Malware / Incertain
- Métriques : classe détectée, score de confiance, temps d'analyse
- Graphique de répartition des résultats

### History
- Tableau de tous les scans passés (`scan_history.csv`)
- Filtre Malware / Benign / Tous
- Téléchargement CSV
- Graphiques : scans par jour, distribution des scores

### Settings
- Réglage du seuil de confiance (0.50 – 1.00)
- Chemin du dossier de logs
- Sauvegarde dans `config/config.json`

---

## Notes

- Le fichier `config/config.json` est créé automatiquement au premier démarrage.
- Le fichier `data/scan_history.csv` est créé automatiquement si absent.
- Aucune base de données, aucun serveur externe.
- Le logo `assets/logo.png` est optionnel.
