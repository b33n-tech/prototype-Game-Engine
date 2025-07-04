import streamlit as st
import json
import time
import matplotlib.pyplot as plt
import numpy as np

# Charger le scénario
with open("fire_scenario.json", "r", encoding="utf-8") as f:
    story_data = json.load(f)

# Initialisation des variables de session
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "current_node" not in st.session_state:
    st.session_state.current_node = "start"
    st.session_state.traits = []
    st.session_state.history = []
    st.session_state.timings = []
    st.session_state.start_time = time.time()
    st.session_state.scene_id = "start"

# Appliquer les conséquences d’un choix
def apply_consequences(consequences):
    if "traits" in consequences:
        for trait in consequences["traits"]:
            if trait not in st.session_state.traits:
                st.session_state.traits.append(trait)

# Afficher la scène actuelle
def show_scene():
    node = story_data[st.session_state.current_node]
    st.markdown(f"### {node['text']}")

    # Chrono : relancer à chaque nouvelle scène
    if st.session_state.scene_id != st.session_state.current_node:
        st.session_state.start_time = time.time()
        st.session_state.scene_id = st.session_state.current_node

    if node["choices"]:
        for i, choice in enumerate(node["choices"]):
            if st.button(choice["label"], key=f"choice_{i}"):
                end_time = time.time()
                elapsed = round(end_time - st.session_state.start_time, 2)

                apply_consequences(choice.get("consequences", {}))
                st.session_state.history.append({
                    "from": st.session_state.current_node,
                    "to": choice["next"],
                    "label": choice["label"],
                    "consequences": choice.get("consequences", {})
                })
                st.session_state.timings.append({
                    "scene": st.session_state.current_node,
                    "choice": choice["label"],
                    "time": elapsed
                })

                st.session_state.current_node = choice["next"]
                st.rerun()
    else:
        st.success("🎯 Fin du scénario.")
        show_results()

# Afficher les résultats de fin
def show_results():
    st.markdown("---")

    # Temps moyen
    avg_time = round(sum(t["time"] for t in st.session_state.timings) / len(st.session_state.timings), 2)

    # Comptage des traits
    trait_scores = {}
    for step in st.session_state.history:
        for trait in step["consequences"].get("traits", []):
            trait_scores[trait] = trait_scores.get(trait, 0) + 1

    # Traits dominants
    dominant_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
    top_traits = [t[0] for t in dominant_traits[:3]]

    # ➤ Synthèse narrative
    st.subheader("🧾 Analyse comportementale (synthèse narrative)")
    narrative = "Lors de ce scénario, votre comportement a montré "
    if avg_time < 5:
        narrative += "une capacité de réaction rapide, presque instinctive, face au danger. "
    elif avg_time < 15:
        narrative += "une réactivité réfléchie, avec des décisions prises dans un temps court mais sans précipitation. "
    else:
        narrative += "une forme d’hésitation ou de prudence accrue dans la prise de décision. "
    if top_traits:
        narrative += f"Vos traits comportementaux les plus notables ont été : **{', '.join(top_traits)}**."
    else:
        narrative += "Aucun trait comportemental marquant n’a été identifié."
    st.markdown(narrative)

    # ➤ Liste des traits
    st.subheader("🧠 Traits comportementaux détectés :")
    if st.session_state.traits:
        st.markdown(", ".join([f"**{t}**" for t in st.session_state.traits]))
    else:
        st.markdown("Aucun trait distinct détecté.")

    # ➤ Historique des choix
    st.subheader("📜 Historique des choix :")
    for step in st.session_state.history:
        st.markdown(f"- **{step['from']}** → *{step['label']}* → **{step['to']}**")

    # ➤ Temps de réponse
    st.subheader("⏱️ Temps de réponse par scène :")
    for t in st.session_state.timings:
        st.markdown(f"- **{t['scene']}** → {t['time']} sec (*{t['choice']}*)")

    # ➤ Interprétation temps moyen
    st.subheader("🧠 Interprétation du temps moyen de réponse :")
    st.markdown(f"- Temps moyen : **{avg_time} sec**")
    if avg_time < 5:
        st.markdown("⚡ **Réaction instinctive** : vous prenez vos décisions très rapidement, ce qui peut indiquer de la confiance… ou de l’impulsivité.")
    elif avg_time < 15:
        st.markdown("🧩 **Réaction réfléchie** : vos choix montrent une capacité à analyser rapidement sous pression.")
    else:
        st.markdown("⏳ **Réaction hésitante** : vous prenez le temps, ce qui peut être lié à un besoin de certitude ou une crainte de se tromper.")

    # ➤ Radar comportemental
    if st.session_state.traits:
        st.subheader("📈 Profil comportemental (diagramme radar)")

        all_traits = ["impulsif", "protecteur", "pragmatique", "suiveur"]
        values = [trait_scores.get(trait, 0) for trait in all_traits]
        labels = all_traits
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        ax.plot(angles, values, color="red", linewidth=2)
        ax.fill(angles, values, color="red", alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_yticks([])
        ax.set_title("Profil détecté")
        st.pyplot(fig)

    # ➤ Redémarrer
    if st.button("🔄 Recommencer"):
        for key in ["game_started", "current_node", "traits", "history", "timings", "scene_id", "start_time"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Interface principale
st.title("🔥 Scénario Incendie – Jeu de Prévention Évolutif")

if not st.session_state.game_started:
    st.markdown("Bienvenue dans ce scénario immersif. Vous allez être confronté à plusieurs choix dans une situation d'urgence.")
    st.markdown("🎯 Votre comportement sera observé pour dresser un **profil de réaction en situation de crise**.")
    if st.button("▶️ Lancer le jeu"):
        st.session_state.game_started = True
        st.rerun()
else:
    show_scene()
