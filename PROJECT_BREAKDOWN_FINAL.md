# 📊 Data Visualization Project - Complete Guide
## Master 2 BDIA - Équipe de 3 Personnes

**Deadline:** 7 Février 2026 à minuit  
**Durée:** 2 semaines (22 Jan - 7 Fév)

---

## 🎯 Vue d'Ensemble du Projet

### Objectif
Développer une application web intelligente de data visualization qui génère automatiquement des visualisations basées sur un problème utilisateur et un dataset.

### Fonctionnalités Clés
1. Upload d'un fichier CSV
2. Saisie d'une problématique textuelle
3. Génération automatique de 3 propositions de visualisations (via LLM)
4. Sélection et téléchargement en PNG

### Stack Technique Recommandée
```
Frontend:        Streamlit
Visualisation:   Plotly
LLM:             Groq API
Backend Logic:   Python
Déploiement:     Hugging Face Spaces
Tests:          Pytest
```

---

## 👥 RÉPARTITION DES TÂCHES - 3 PERSONNES

### ⚖️ Équilibre des Charges

| Personne | Heures | Domaine Principal | Lignes de Code |
|----------|--------|-------------------|----------------|
| Person 1 | ~20h   | LLM + Data        | ~800 lignes    |
| Person 2 | ~20h   | Viz + Frontend    | ~800 lignes    |
| Person 3 | ~20h   | Infra + Tests     | ~800 lignes    |

---

## 🧑‍💻 PERSON 1 - LLM & DATA PROCESSING LEAD

### 🎯 Mission Principale
Responsable de l'intelligence du système : intégration LLM et traitement des données.

### 📋 Responsabilités Détaillées

#### SEMAINE 1 (12-15 heures)

**Jour 1-2: Configuration LLM (4h)**
- [ ] Créer compte OpenAI/Anthropic et obtenir API key
- [ ] Installer et tester la bibliothèque LLM
- [ ] Créer `src/llm/client.py` - Client API avec gestion d'erreurs
- [ ] Tester appel API basique avec prompt simple
- [ ] Documenter le choix du modèle (GPT-3.5 vs GPT-4 vs Claude)

**Jour 3-4: Prompt Engineering (5h)**
- [ ] Créer `src/llm/prompts.py` - Templates de prompts
- [ ] Designer le prompt pour l'analyse de problématique
- [ ] Designer le prompt pour générer 3 propositions
- [ ] Implémenter chain-of-thought reasoning
- [ ] Tester avec 5+ problématiques différentes
- [ ] Itérer sur les prompts basé sur les résultats

**Jour 5: Analyseur Principal (3h)**
- [ ] Créer `src/llm/analyzer.py` - Logique principale
- [ ] Implémenter `analyze_and_recommend()` 
- [ ] Parser et valider les réponses JSON du LLM
- [ ] Gérer les erreurs (API down, JSON invalide, rate limits)
- [ ] Intégrer avec le système de données

**Jour 6-7: Data Processing (4h)**
- [ ] Créer `src/data/processor.py` - Traitement CSV
- [ ] Implémenter validation de fichiers CSV
- [ ] Créer `src/data/profiler.py` - Analyse de colonnes
- [ ] Détecter types de données automatiquement
- [ ] Calculer statistiques descriptives pour le LLM
- [ ] Gérer données manquantes et valeurs aberrantes

#### SEMAINE 2 (8-10 heures)

**Jour 8-9: Optimisation LLM (4h)**
- [ ] Implémenter système de cache pour éviter appels répétés
- [ ] Ajouter retry logic avec exponential backoff
- [ ] Optimiser les prompts basés sur tests
- [ ] Réduire tokens utilisés (coûts)
- [ ] Documenter les patterns de prompts réussis

**Jour 10-11: Raffinement & Edge Cases (4h)**
- [ ] Créer fonction de raffinement de visualisation sélectionnée
- [ ] Gérer différents formats de CSV (séparateurs, encodages)
- [ ] Valider que les colonnes suggérées existent
- [ ] Améliorer justifications générées par LLM
- [ ] Ajouter fallback si LLM échoue

**Jour 12-14: Tests & Documentation (2h)**
- [ ] Écrire 10+ tests unitaires pour LLM module
- [ ] Écrire 5+ tests pour data processing
- [ ] Documenter toutes les fonctions (docstrings)
- [ ] Créer guide de prompt engineering
- [ ] Préparer exemples de réussite/échec

### 📁 Fichiers à Créer

```
src/llm/
├── __init__.py
├── client.py          # Client API OpenAI/Claude
├── prompts.py         # Templates de prompts
└── analyzer.py        # Logique d'analyse principale

src/data/
├── __init__.py
├── processor.py       # Traitement CSV
├── profiler.py        # Analyse de colonnes
└── validator.py       # Validation de données
```

### 📊 Livrables de Person 1

- ✅ Module LLM fonctionnel avec 3 propositions de viz
- ✅ Pipeline de traitement de données robuste
- ✅ 15+ tests unitaires passants
- ✅ Documentation des prompts et stratégies
- ✅ Gestion d'erreurs complète

---

## 🎨 PERSON 2 - VISUALIZATION & FRONTEND LEAD

### 🎯 Mission Principale
Responsable de l'interface utilisateur et génération des visualisations.

### 📋 Responsabilités Détaillées

#### SEMAINE 1 (12-15 heures)

**Jour 1-2: Setup Frontend (3h)**
- [ ] Installer Streamlit et tester basiquement
- [ ] Créer structure de `app.py` principal
- [ ] Designer layout (sidebar + main area)
- [ ] Implémenter upload de fichier CSV
- [ ] Créer formulaire de saisie de problématique
- [ ] Ajouter bouton "Générer"

**Jour 3-5: Moteur de Visualisation (7h)**
- [ ] Créer `src/visualization/generator.py`
- [ ] Implémenter **Scatter Plot** avec Plotly
  - Axes automatiques
  - Couleurs par catégorie
  - Tooltips informatifs
- [ ] Implémenter **Bar Chart**
  - Grouped bars
  - Bonnes pratiques (pas de 3D, pas de chartjunk)
- [ ] Implémenter **Line Chart**
  - Multiple séries
  - Markers appropriés
- [ ] Implémenter **Histogram**
  - Bins automatiques
  - KDE overlay (optionnel)
- [ ] Implémenter **Box Plot**
  - Détection outliers
  - Labels clairs
- [ ] Implémenter **Heatmap** (corrélation)
  - Annotations de valeurs
  - Colormap appropriée

**Jour 6-7: Système de Style (2h)**
- [ ] Créer `src/visualization/styler.py`
- [ ] Définir palettes de couleurs (colorblind-safe)
- [ ] Fonction d'application de style uniforme
- [ ] Formattage automatique des axes
- [ ] Gestion des titres et légendes
- [ ] Assurer data-ink ratio optimal

#### SEMAINE 2 (8-10 heures)

**Jour 8-9: Interface Utilisateur (4h)**
- [ ] Afficher preview des données uploadées
- [ ] Créer affichage des 3 propositions en tabs/cards
- [ ] Afficher justifications pour chaque viz
- [ ] Afficher best practices appliquées
- [ ] Ajouter sélection de la visualisation
- [ ] Implémenter états de chargement (spinners)

**Jour 10-11: Export & Polish (3h)**
- [ ] Créer `src/visualization/exporter.py`
- [ ] Implémenter export PNG haute qualité
- [ ] Implémenter export HTML interactif (bonus)
- [ ] Ajouter bouton de téléchargement
- [ ] Améliorer responsive design
- [ ] Ajouter messages d'erreur user-friendly

**Jour 12-14: UX & Tests (3h)**
- [ ] Améliorer flow utilisateur
- [ ] Ajouter aide contextuelle (tooltips, exemples)
- [ ] Tester avec différents datasets
- [ ] Améliorer styling général (CSS custom)
- [ ] Écrire tests pour composants de viz
- [ ] Documenter choix de design

### 📁 Fichiers à Créer

```
src/visualization/
├── __init__.py
├── generator.py       # Génération de 6 types de viz
├── styler.py          # Système de styles
└── exporter.py        # Export PNG/HTML

src/ui/
├── __init__.py
└── components.py      # Composants UI réutilisables

app.py                 # Application Streamlit principale
```

### 📊 Livrables de Person 2

- ✅ 6 types de visualizations fonctionnels
- ✅ Interface Streamlit professionnelle et intuitive
- ✅ Export PNG haute qualité
- ✅ Design responsive et accessible
- ✅ 10+ tests pour visualisations
- ✅ Documentation UX/UI

---

## 🔧 PERSON 3 - INFRASTRUCTURE & QUALITY LEAD

### 🎯 Mission Principale
Responsable de l'infrastructure, tests, déploiement et qualité du code.

### 📋 Responsabilités Détaillées

#### SEMAINE 1 (12-15 heures)

**Jour 1: Setup Projet (3h)**
- [ ] Créer repository GitHub avec structure complète
- [ ] Configurer .gitignore approprié
- [ ] Ajouter LICENSE (MIT)
- [ ] Créer structure de dossiers
  ```
  src/, tests/, docs/, examples/, .github/
  ```
- [ ] Setup uv ou poetry pour gestion dépendances
- [ ] Créer pyproject.toml avec toutes config
- [ ] Créer requirements.txt
- [ ] Ajouter Person 1 et 2 comme collaborateurs

**Jour 2: Configuration System (2h)**
- [ ] Créer `src/config/settings.py`
- [ ] Gérer variables d'environnement
- [ ] Créer .env.example
- [ ] Valider configuration au démarrage
- [ ] Créer système de constantes
- [ ] Documenter toutes les config possibles

**Jour 3: Logging & Errors (2h)**
- [ ] Créer `src/utils/logger.py` - Système de logging
- [ ] Créer `src/utils/exceptions.py` - Exceptions custom
- [ ] Définir 8+ types d'exceptions spécifiques
- [ ] Créer fonction de conversion erreur → message user-friendly
- [ ] Configurer logs en fichiers + console
- [ ] Tester système de logging

**Jour 4-5: Framework de Tests (4h)**
- [ ] Installer pytest, pytest-cov, pytest-mock
- [ ] Créer `tests/conftest.py` avec fixtures
- [ ] Créer générateur de données de test
- [ ] Setup mocking pour API LLM
- [ ] Créer 3+ datasets de test (normal, edge cases, erreurs)
- [ ] Configurer coverage reporting (target: 70%+)

**Jour 6-7: CI/CD Pipeline (3h)**
- [ ] Créer `.github/workflows/ci.yml`
  - Tests automatiques sur PR
  - Vérification formatage (black)
  - Linting (flake8)
  - Type checking (mypy)
  - Coverage report
- [ ] Créer `.github/workflows/deploy.yml`
- [ ] Setup pre-commit hooks
- [ ] Configurer branch protection sur main
- [ ] Tester pipeline avec dummy PR

#### SEMAINE 2 (8-10 heures)

**Jour 8-9: Tests Unitaires (4h)**
- [ ] Écrire tests pour `src/config/`
- [ ] Écrire tests pour `src/utils/`
- [ ] Écrire tests pour intégration LLM (avec mocks)
- [ ] Écrire tests pour visualisations
- [ ] Écrire tests pour data processing
- [ ] Atteindre >70% coverage

**Jour 10: Tests d'Intégration (2h)**
- [ ] Créer `tests/integration/test_full_flow.py`
- [ ] Tester flow complet: upload → LLM → viz → export
- [ ] Tester avec 3 datasets différents
- [ ] Tester gestion d'erreurs end-to-end
- [ ] Valider performance (temps de réponse)

**Jour 11-12: Déploiement (3h)**
- [ ] Créer compte Hugging Face Spaces
- [ ] Configurer Space avec Streamlit SDK
- [ ] Créer fichier requirements.txt pour HF
- [ ] Ajouter secrets (API keys) dans HF
- [ ] Déployer version initiale
- [ ] Tester app déployée
- [ ] Débugger problèmes de déploiement
- [ ] Configurer auto-deploy depuis main

**Jour 13-14: Documentation & Polish (2h)**
- [ ] Écrire README.md complet
  - Description
  - Installation
  - Usage
  - Architecture
  - Lien vers app déployée
- [ ] Créer `docs/architecture.md`
- [ ] Documenter décisions techniques
- [ ] Créer guide de contribution
- [ ] Préparer 3 exemples complets

### 📁 Fichiers à Créer

```
src/config/
├── __init__.py
└── settings.py        # Configuration centralisée

src/utils/
├── __init__.py
├── logger.py          # Système de logging
└── exceptions.py      # Exceptions custom

tests/
├── conftest.py        # Fixtures partagées
├── unit/
│   ├── test_llm.py
│   ├── test_visualization.py
│   ├── test_data.py
│   ├── test_config.py
│   └── test_utils.py
├── integration/
│   └── test_full_flow.py
└── utils/
    └── test_data_generator.py

.github/workflows/
├── ci.yml             # CI pipeline
└── deploy.yml         # Déploiement auto

README.md
LICENSE
pyproject.toml
requirements.txt
.pre-commit-config.yaml
```

### 📊 Livrables de Person 3

- ✅ Repository GitHub professionnel
- ✅ 20+ tests avec >70% coverage
- ✅ CI/CD pipeline fonctionnel
- ✅ App déployée sur HF Spaces
- ✅ Documentation complète
- ✅ Système de logging et erreurs
- ✅ Configuration robuste

---

## 📅 TIMELINE DÉTAILLÉE - 2 SEMAINES

### Semaine 1: Foundation & Core Features

#### Jour 1 (Mercredi 22 Jan) - TOUS ENSEMBLE - 3h
**Matin (1.5h):**
- [ ] Réunion kickoff (30 min)
  - Présentation du projet
  - Assignation des rôles
  - Accord sur outils de communication
- [ ] Setup collaboratif (1h)
  - Person 3 crée repo, ajoute autres
  - Tous clonent le repo
  - Décision stack technique finale
  - Accord sur conventions de code

**Après-midi (1.5h):**
- [ ] Chacun setup son environnement
- [ ] Person 1: Test API LLM
- [ ] Person 2: Test Streamlit hello world
- [ ] Person 3: Finalise structure projet
- [ ] Premier commit de chaque personne

#### Jour 2-3 (Jeudi-Vendredi)
**Person 1:** LLM client + prompts basiques  
**Person 2:** Setup Streamlit + premiers composants  
**Person 3:** Config + logging + tests setup

**Checkpoint Vendredi soir:**
- [ ] Standup rapide (15 min)
- [ ] Chacun montre sa progression
- [ ] Identifier blockers

#### Jour 4-5 (Weekend)
**Person 1:** Data processing pipeline  
**Person 2:** Implémentation 3 premiers types de viz  
**Person 3:** Framework de tests + CI/CD

**Checkpoint Dimanche soir:**
- [ ] Intégration session (1h)
- [ ] Premiers PRs croisés
- [ ] Code review

#### Jour 6-7 (Lundi-Mardi)
**Person 1:** Analyzer principal + intégration  
**Person 2:** 3 types de viz restants  
**Person 3:** Tests unitaires + pre-commit

**MILESTONE FIN SEMAINE 1:**
- ✅ MVP fonctionnel localement
- ✅ Upload CSV ✓
- ✅ LLM retourne 3 propositions ✓
- ✅ Au moins 1 type de viz s'affiche ✓
- ✅ Tests basiques passent ✓
- ✅ Repository bien organisé ✓

### Semaine 2: Polish & Deployment

#### Jour 8-9 (Mercredi-Jeudi)
**Person 1:** Optimisation LLM + cache  
**Person 2:** UI polish + export PNG  
**Person 3:** Tests d'intégration + premier déploiement

#### Jour 10-11 (Vendredi-Weekend)
**Person 1:** Edge cases + raffinement  
**Person 2:** UX improvements + responsive  
**Person 3:** Déploiement stable + monitoring

**Checkpoint Samedi:**
- [ ] Session de test tous ensemble (2h)
- [ ] Bug bash
- [ ] Liste des issues à fixer

#### Jour 12-13 (Lundi-Mardi)
**TOUS:** Mode polish & debug
- [ ] Fixer bugs critiques
- [ ] Tests avec datasets réels
- [ ] Optimisations finales
- [ ] Préparation exemples

#### Jour 14 (Mercredi 5 Fév)
**TOUS:** Finalisation
- [ ] Tests finaux sur app déployée
- [ ] Vérification de tous les livrables
- [ ] Enregistrement vidéo démo (3 min)
- [ ] Rédaction rapport avec 3 exemples

#### Jour 15-16 (Jeudi-Vendredi 6-7 Fév)
- [ ] Buffer pour problèmes de dernière minute
- [ ] Revue finale de la documentation
- [ ] **SOUMISSION: Samedi 7 Fév à minuit**

---

## 🤝 COLLABORATION & COMMUNICATION

### Communication Quotidienne

**Daily Standup (Async sur chat - 15 min/jour):**
Chaque personne poste quotidiennement:
```
✅ Hier: Ce que j'ai accompli
🎯 Aujourd'hui: Ce que je vais faire
🚧 Blockers: Problèmes ou aide nécessaire
```

### Réunions Synchrones

**3 réunions obligatoires:**
1. **Kickoff** - Jour 1 - 1.5h
2. **Mid-point** - Jour 7 - 1h (fin Semaine 1)
3. **Final Review** - Jour 13 - 1h

**Réunions optionnelles:**
- Debug sessions si bloqué >1h
- Code review sessions

### Workflow Git

**Branch Strategy:**
```
main                    # Production, déployé sur HF
├── develop             # Intégration
├── feature/llm-integration      (Person 1)
├── feature/visualizations       (Person 2)
└── feature/infrastructure       (Person 3)
```

**Process Pull Request:**
1. Créer feature branch
2. Développer fonctionnalité
3. Créer PR vers develop
4. **Un autre membre review** (obligatoire!)
5. Merge après approbation
6. Delete branch

**Règles de Commit:**
- Commits fréquents (plusieurs par jour)
- Messages clairs en anglais
- Format: `type: description`
  - `feat: add LLM client`
  - `fix: handle CSV parsing error`
  - `test: add unit tests for analyzer`
  - `docs: update README`

### Code Review Guidelines

**Reviewer cherche:**
- ✅ Code fonctionne
- ✅ Tests passent
- ✅ Pas de code dupliqué
- ✅ Nommage clair
- ✅ Docstrings présents
- ✅ Pas de secrets (API keys) dans code

**Comment reviewer:**
- Constructif, pas critique
- Poser questions si pas clair
- Suggérer améliorations
- Approuver si bon (même si pas parfait)

---

## 🎯 LIVRABLES FINAUX

### 1. Application Déployée
- [ ] URL publique fonctionnelle (HF Spaces)
- [ ] Toutes les fonctionnalités marchent
- [ ] Pas de crash
- [ ] Performance acceptable (<5s par viz)

### 2. Repository GitHub
- [ ] Lien: `github.com/VOTRE_EQUIPE/intelligent-data-viz`
- [ ] Structure claire avec `src/` layout
- [ ] README.md complet
- [ ] LICENSE file
- [ ] Gestion dépendances (uv/poetry)
- [ ] Tests (>70% coverage)
- [ ] CI/CD fonctionnel
- [ ] Commits visibles des 3 membres
- [ ] Au moins 3 Pull Requests mergées

### 3. Rapport avec 3 Exemples
**Format:** PDF ou Word (3-5 pages)

**Contenu pour chaque exemple:**
- Problématique posée
- Dataset utilisé (description)
- 3 propositions générées par l'IA
- Justifications
- Visualisation finale choisie (screenshot)
- Analyse de la qualité

**3 exemples suggérés:**
1. Housing prices (prix immobilier)
2. Sales analysis (analyse ventes)
3. Student performance (performance étudiants)

### 4. Vidéo Démo (3 minutes)
**Format:** MP4, uploadé sur YouTube/Drive

**Structure:**
- 0:00-0:30 - Introduction projet et équipe
- 0:30-1:00 - Upload dataset + problématique
- 1:00-2:00 - Montrer 3 propositions + justifications
- 2:00-2:30 - Sélection et visualisation finale
- 2:30-3:00 - Export PNG + conclusion

**Tips:**
- Screencast avec voix-off ou caméra
- Montrer l'app déployée (pas localhost)
- Préparer script avant
- 2-3 prises maximum

---

## 📊 EXEMPLES DE DATASETS & PROBLÉMATIQUES

### Exemple 1: Housing Prices
**Fichier:** `examples/housing_data.csv`  
**Colonnes:** price, size_sqm, rooms, location, year_built, condition  
**Problématiques possibles:**
- "Quels facteurs influencent le prix des logements?"
- "Comment la taille affecte-t-elle le prix?"
- "Y a-t-il une différence de prix entre Paris et Lyon?"

**Visualisations attendues:**
- Scatter: price vs size (colored by location)
- Bar: average price by location
- Box plot: price distribution by number of rooms

### Exemple 2: Sales Data
**Fichier:** `examples/sales_data.csv`  
**Colonnes:** date, product, revenue, region, units_sold, category  
**Problématiques possibles:**
- "Comment évoluent les ventes au fil du temps?"
- "Quels produits génèrent le plus de revenus?"
- "Quelle région performe le mieux?"

**Visualisations attendues:**
- Line chart: revenue over time by product
- Bar chart: total revenue by region
- Stacked bar: units sold by category and region

### Exemple 3: Student Performance
**Fichier:** `examples/student_data.csv`  
**Colonnes:** student_id, study_hours, grade, subject, age, has_tutor  
**Problématiques possibles:**
- "Quel est l'impact du temps d'étude sur les notes?"
- "Les tuteurs améliorent-ils les résultats?"
- "Quelle matière a les meilleurs résultats?"

**Visualisations attendues:**
- Scatter: study_hours vs grade (colored by has_tutor)
- Box plot: grade distribution by subject
- Bar chart: average grade by study hours range

---

## ✅ CHECKLIST PRÉ-SOUMISSION

### Application
- [ ] Fonctionne sur URL déployée
- [ ] Upload CSV marche
- [ ] Génération de 3 propositions marche
- [ ] Visualisations s'affichent correctement
- [ ] Export PNG fonctionne
- [ ] Pas de secrets exposés dans code
- [ ] Messages d'erreur user-friendly

### Repository
- [ ] README.md avec:
  - [ ] Description claire
  - [ ] Instructions d'installation
  - [ ] Instructions d'utilisation
  - [ ] Lien vers app déployée
  - [ ] Informations équipe
- [ ] LICENSE file présent
- [ ] .gitignore approprié
- [ ] Structure src/ organisée
- [ ] Tests présents (>15 tests minimum)
- [ ] CI/CD pipeline passe
- [ ] Commits des 3 membres visibles
- [ ] Pull Requests documentées

### Code Quality
- [ ] Code formaté (black)
- [ ] Pas de warnings flake8
- [ ] Docstrings sur toutes fonctions
- [ ] Pas de code mort
- [ ] Gestion d'erreurs appropriée
- [ ] Logging en place

### Tests
- [ ] Tests unitaires pour LLM
- [ ] Tests unitaires pour visualizations
- [ ] Tests unitaires pour data processing
- [ ] Tests d'intégration
- [ ] Coverage >70%
- [ ] Tous les tests passent

### Documentation
- [ ] README complet
- [ ] Docstrings partout
- [ ] Comments pour code complexe
- [ ] Architecture documentée

### Livrables
- [ ] Rapport PDF/Word avec 3 exemples
- [ ] Screenshots de qualité
- [ ] Vidéo 3 min enregistrée et uploadée
- [ ] Tous les liens fonctionnent

---

## 🆘 TROUBLESHOOTING & FAQ

### Problèmes Courants

**"LLM retourne du JSON invalide"**
→ Person 1: Nettoyer la réponse avant parsing
```python
response = response.strip()
if response.startswith("```json"):
    response = response[7:-3]
result = json.loads(response)
```

**"Tests échouent en CI mais passent localement"**
→ Person 3: Vérifier variables d'environnement, versions Python

**"App crash sur HF Spaces"**
→ Person 3: Vérifier logs HF, requirements.txt, secrets configurés

**"Git merge conflicts"**
→ Communiquer avant modifier mêmes fichiers, pull souvent

### Qui Contacter Pour Quoi

**Problème avec LLM/API:**
→ Person 1 lead, mais tous peuvent aider

**Problème avec UI/Streamlit:**
→ Person 2 lead, mais tous peuvent aider

**Problème avec Git/Déploiement:**
→ Person 3 lead, mais tous peuvent aider

**Bloqué >30 minutes:**
→ Poster dans chat équipe, demander aide

### Ressources

- OpenAI API Docs: https://platform.openai.com/docs
- Streamlit Docs: https://docs.streamlit.io
- Plotly Examples: https://plotly.com/python/
- HF Spaces: https://huggingface.co/docs/hub/spaces
- Pytest: https://docs.pytest.org

---

## 🎓 CRITÈRES D'ÉVALUATION

Votre projet sera évalué sur:

1. **Fonctionnalité (30%)**
   - Application fonctionne comme spécifié
   - 3 propositions générées
   - Visualisations correctes
   - Export fonctionne

2. **Qualité du Code (25%)**
   - Structure claire
   - Bonnes pratiques
   - Tests présents
   - Documentation

3. **Visualisations (20%)**
   - Suivent best practices
   - Pas de chartjunk
   - Lisibles et informatives
   - Titres/axes/légendes appropriés

4. **Intégration LLM (15%)**
   - Prompts pertinents
   - Recommandations sensées
   - Justifications valides

5. **Collaboration (10%)**
   - Git history claire
   - Pull Requests
   - Contributions équilibrées

---

## 💪 CONSEILS FINAUX

### Pour Réussir

1. **Commencez Simple**
   - MVP d'abord, polish ensuite
   - Ne pas over-engineer
   - Itérer progressivement

2. **Communiquez Tôt et Souvent**
   - Standup quotidien (même async)
   - Signaler blockers immédiatement
   - Demander aide après 30 min bloqué

3. **Testez Fréquemment**
   - Run code toutes les 15-30 min
   - Tests automatiques
   - Tester sur app déployée régulièrement

4. **Documentez en Avançant**
   - Pas à la fin!
   - Docstrings au moment d'écrire fonction
   - README mis à jour régulièrement

5. **Gérez Votre Temps**
   - 2-3h par jour max
   - Pauses régulières
   - Pas de all-nighter la veille!

### Ce qui Fait la Différence

- ✨ Code propre et lisible
- ✨ Bonne UX (messages clairs, loading states)
- ✨ Visualisations vraiment bonnes (pas juste fonctionnelles)
- ✨ Documentation claire
- ✨ Démo vidéo professionnelle

### Ce qui Pénalise

- ❌ App qui crash
- ❌ API keys exposées dans repo
- ❌ Pas de tests
- ❌ README incomplet
- ❌ Commits avec messages vagues ("fix", "update")

---

## 🎉 VOUS ÊTES PRÊTS!

Vous avez maintenant:
- ✅ Répartition claire des tâches (20h chacun)
- ✅ Timeline détaillée jour par jour
- ✅ Fichiers à créer listés
- ✅ Exemples de datasets
- ✅ Checklist complète
- ✅ Guide de collaboration

**Prochaines Étapes:**
1. Lire ce document en entier (30 min)
2. Réunion kickoff équipe (1h)
3. Déclarer équipe sur Google Sheet
4. Créer chat équipe (Discord/Slack/WhatsApp)
5. Person 3 crée repo GitHub
6. COMMENCER! 🚀

**Deadline: Samedi 7 Février 2026 à minuit**

Bon courage! Vous allez y arriver! 💪

---

*Document créé le 22 Janvier 2026*  
*Version: 1.0 - Distribution Équilibrée 3 Personnes*
