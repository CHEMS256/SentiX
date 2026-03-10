
# Sentix 🧠
### Analyseur de Sentiments Intelligent Multilingue
<div align="center">
  <img src="https://img.shields.io/badge/Version-2.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.9+-9cf.svg" alt="Python">
</div>

> Automatisation de l'analyse de sentiments pour les avis clients via le Machine Learning et le traitement du langage naturel (NLP).

<div align="center">
 • <a href="#-à-propos">À Propos</a> •
  <a href="#-fonctionnalités">🌟 Fonctionnalités</a> •
  <a href="#-démarrage-rapide">🚀 Démarrage Rapide</a> •
  <a href="#-installation-détaillée">📦 Installation Détaillée</a> •
  <a href="#-utilisation">🎯 Utilisation</a> •
  <a href="#-déploiement">🚀 Déploiement</a> •
  <a href="#-documentation">📚 Documentation</a> 
 • <a href="#-contribuer">🤝 Contribuer</a> •
  <a href="#-licence">📄 Licence</a> 
</div>

## Table des Matières
- [À Propos](#à-propos)
- [🌟 Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [🚀 Démarrage Rapide](#-démarrage-rapide)
- [📦 Installation Détaillée](#-installation-détaillée)
- [🎯 Utilisation](#-utilisation)
- [🚀 Déploiement](#-déploiement)
- [📚 Documentation](#-documentation)
- [🤝 Contribuer](#-contribuer)
- [📄 Licence](#-licence)

---

## À Propos

**Sentix** est une application web intelligente conçue pour analyser les sentiments des avis clients en temps réel. Développée avec **Flask** (Python) pour le backend et une interface frontend moderne, elle se distingue par sa capacité à traiter des données multilingues, y compris le **Français, l'Anglais, l'Arabe littéraire et le Darija (Marocain)**.

Le projet utilise une approche hybride combinant des règles linguistiques contextuelles et le Machine Learning (Random Forest / TF-IDF) pour offrir une analyse précise même sur des textes courts ou informels.

---

## 🌟 Fonctionnalités

- **🧠 Analyse Hybride** : Combine dictionnaires contextuels et modèle Random Forest pour une précision accrue.
- **🌍 Multilingue** : Support natif du Français, Anglais, Arabe et Darija.
- **📊 Traitement par lots** : Importez des fichiers Excel (`.xlsx`) ou CSV pour analyser des centaines d'avis en un clic.
- **📈 Visualisation** : Dashboard immédiat affichant la distribution des sentiments (Positif, Négatif, Neutre).
- **📥 Rapports** : Téléchargement automatique du fichier analysé avec les tags de sentiment.
- ** Interface Moderne** : UI responsive avec effet "Glassmorphism" et glisser-déposer (Drag & Drop).

---

## 🏗️ Architecture

Le projet suit une architecture MVC simplifiée :

- **Backend (Python/Flask)** :
  - `AnalyseurSentiments` : Cœur du moteur ML (Vectorisation TF-IDF + Classification).
  - `APIIntelligente` : Module de détection de langue et d'analyse par règles.
  - `GestionnaireExcel` : Gestion des entrées/sorties de fichiers.
- **Frontend (HTML/CSS/JS)** :
  - Single Page Application (SPA) légère.
  - Communication asynchrone (AJAX/Fetch) avec le serveur.

---

## 🚀 Démarrage Rapide

Suivez ces étapes pour lancer le projet en local en moins de 2 minutes.

1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/sentix.git
   cd sentix
   ```

2. **Créez un environnement virtuel** (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Installez les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancez l'application** :
   ```bash
   python app.py
   ```

5. **Accédez à l'interface** : Ouvrez votre navigateur à l'adresse `http://127.0.0.1:5000`.

---

## 📦 Installation Détaillée

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Dépendances
Créez un fichier `requirements.txt` contenant :

```text
Flask
pandas
numpy
scikit-learn
langdetect
openpyxl
werkzeug
```

### Structure des Dossiers
Assurez-vous que votre projet respecte cette arborescence :
```
sentix/
│
├── app.py                # Serveur Flask et logique ML
├── index.html            # Interface utilisateur
├── requirements.txt      # Dépendances
│
├── uploads/              # Dossier temporaire pour les fichiers reçus
└── resultats_analyse/    # Dossier où sont stockés les rapports Excel
```

> **Note** : Les dossiers `uploads` et `resultats_analyse` sont créés automatiquement au premier lancement.

---

## 🎯 Utilisation

1. **Accueil** : L'interface affiche une zone de dépôt.
2. **Import** : Glissez-déposez un fichier Excel ou CSV contenant une colonne "Avis", "Comment" ou "Text".
3. **Analyse** : Le serveur détecte la langue, analyse le sentiment et compte les résultats.
4. **Résultats** :
   - Consultez les statistiques (Total, Positifs, Négatifs).
   - Visualisez un aperçu toutes lignes analysées .

---

## 🚀 Déploiement

Pour déployer Sentix en production (serveur Linux, Heroku, Render, etc.) :

### Utilisation de Gunicorn (Linux)
1. Installez Gunicorn :
   ```bash
   pip install gunicorn
   ```
2. Lancez l'application :
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Variables d'environnement
Il est recommandé de désactiver le mode debug en production :
```python
# Dans app.py
if __name__ == '__main__':
    app.run(debug=False, port=5000)
```

### Docker (Optionnel)
Un `Dockerfile` peut être créé pour containeriser l'application, assurant une portabilité maximale.

---

## 📚 Documentation

### API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Sert l'interface HTML principale. |
| `POST` | `/upload` | Reçoit le fichier, lance l'analyse, retourne un JSON avec les stats et l'URL de téléchargement. |
| `GET` | `/download/<filename>` | Permet le téléchargement du fichier Excel résultant. |

### Modèle Machine Learning
- **Vectorisation** : `TfidfVectorizer` (n-grams de caractères 2-4).
- **Classifieur** : `RandomForestClassifier` (200 estimateurs).
- **Entraînement** : Réalisé "in-memory" au démarrage sur un dataset de démonstration intégré.

---

## 🤝 Contribuer

Les contributions sont ce qui fait de la communauté open source un endroit incroyable. Toutes les contributions sont les bienvenues !

1. Forkez le projet.
2. Créez votre branche (`git checkout -b feature/AmazingFeature`).
3. Commitez vos changements (`git commit -m 'Add some AmazingFeature'`).
4. Poussez vers la branche (`git push origin feature/AmazingFeature`).
5. Ouvrez une Pull Request.

---

## 📄 Licence

Distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus d'informations.
