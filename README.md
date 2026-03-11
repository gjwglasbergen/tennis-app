# 🎾 TennisTracker

Houd tennisscores bij en deel live wedstrijden met vrienden.

---

## 🚀 Setup in 5 stappen

### Stap 1: Supabase database aanmaken

1. Ga naar [supabase.com](https://supabase.com) en maak een gratis account
2. Klik **New Project** → geef het een naam (bijv. `tennisTracker`)
3. Ga naar **SQL Editor** en plak de inhoud van `schema.sql` → klik **Run**
4. Ga naar **Settings → API** en kopieer:
   - **Project URL** (bijv. `https://abc123.supabase.co`)
   - **anon public key**

### Stap 2: Secrets instellen

Bewerk `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://jouw-project.supabase.co"
SUPABASE_KEY = "jouw-anon-key"
```

> ⚠️ Voeg `.streamlit/secrets.toml` toe aan `.gitignore`!

### Stap 3: Wachtwoord instellen

Genereer een gehashed wachtwoord:

```python
import streamlit_authenticator as stauth
hashed = stauth.Hasher(['jouwwachtwoord']).generate()
print(hashed[0])
```

Plak de output in `config.yaml` bij `password:`.

### Stap 4: Lokaal testen

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Stap 5: Deployen op Streamlit Cloud (gratis)

1. Push je code naar GitHub (zonder `secrets.toml`!)
2. Ga naar [share.streamlit.io](https://share.streamlit.io)
3. Verbind je GitHub repo → selecteer `app.py`
4. Voeg secrets toe via **Settings → Secrets** in het dashboard
5. Klik **Deploy** 🎉

---

## 🎮 Gebruik

| Functie | Hoe |
|---|---|
| Wedstrijd aanmaken | "Nieuwe Wedstrijd" menu |
| Score bijhouden | Klik op speler na elk punt |
| Punt type kiezen | Selecteer type vóór het klikken |
| Live delen | Kopieer de `?match=xxx&view=live` link |
| Ongedaan maken | "↩️ Ongedaan" knop |

## 📊 Punt types

- 🎯 **Ace** — directe service winner
- 💥 **Smash** — smash winner
- 🏓 **Volley** — net winner
- 🏆 **Winner** — gewonnen slagwisseling
- 😬 **Unforced Error** — eigen fout
- ❌ **Dubbele Fout** — twee fouten bij opslag

---

## 📁 Projectstructuur

```
tennis-app/
├── app.py              # Hoofd applicatie
├── config.yaml         # Gebruikersaccounts
├── requirements.txt    # Python dependencies
├── schema.sql          # Database tabellen
└── .streamlit/
    └── secrets.toml    # API keys (niet naar GitHub!)
```
