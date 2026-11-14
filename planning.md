# Planning — llm-chat

## Objectif

Construire **à la main** (sans framework type LangChain) un chatbot **expert Java**, pour comprendre chaque brique : appel LLM, prompt, mémoire, streaming, interface, persistance, robustesse, déploiement.

> Pourquoi ce projet (apprentissage, portfolio, outil perso…) : _à compléter_

## Cadrage

- **Timebox** : 5 à 7 sessions de 1 à 2 h.
- **Un commit par étape**, et ce fichier mis à jour à chaque fois.
- **Pas de framework** : mémoire et streaming écrits à la main.
- **Avancer pas à pas** : comprendre avant d'ajouter.

## Stack

| Brique | Choix |
|---|---|
| Langage | Python 3.12, venv + `requirements.txt` |
| LLM | OpenAI (`responses.create`), Claude et Ollama en option plus tard |
| Interface | Gradio (`gr.ChatInterface`) |
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
- [ ] Ajouter `.gradio/` et `__pycache__/` au `.gitignore`
- [ ] Nettoyer `requirements.txt` (retirer `streamlit` si Gradio est retenu, fixer la version de `gradio`)
- **Fini quand** : la clé est chargée depuis `.env`, jamais commitée, et un plafond de dépense est fixé.

### 2. Premier appel LLM ✅

- **Concepts** : rôles `user` / `assistant`, prompt système séparé (`instructions`), tokens, `max_output_tokens`, API **sans état**.
- [x] Réponse affichée en console
- [ ] Afficher les tokens consommés (`input_tokens`, `output_tokens`)
- **Fini quand** : tu obtiens une réponse en console et tu sais lire le nombre de tokens consommés.

### 3. Prompt design 🟡

- **Concepts** : rôle, contexte, objectif, contraintes, format de sortie ; comportement quand le modèle ne sait pas.
- [x] Prompt structuré (ROLE / CONTEXT / OBJECTIVE / TASKS / CONSTRAINTS / OUTPUT FORMAT)
- [ ] Le prompt est lu depuis `prompts/` (pas depuis `.env`)
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
- [ ] Corriger le rôle de la réponse : `"assistant"` (pas `"user"`)
- [ ] Limiter l'historique à `HISTORY_LIMIT` messages
- **Fini quand** : le bot se souvient d'une info donnée 5 tours plus tôt, et l'historique est limité.

### 5. Streaming ✅

- **Concepts** : fragments (deltas), temps jusqu'au premier token vs temps total.
- [x] Réponse affichée progressivement en console
- [x] Texte complet reconstitué et ajouté à l'historique
- [ ] Décider quoi faire si le stream est interrompu (garder la réponse partielle ou non)
- **Fini quand** : affichage progressif + réponse complète bien enregistrée.

### 6. Interface Gradio ⬜

- **Concepts** : `gr.ChatInterface` appelle `fn(message, history)` ; l'historique Gradio a son propre format → le **convertir** avant de l'envoyer à OpenAI.
- [ ] Brancher la fonction de chat sur `gr.ChatInterface`
- [ ] Convertir l'historique Gradio (garder seulement `role` + texte)
- [ ] Streaming dans le navigateur (`yield` du texte cumulé)
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

- **Options** : Hugging Face Spaces (simple, fait pour Gradio) ou Docker sur un VPS derrière un reverse proxy HTTPS.
- **Concepts** : secrets en production, volume persistant pour SQLite, protection de l'accès.
- [ ] Choisir l'option
- [ ] Protéger l'accès (une URL publique sans authentification = ta clé API offerte à tout le monde)
- [ ] Volume persistant pour la base
- **Fini quand** : une URL fonctionne, l'accès est protégé et l'historique survit à un redémarrage.

---

## Trois pièges à garder en tête

1. **Coût** : il croît avec la longueur de la conversation, pas seulement avec le nombre de messages.
2. **Streaming et mémoire** : toujours enregistrer la réponse **complète** après le stream.
3. **SQLite en déploiement** : sans volume persistant, tout est perdu à chaque redéploiement.

## Sécurité

- [ ] Régénérer la clé `GEMINI_API_KEY` (affichée par erreur pendant une session)
- [ ] Vérifier avant chaque commit que `.env` n'apparaît pas dans `git status`
