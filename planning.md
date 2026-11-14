# Planning — llm-chat

## Objectif

Construire **à la main** (sans framework type LangChain) un chatbot **expert Java**, pour comprendre chaque brique : appel LLM, prompt, mémoire, streaming, interface, persistance, robustesse, déploiement.

Notions à approfondir à chaque étape : voir [apprentissage.md](apprentissage.md).

## Stack

| Brique | Choix |
|---|---|
| Langage | Python 3.12, venv + `requirements.txt` |
| LLM | OpenAI (`responses.create`), Claude et Ollama en option plus tard |
| Interface | Flask (back-end) + une page HTML/JavaScript (front-end) |
| Persistance | SQLite (module `sqlite3` standard) |
| Secrets | `.env` (jamais commité) |
| Code | GitHub : `fouzo09/llm-chat` |

## Organisation du code

```
llm-chat/
├── main.py                               ← point d'entrée
├── helpers/                              ← fonctions réutilisables (à remplir au fil des étapes)
├── prompts/
│   └── JAVA_EXPERT_INSTRUCT_PROMPT.md    ← prompt système, versionné
├── requirements.txt
├── planning.md
├── .env                                  ← secrets et réglages, ignoré par Git
└── .gitignore
```

Règle : le `.env` contient les **secrets** et les **réglages** (modèle, limites). Les **prompts** vont dans `prompts/`, versionnés.

---

## Étapes

Légende : ✅ fait · 🟡 en cours · ⬜ à faire

### 1. Environnement 🟡

- **Concepts** : environnement virtuel, gestion des secrets, facturation au token.
- [x] venv + `requirements.txt`
- [x] `.env` chargé avec `python-dotenv`, ignoré par Git
- [x] Dépôt GitHub + premier commit
- [ ] Plafond de dépense fixé dans la console OpenAI
- **Fini quand** : la clé est chargée depuis `.env`, jamais commitée, et un plafond de dépense est fixé.

### 2. Premier appel LLM ✅

- **Concepts** : rôles `user` / `assistant`, prompt système séparé (`instructions`), tokens, `max_output_tokens`, API **sans état**.
- [x] Réponse affichée en console
- [ ] Afficher les tokens consommés (`input_tokens`, `output_tokens`)
- **Fini quand** : tu obtiens une réponse en console et tu sais lire le nombre de tokens consommés.

### 3. Prompt design 🟡

- **Concepts** : rôle, contexte, objectif, contraintes, format de sortie ; comportement quand le modèle ne sait pas.
- [x] Prompt structuré (ROLE / CONTEXT / OBJECTIVE / TASKS / CONSTRAINTS / OUTPUT FORMAT)
- [x] Le prompt est lu depuis `prompts/`
- [ ] Jeu de 8 à 10 questions de test dans un fichier, par exemple :
  - question simple : différence `ArrayList` / `LinkedList`
  - stack trace `NullPointerException`
  - relecture d'un bout de code
  - question hors sujet (recette de crêpes)
  - question piège : méthode qui n'existe pas (`List.shuffleAll()`)
  - question à laquelle il manque une info (version de Java)
- **Fini quand** : le prompt passe le jeu de test, rejoué à chaque modification.

### 4. Mémoire de conversation 🟡

- **Concepts** : l'historique est une liste renvoyée **en entier** à chaque tour → fenêtre de contexte, coût qui grossit, troncature.
- [x] Liste `history` envoyée au modèle
- [ ] Limiter l'historique à `HISTORY_LIMIT` messages
- **Fini quand** : le bot se souvient d'une info donnée 5 tours plus tôt, et l'historique est limité.

### 5. Streaming ✅

- **Concepts** : fragments (deltas), temps jusqu'au premier token vs temps total.
- [x] Réponse affichée progressivement en console
- [x] Texte complet reconstitué et ajouté à l'historique
- [ ] Décider quoi faire si le stream est interrompu (garder la réponse partielle ou non)
- **Fini quand** : affichage progressif + réponse complète bien enregistrée.

### 6. Interface Flask ⬜

- **Outils** : Flask (routes, `render_template`, `Response` avec un générateur), une page HTML + JavaScript (`fetch`).
- **Concepts clés** :
  - Séparation **back-end** (Flask, appelle OpenAI) / **front-end** (page HTML, affiche le chat). La clé API ne quitte jamais le serveur.
  - HTTP est **sans état** : chaque requête arrive « vierge ». Il faut identifier l'utilisateur (identifiant de session) et garder son historique **côté serveur** (un dictionnaire pour commencer, SQLite à l'étape 7). Le cookie de session Flask est trop petit (~4 Ko) pour y stocker l'historique.
  - Streaming HTTP : la route renvoie un générateur, le JavaScript lit la réponse morceau par morceau (`response.body.getReader()`) ou via Server-Sent Events.
- [ ] Nettoyer les dépendances : retirer `gradio` et `streamlit`, ajouter `flask` dans `requirements.txt` ; retirer `import gradio` de `main.py`
- [ ] Route `GET /` qui renvoie la page du chat (`templates/index.html`)
- [ ] Route `POST /chat` qui reçoit la question en JSON et renvoie la réponse en streaming
- [ ] Historique par utilisateur conservé côté serveur
- [ ] JavaScript : envoyer la question, afficher la réponse au fil de l'eau
- [ ] Enregistrer la réponse **complète** dans l'historique à la fin du stream
- [ ] Lancer avec `flask --app main run --debug`
- **Fini quand** : conversation multi-tours streamée dans le navigateur.

### 7. Persistance SQLite ⬜

- **Concepts** : tables `conversations` / `messages`, identifiant de session ; on **stocke tout**, on **envoie une partie**.
- [ ] Schéma des deux tables
- [ ] Sauvegarde de chaque message
- [ ] Reprise d'une ancienne conversation
- **Fini quand** : tu relances l'application et reprends une ancienne conversation.

### 8. Robustesse ⬜

- **Concepts** : timeouts, retries avec backoff, rate limits, messages d'erreur propres, journalisation.
- [x] `try` / `except APIError` autour de l'appel
- [ ] Vérifier `OPENAI_MODEL` au démarrage
- [ ] Journaliser latence et tokens par requête
- **Fini quand** : couper le réseau ou mettre une mauvaise clé ne fait pas planter l'application.

### 9. Déploiement ⬜

- **Options** : Docker sur un VPS derrière un reverse proxy HTTPS.
- [ ] Remplacer le serveur de développement Flask par un serveur de production (Gunicorn)
- **Concepts** : secrets en production, volume persistant pour SQLite, protection de l'accès.
- [ ] Protéger l'accès (une URL publique sans authentification = ta clé API offerte à tout le monde)
- [ ] Volume persistant pour la base
- **Fini quand** : une URL fonctionne, l'accès est protégé et l'historique survit à un redémarrage.

---

## Trois pièges à garder en tête

1. **Coût** : il croît avec la longueur de la conversation, pas seulement avec le nombre de messages.
2. **Streaming et mémoire** : toujours enregistrer la réponse **complète** après le stream.
3. **SQLite en déploiement** : sans volume persistant, tout est perdu à chaque redéploiement.
