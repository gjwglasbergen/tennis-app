import streamlit as st
from supabase import create_client
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from datetime import datetime
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎾 TennisTracker",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Supabase client ───────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ── Auth ──────────────────────────────────────────────────────────────────────
with open("config.yaml") as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

name, authentication_status, username = authenticator.login("main")

if authentication_status is False:
    st.error("❌ Gebruikersnaam of wachtwoord onjuist.")
    st.stop()

if authentication_status is None:
    st.info("👆 Log in om door te gaan.")
    st.markdown("---")
    st.caption("TennisTracker — Houd jouw wedstrijden bij.")
    st.stop()

# ── Helpers ───────────────────────────────────────────────────────────────────
POINT_TYPES = ["Ace", "Smash", "Volley", "Winner", "Unforced Error", "Dubbele Fout"]
POINT_EMOJI = {
    "Ace": "🎯", "Smash": "💥", "Volley": "🏓",
    "Winner": "🏆", "Unforced Error": "😬", "Dubbele Fout": "❌"
}

def tennis_score_display(games_p1, games_p2, points_p1, points_p2):
    """Convert raw point count to tennis score string."""
    pts = [0, 15, 30, 40]
    if points_p1 >= 3 and points_p2 >= 3:
        diff = points_p1 - points_p2
        if diff == 0:
            return games_p1, games_p2, "40", "40", "Deuce"
        elif diff == 1:
            return games_p1, games_p2, "AD", "40", ""
        elif diff == -1:
            return games_p1, games_p2, "40", "AD", ""
    p1_str = pts[min(points_p1, 3)] if points_p1 < 4 else "40"
    p2_str = pts[min(points_p2, 3)] if points_p2 < 4 else "40"
    return games_p1, games_p2, str(p1_str), str(p2_str), ""

def load_match(match_id):
    resp = supabase.table("matches").select("*").eq("id", match_id).single().execute()
    return resp.data

def load_points(match_id):
    resp = supabase.table("points").select("*").eq("match_id", match_id).order("created_at").execute()
    return resp.data or []

def save_point(match_id, winner, point_type):
    supabase.table("points").insert({
        "match_id": match_id,
        "winner": winner,
        "point_type": point_type,
        "created_at": datetime.utcnow().isoformat(),
    }).execute()

def update_match_score(match_id, sets_p1, sets_p2, games_p1, games_p2,
                       points_p1, points_p2, status="active"):
    supabase.table("matches").update({
        "sets_p1": sets_p1, "sets_p2": sets_p2,
        "games_p1": games_p1, "games_p2": games_p2,
        "points_p1": points_p1, "points_p2": points_p2,
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
    }).eq("id", match_id).execute()

def recalculate_score(points):
    """Recalculate full score from point history."""
    sets_p1, sets_p2 = 0, 0
    games_p1, games_p2 = 0, 0
    raw_p1, raw_p2 = 0, 0

    for pt in points:
        if pt["winner"] == "p1":
            raw_p1 += 1
        else:
            raw_p2 += 1

        # Check game won
        game_won = False
        if raw_p1 >= 4 and raw_p2 >= 4:
            diff = raw_p1 - raw_p2
            if abs(diff) >= 2:
                if diff > 0:
                    games_p1 += 1
                else:
                    games_p2 += 1
                raw_p1, raw_p2 = 0, 0
                game_won = True
        elif raw_p1 >= 4 and raw_p1 - raw_p2 >= 2:
            games_p1 += 1
            raw_p1, raw_p2 = 0, 0
            game_won = True
        elif raw_p2 >= 4 and raw_p2 - raw_p1 >= 2:
            games_p2 += 1
            raw_p1, raw_p2 = 0, 0
            game_won = True

        if game_won:
            # Check set won (best of 6, tiebreak at 6-6)
            if games_p1 >= 6 and games_p1 - games_p2 >= 2:
                sets_p1 += 1
                games_p1, games_p2 = 0, 0
            elif games_p2 >= 6 and games_p2 - games_p1 >= 2:
                sets_p2 += 1
                games_p1, games_p2 = 0, 0
            elif games_p1 == 7 or games_p2 == 7:
                if games_p1 > games_p2:
                    sets_p1 += 1
                else:
                    sets_p2 += 1
                games_p1, games_p2 = 0, 0

    return sets_p1, sets_p2, games_p1, games_p2, raw_p1, raw_p2

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👋 Hallo, {name}!")
    authenticator.logout("Uitloggen", "sidebar")
    st.markdown("---")
    page = st.radio("Navigatie", ["🏠 Dashboard", "➕ Nieuwe Wedstrijd", "📊 Mijn Wedstrijden"])

st.sidebar.markdown("---")
st.sidebar.caption("🎾 TennisTracker v1.0")

# ── Pages ─────────────────────────────────────────────────────────────────────

# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🎾 TennisTracker Dashboard")

    # Active matches
    active = supabase.table("matches").select("*") \
        .eq("owner", username).eq("status", "active") \
        .order("created_at", desc=True).execute().data or []

    if active:
        st.subheader("⚡ Actieve Wedstrijden")
        for m in active:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{m['player1']}** vs **{m['player2']}**")
                    st.caption(f"Sets: {m['sets_p1']}–{m['sets_p2']}  |  Games: {m['games_p1']}–{m['games_p2']}")
                with col2:
                    if st.button("🎮 Beheren", key=f"manage_{m['id']}"):
                        st.session_state["active_match"] = m["id"]
                        st.query_params["match"] = m["id"]
                        st.rerun()
                with col3:
                    share_url = f"?match={m['id']}&view=live"
                    st.code(f"?match={m['id']}&view=live", language=None)
    else:
        st.info("Geen actieve wedstrijden. Maak een nieuwe aan! ➡️")

    st.markdown("---")

    # Recent matches
    recent = supabase.table("matches").select("*") \
        .eq("owner", username).eq("status", "finished") \
        .order("updated_at", desc=True).limit(5).execute().data or []

    if recent:
        st.subheader("📋 Recente Wedstrijden")
        for m in recent:
            winner = m["player1"] if m["sets_p1"] > m["sets_p2"] else m["player2"]
            st.markdown(f"- **{m['player1']}** vs **{m['player2']}** → 🏆 {winner}  "
                        f"({m['sets_p1']}–{m['sets_p2']} sets)")

# ════════════════════════════════════════════════════════════
# NIEUWE WEDSTRIJD
# ════════════════════════════════════════════════════════════
elif page == "➕ Nieuwe Wedstrijd":
    st.title("➕ Nieuwe Wedstrijd Aanmaken")

    with st.form("new_match"):
        col1, col2 = st.columns(2)
        with col1:
            p1 = st.text_input("Speler 1", placeholder="Naam speler 1")
        with col2:
            p2 = st.text_input("Speler 2", placeholder="Naam speler 2")

        col3, col4 = st.columns(2)
        with col3:
            surface = st.selectbox("Ondergrond", ["Hard", "Gravel", "Gras", "Indoor"])
        with col4:
            best_of = st.selectbox("Format", ["Best of 3", "Best of 5"])

        submitted = st.form_submit_button("🎾 Wedstrijd Starten", type="primary", use_container_width=True)

    if submitted:
        if not p1 or not p2:
            st.error("Vul beide spelernamen in.")
        elif p1 == p2:
            st.error("Spelers moeten verschillende namen hebben.")
        else:
            result = supabase.table("matches").insert({
                "player1": p1, "player2": p2,
                "surface": surface, "best_of": int(best_of.split()[-1]),
                "sets_p1": 0, "sets_p2": 0,
                "games_p1": 0, "games_p2": 0,
                "points_p1": 0, "points_p2": 0,
                "status": "active",
                "owner": username,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()

            match_id = result.data[0]["id"]
            st.success(f"✅ Wedstrijd aangemaakt!")
            st.info(f"**Deel link:** `?match={match_id}&view=live`")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🎮 Start Scorebijhouding", type="primary"):
                    st.session_state["active_match"] = match_id
                    st.query_params["match"] = match_id
                    st.rerun()

# ════════════════════════════════════════════════════════════
# MIJN WEDSTRIJDEN
# ════════════════════════════════════════════════════════════
elif page == "📊 Mijn Wedstrijden":
    st.title("📊 Mijn Wedstrijden")

    all_matches = supabase.table("matches").select("*") \
        .eq("owner", username) \
        .order("created_at", desc=True).execute().data or []

    if not all_matches:
        st.info("Nog geen wedstrijden. Maak er een aan!")
    else:
        status_filter = st.selectbox("Filter", ["Alle", "Actief", "Afgerond"])
        for m in all_matches:
            if status_filter == "Actief" and m["status"] != "active":
                continue
            if status_filter == "Afgerond" and m["status"] != "finished":
                continue

            with st.expander(f"{'⚡' if m['status'] == 'active' else '✅'} {m['player1']} vs {m['player2']} — {m['sets_p1']}:{m['sets_p2']} sets"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Sets", f"{m['sets_p1']}–{m['sets_p2']}")
                col2.metric("Games", f"{m['games_p1']}–{m['games_p2']}")
                col3.metric("Ondergrond", m["surface"])

                points = load_points(m["id"])
                if points:
                    st.markdown("**Punt statistieken:**")
                    stats = {}
                    for pt in points:
                        key = f"{pt['winner']}_{pt['point_type']}"
                        stats[key] = stats.get(key, 0) + 1

                    import pandas as pd
                    rows = []
                    for pt_type in POINT_TYPES:
                        p1_count = stats.get(f"p1_{pt_type}", 0)
                        p2_count = stats.get(f"p2_{pt_type}", 0)
                        rows.append({"Type": f"{POINT_EMOJI[pt_type]} {pt_type}",
                                     m["player1"]: p1_count,
                                     m["player2"]: p2_count})
                    df = pd.DataFrame(rows)
                    st.dataframe(df, hide_index=True, use_container_width=True)

                if m["status"] == "active":
                    if st.button("🎮 Score bijhouden", key=f"go_{m['id']}"):
                        st.session_state["active_match"] = m["id"]
                        st.query_params["match"] = m["id"]
                        st.rerun()

# ════════════════════════════════════════════════════════════
# LIVE SCORE / BEHEREN (via query param)
# ════════════════════════════════════════════════════════════
params = st.query_params
if "match" in params:
    match_id = params["match"]
    is_viewer = params.get("view") == "live" and "active_match" not in st.session_state

    match = load_match(match_id)
    if not match:
        st.error("Wedstrijd niet gevonden.")
        st.stop()

    points = load_points(match_id)
    s1, s2, g1, g2, raw1, raw2 = recalculate_score(points)
    _, _, p1_score, p2_score, deuce_label = tennis_score_display(g1, g2, raw1, raw2)

    # ── Score display ──
    st.markdown("---")
    st.markdown(f"## 🎾 {match['player1']} vs {match['player2']}")
    st.caption(f"Ondergrond: {match['surface']}  |  Format: Best of {match['best_of']}")

    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown(f"<h1 style='text-align:center;color:#2ecc71'>{match['player1']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center'>{s1} sets | {g1} games | {p1_score}</h2>", unsafe_allow_html=True)
    with c2:
        st.markdown("<h2 style='text-align:center;margin-top:40px'>VS</h2>", unsafe_allow_html=True)
        if deuce_label:
            st.markdown(f"<p style='text-align:center;color:orange'><b>{deuce_label}</b></p>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<h1 style='text-align:center;color:#e74c3c'>{match['player2']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center'>{s2} sets | {g2} games | {p2_score}</h2>", unsafe_allow_html=True)

    # ── Point history ──
    if points:
        st.markdown("**Laatste 5 punten:**")
        for pt in reversed(points[-5:]):
            winner_name = match["player1"] if pt["winner"] == "p1" else match["player2"]
            emoji = POINT_EMOJI.get(pt["point_type"], "●")
            st.markdown(f"- {emoji} **{winner_name}** — {pt['point_type']}")

    # ── Controls (only for owner / non-viewer) ──
    if not is_viewer and match["status"] == "active" and (match["owner"] == username):
        st.markdown("---")
        st.subheader("🎮 Scorebeheer")

        pt_type = st.selectbox("Type punt", POINT_TYPES,
                               format_func=lambda x: f"{POINT_EMOJI[x]} {x}")

        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_a:
            if st.button(f"🟢 Punt voor {match['player1']}", use_container_width=True, type="primary"):
                save_point(match_id, "p1", pt_type)
                pts = load_points(match_id)
                ns1, ns2, ng1, ng2, np1, np2 = recalculate_score(pts)
                status = "active"
                max_sets = (match["best_of"] + 1) // 2
                if ns1 >= max_sets or ns2 >= max_sets:
                    status = "finished"
                update_match_score(match_id, ns1, ns2, ng1, ng2, np1, np2, status)
                st.rerun()
        with col_b:
            if st.button("↩️ Ongedaan", use_container_width=True):
                last = supabase.table("points").select("id") \
                    .eq("match_id", match_id).order("created_at", desc=True).limit(1).execute().data
                if last:
                    supabase.table("points").delete().eq("id", last[0]["id"]).execute()
                    pts = load_points(match_id)
                    ns1, ns2, ng1, ng2, np1, np2 = recalculate_score(pts)
                    update_match_score(match_id, ns1, ns2, ng1, ng2, np1, np2)
                    st.rerun()
        with col_c:
            if st.button(f"🔴 Punt voor {match['player2']}", use_container_width=True, type="primary"):
                save_point(match_id, "p2", pt_type)
                pts = load_points(match_id)
                ns1, ns2, ng1, ng2, np1, np2 = recalculate_score(pts)
                status = "active"
                max_sets = (match["best_of"] + 1) // 2
                if ns1 >= max_sets or ns2 >= max_sets:
                    status = "finished"
                update_match_score(match_id, ns1, ns2, ng1, ng2, np1, np2, status)
                st.rerun()

        st.markdown("---")
        if match["status"] == "active":
            if st.button("🏁 Wedstrijd Beëindigen", type="secondary"):
                update_match_score(match_id, s1, s2, g1, g2, raw1, raw2, "finished")
                st.success("Wedstrijd afgerond!")
                st.rerun()

    elif is_viewer:
        st.info("👁️ Je bekijkt deze wedstrijd live. Ververs de pagina voor de laatste score.")
        if st.button("🔄 Ververs Score"):
            st.rerun()
        # Auto-refresh every 15 seconds for viewers
        time.sleep(15)
        st.rerun()
