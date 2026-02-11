#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XIsion - Interface Streamlit
Plateforme d'aide à la décision pour la Premier League
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="ScoutOnze - Premier League Analytics",
    page_icon="⚽",
    layout="wide"
)

# Titre principal
st.title("⚽ ScoutOnze - Aide à la décision Premier League 2025-2026")
st.markdown("---")

# Chargement des données
@st.cache_data
def load_data():
    """Charge toutes les données nécessaires"""
    players = pd.read_csv('data/player_form_scores.csv')
    top_by_team = pd.read_csv('data/top_players_by_team.csv')
    matches_scheduled = pd.read_csv('data/matches_scheduled.csv')
    standings = pd.read_csv('data/standings.csv')
    
    return players, top_by_team, matches_scheduled, standings

try:
    df_players, df_top_by_team, df_scheduled, df_standings = load_data()
    
    # Sidebar - Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choisir une page",
        [
            "📊 Vue d'ensemble",
            "⚽ Meilleur XI",
            "👥 Analyse par équipe", 
            "🏆 Top joueurs", 
            "🔍 Recherche joueur", 
            "🔮 Prédictions", 
            "💎 Talents cachés",
            "📈 Évolution forme",
            "📅 Prochains matchs", 
            "⚽ Générateur de composition"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**{len(df_players)} joueurs** analysés")
    st.sidebar.info(f"**Score moyen** : {df_players['Score_Forme'].mean():.1f}/10")
    
    # PAGE 1 : Vue d'ensemble
    if page == "📊 Vue d'ensemble":
        st.header("📊 Vue d'ensemble de la saison")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Joueurs analysés", len(df_players))
        
        with col2:
            best_player = df_players.nlargest(1, 'Score_Forme').iloc[0]
            st.metric("Meilleur score", f"{best_player['Score_Forme']:.1f}", best_player['Joueur'])
        
        with col3:
            avg_score = df_players['Score_Forme'].mean()
            st.metric("Score moyen", f"{avg_score:.1f}/10")
        
        with col4:
            st.metric("Équipes", len(df_players['Equipe_principale'].unique()))
        
        st.markdown("---")
        
        # Distribution des scores
        st.subheader("📈 Distribution des scores de forme")
        
        fig_hist = px.histogram(
            df_players, 
            x='Score_Forme', 
            nbins=30,
            title="Distribution des scores de forme (tous joueurs)",
            labels={'Score_Forme': 'Score de forme', 'count': 'Nombre de joueurs'},
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Scores par poste
        st.subheader("🎯 Scores moyens par poste")
        
        avg_by_position = df_players.groupby('Poste_simplifie')['Score_Forme'].mean().sort_values(ascending=False)
        
        fig_bar = px.bar(
            x=avg_by_position.index,
            y=avg_by_position.values,
            title="Score moyen par poste",
            labels={'x': 'Poste', 'y': 'Score moyen'},
            color=avg_by_position.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Top 10 global
        st.subheader("🔥 Top 10 joueurs en forme (tous postes confondus)")
        
        top_10 = df_players.nlargest(10, 'Score_Forme')[
            ['Joueur', 'Equipe_principale', 'Poste_simplifie', 'Score_Forme', 'Matchs', 'Minutes', 'Buts', 'Passes_decisives']
        ]
        
        st.dataframe(
            top_10.reset_index(drop=True),
            use_container_width=True,
            height=400
        )
    
    # PAGE 2 : Meilleur XI
    elif page == "⚽ Meilleur XI":
        st.header("⚽ Meilleur XI en forme - Premier League")
        
        st.markdown("""
        **Formation 4-3-3** | Basé sur les scores de forme des 6 derniers matchs
        """)
        
        # Créer le terrain avec matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 14))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 14)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Couleur du terrain
        field_color = '#1a5f3a'
        fig.patch.set_facecolor(field_color)
        ax.set_facecolor(field_color)
        
        # Lignes du terrain
        ax.plot([1, 9], [0.5, 0.5], 'white', linewidth=2)
        ax.plot([1, 9], [13.5, 13.5], 'white', linewidth=2)
        ax.plot([1, 1], [0.5, 13.5], 'white', linewidth=2)
        ax.plot([9, 9], [0.5, 13.5], 'white', linewidth=2)
        ax.plot([1, 9], [7, 7], 'white', linewidth=2)
        
        # Cercle central
        circle = plt.Circle((5, 7), 1.2, color='white', fill=False, linewidth=2)
        ax.add_patch(circle)
        
        # Surfaces de réparation
        ax.plot([2.5, 2.5], [0.5, 2.5], 'white', linewidth=2)
        ax.plot([7.5, 7.5], [0.5, 2.5], 'white', linewidth=2)
        ax.plot([2.5, 7.5], [2.5, 2.5], 'white', linewidth=2)
        
        ax.plot([2.5, 2.5], [13.5, 11.5], 'white', linewidth=2)
        ax.plot([7.5, 7.5], [13.5, 11.5], 'white', linewidth=2)
        ax.plot([2.5, 7.5], [11.5, 11.5], 'white', linewidth=2)
        
        # Sélectionner les meilleurs joueurs par poste
        best_gk = df_players[df_players['Poste_simplifie'] == 'GK'].nlargest(1, 'Score_Forme')
        best_def = df_players[df_players['Poste_simplifie'] == 'DEF'].nlargest(4, 'Score_Forme')
        best_mid = df_players[df_players['Poste_simplifie'] == 'MID'].nlargest(3, 'Score_Forme')
        best_fwd = df_players[df_players['Poste_simplifie'] == 'FWD'].nlargest(3, 'Score_Forme')
        
        # Positions sur le terrain (x, y)
        def add_player(ax, x, y, name, score, team, color='#00ff87'):
            # Cercle joueur
            circle = plt.Circle((x, y), 0.35, color=color, ec='white', linewidth=2, zorder=10)
            ax.add_patch(circle)
            
            # Nom
            ax.text(x, y-0.7, name, ha='center', va='top', 
                    fontsize=8, fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7, edgecolor='none'))
            
            # Équipe
            ax.text(x, y-1.1, team, ha='center', va='top',
                    fontsize=6, color='white', style='italic')
            
            # Score
            ax.text(x, y, f'{score:.1f}', ha='center', va='center',
                    fontsize=10, fontweight='bold', color='black', zorder=11)
        
        # Ajouter le gardien
        if len(best_gk) > 0:
            player = best_gk.iloc[0]
            add_player(ax, 5, 1.5, player['Joueur'], player['Score_Forme'], 
                      player['Equipe_principale'].split(',')[0], color='#ffd700')
        
        # Ajouter les défenseurs
        def_positions = [(2.5, 3.5), (4.2, 3.8), (5.8, 3.8), (7.5, 3.5)]
        for i, (_, player) in enumerate(best_def.iterrows()):
            if i < len(def_positions):
                x, y = def_positions[i]
                add_player(ax, x, y, player['Joueur'], player['Score_Forme'],
                          player['Equipe_principale'].split(',')[0], color='#4169e1')
        
        # Ajouter les milieux
        mid_positions = [(3, 6.5), (5, 7), (7, 6.5)]
        for i, (_, player) in enumerate(best_mid.iterrows()):
            if i < len(mid_positions):
                x, y = mid_positions[i]
                add_player(ax, x, y, player['Joueur'], player['Score_Forme'],
                          player['Equipe_principale'].split(',')[0], color='#00ff87')
        
        # Ajouter les attaquants
        fwd_positions = [(2.5, 10), (5, 10.5), (7.5, 10)]
        for i, (_, player) in enumerate(best_fwd.iterrows()):
            if i < len(fwd_positions):
                x, y = fwd_positions[i]
                add_player(ax, x, y, player['Joueur'], player['Score_Forme'],
                          player['Equipe_principale'].split(',')[0], color='#ff4444')
        
        # Titre
        ax.text(5, 13.2, 'Meilleur XI - Premier League', 
                ha='center', va='center', fontsize=16, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8, edgecolor='white', linewidth=2))
        
        # Légende
        legend_y = 0.2
        ax.text(1.5, legend_y, '●', ha='center', fontsize=16, color='#ffd700')
        ax.text(2.2, legend_y, 'GK', ha='left', fontsize=9, color='white', fontweight='bold')
        
        ax.text(3.2, legend_y, '●', ha='center', fontsize=16, color='#4169e1')
        ax.text(3.9, legend_y, 'DEF', ha='left', fontsize=9, color='white', fontweight='bold')
        
        ax.text(5, legend_y, '●', ha='center', fontsize=16, color='#00ff87')
        ax.text(5.7, legend_y, 'MID', ha='left', fontsize=9, color='white', fontweight='bold')
        
        ax.text(7, legend_y, '●', ha='center', fontsize=16, color='#ff4444')
        ax.text(7.7, legend_y, 'FWD', ha='left', fontsize=9, color='white', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Stats du XI
        st.markdown("---")
        st.subheader("📊 Statistiques du XI")
        
        col1, col2, col3 = st.columns(3)
        
        all_xi = pd.concat([best_gk, best_def, best_mid, best_fwd])
        
        with col1:
            avg_score = all_xi['Score_Forme'].mean()
            st.metric("Score moyen du XI", f"{avg_score:.1f}/10")
        
        with col2:
            total_goals = all_xi['Buts'].sum()
            st.metric("Buts totaux", int(total_goals))
        
        with col3:
            total_assists = all_xi['Passes_decisives'].sum()
            st.metric("Passes décisives", int(total_assists))
        
        # Tableau détaillé
        st.markdown("### 📋 Détails du XI")
        
        xi_display = all_xi[[
            'Joueur', 'Equipe_principale', 'Poste_simplifie', 'Score_Forme',
            'Matchs', 'Buts', 'Passes_decisives'
        ]].copy()
        
        xi_display.columns = ['Joueur', 'Équipe', 'Poste', 'Score', 'Matchs', 'Buts', 'Passes']
        
        st.dataframe(
            xi_display.reset_index(drop=True),
            use_container_width=True
        )
    
    # PAGE 3 : Analyse par équipe
    elif page == "👥 Analyse par équipe":
        st.header("👥 Analyse par équipe")
        
        # Sélection de l'équipe
        # Nettoyer les noms d'équipes (enlever les multiples équipes)
        unique_teams = sorted(df_players['Equipe_principale'].str.split(',').str[0].unique())
        selected_team = st.selectbox("Choisir une équipe", unique_teams)
        
        if selected_team:
            # Filtrer les joueurs de l'équipe (même si multiples équipes)
            team_players = df_players[
                df_players['Equipe_principale'].str.contains(selected_team, na=False, regex=False)
            ].copy()
            
            st.markdown(f"### ⚽ {selected_team}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Effectif analysé", len(team_players))
            
            with col2:
                avg_team_score = team_players['Score_Forme'].mean()
                st.metric("Score moyen équipe", f"{avg_team_score:.1f}/10")
            
            with col3:
                best_player_team = team_players.nlargest(1, 'Score_Forme').iloc[0]
                st.metric("Meilleur joueur", best_player_team['Joueur'], f"{best_player_team['Score_Forme']:.1f}")
            
            st.markdown("---")
            
            # Top joueurs par poste
            st.subheader("🔥 Meilleurs joueurs par poste")
            
            for poste in ['GK', 'DEF', 'MID', 'FWD']:
                players_at_pos = team_players[team_players['Poste_simplifie'] == poste].nlargest(5, 'Score_Forme')
                
                if len(players_at_pos) > 0:
                    st.markdown(f"**{poste}**")
                    
                    cols = st.columns(len(players_at_pos))
                    for idx, (_, player) in enumerate(players_at_pos.iterrows()):
                        with cols[idx]:
                            st.metric(
                                player['Joueur'][:15] + "..." if len(player['Joueur']) > 15 else player['Joueur'],
                                f"{player['Score_Forme']:.1f}",
                                f"{player['Buts']}⚽ {player['Passes_decisives']}🎯"
                            )
            
            st.markdown("---")
            
            # Tableau détaillé
            st.subheader("📋 Effectif complet")
            
            team_players_display = team_players[
                ['Joueur', 'Poste_simplifie', 'Score_Forme', 'Matchs', 'Minutes', 'Buts', 'Passes_decisives']
            ].sort_values('Score_Forme', ascending=False)
            
            st.dataframe(
                team_players_display.reset_index(drop=True),
                use_container_width=True,
                height=500
            )
    
    # PAGE 4 : Top joueurs
    elif page == "🏆 Top joueurs":
        st.header("🏆 Top joueurs par poste")
        
        # Sélection du poste
        position = st.selectbox("Choisir un poste", ['GK', 'DEF', 'MID', 'FWD'])
        
        # Slider pour le nombre de joueurs
        top_n = st.slider("Nombre de joueurs à afficher", 5, 50, 10)
        
        # Filtrer et afficher
        players_at_pos = df_players[df_players['Poste_simplifie'] == position].nlargest(top_n, 'Score_Forme')
        
        st.subheader(f"🔥 Top {top_n} {position}")
        
        # Graphique
        fig = px.bar(
            players_at_pos,
            x='Joueur',
            y='Score_Forme',
            color='Equipe_principale',
            title=f"Top {top_n} {position} - Scores de forme",
            labels={'Score_Forme': 'Score de forme', 'Joueur': 'Joueur'},
            hover_data=['Matchs', 'Minutes', 'Buts', 'Passes_decisives']
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.dataframe(
            players_at_pos[['Joueur', 'Equipe_principale', 'Score_Forme', 'Matchs', 'Minutes', 'Buts', 'Passes_decisives']].reset_index(drop=True),
            use_container_width=True
        )
    
    # PAGE 5 : Recherche joueur
    elif page == "🔍 Recherche joueur":
        st.header("🔍 Recherche de joueur")
        
        # Barre de recherche
        search_query = st.text_input("Rechercher un joueur par nom", placeholder="Ex: Bruno Fernandes")
        
        if search_query:
            # Recherche insensible à la casse et partielle
            results = df_players[
                df_players['Joueur'].str.contains(search_query, case=False, na=False)
            ].sort_values('Score_Forme', ascending=False)
            
            if len(results) == 0:
                st.warning(f"Aucun joueur trouvé pour '{search_query}'")
            else:
                st.success(f"**{len(results)} joueur(s) trouvé(s)**")
                st.markdown("---")
                
                # Afficher chaque joueur
                for idx, player in results.iterrows():
                    with st.expander(f"⚽ {player['Joueur']} - {player['Equipe_principale']} ({player['Poste_simplifie']}) - Score: {player['Score_Forme']:.1f}/10"):
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Score de forme", f"{player['Score_Forme']:.1f}/10")
                            st.metric("Poste", player['Poste_simplifie'])
                        
                        with col2:
                            st.metric("Équipe", player['Equipe_principale'])
                            st.metric("Matchs joués", player['Matchs'])
                        
                        with col3:
                            st.metric("Minutes", player['Minutes'])
                            st.metric("Buts", f"⚽ {player['Buts']}")
                        
                        st.markdown("---")
                        
                        # Stats détaillées
                        st.subheader("📊 Statistiques détaillées")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Passes décisives", f"🎯 {player['Passes_decisives']}")
                        
                        with col2:
                            if 'Matchs_6_derniers' in player:
                                st.metric("Matchs (6 derniers)", player['Matchs_6_derniers'])
                            else:
                                st.metric("Minutes/match", f"{player['Minutes']/player['Matchs']:.0f}")
                        
                        with col3:
                            buts_par_match = player['Buts'] / player['Matchs'] if player['Matchs'] > 0 else 0
                            st.metric("Buts/match", f"{buts_par_match:.2f}")
                        
                        with col4:
                            passes_par_match = player['Passes_decisives'] / player['Matchs'] if player['Matchs'] > 0 else 0
                            st.metric("Passes/match", f"{passes_par_match:.2f}")
                        
                        # Comparaison avec la moyenne du poste
                        st.markdown("---")
                        st.subheader("📈 Comparaison avec la moyenne du poste")
                        
                        avg_score_poste = df_players[df_players['Poste_simplifie'] == player['Poste_simplifie']]['Score_Forme'].mean()
                        diff_score = player['Score_Forme'] - avg_score_poste
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                f"Score moyen ({player['Poste_simplifie']})",
                                f"{avg_score_poste:.1f}/10"
                            )
                        
                        with col2:
                            st.metric(
                                "Différence",
                                f"{diff_score:+.1f}",
                                delta=f"{diff_score:+.1f}",
                                delta_color="normal"
                            )
                        
                        # Classement au poste
                        rank = len(df_players[
                            (df_players['Poste_simplifie'] == player['Poste_simplifie']) & 
                            (df_players['Score_Forme'] > player['Score_Forme'])
                        ]) + 1
                        
                        total_at_position = len(df_players[df_players['Poste_simplifie'] == player['Poste_simplifie']])
                        
                        st.info(f"🏆 Classement : **{rank}e / {total_at_position}** {player['Poste_simplifie']} de Premier League")
        
        else:
            st.info("👆 Tapez un nom de joueur pour commencer la recherche")
            
            # Afficher quelques exemples
            st.markdown("### 💡 Exemples de recherche :")
            
            top_3 = df_players.nlargest(3, 'Score_Forme')
            
            for _, player in top_3.iterrows():
                st.markdown(f"- {player['Joueur']} ({player['Equipe_principale']}) - {player['Score_Forme']:.1f}/10")
    
    # PAGE 6 : Prédictions meilleur buteur
    elif page == "🔮 Prédictions":
        st.header("🔮 Prédictions de fin de saison")
        
        st.markdown("### ⚽ Qui va finir meilleur buteur ?")
        
        # Calcul de la projection
        # Nombre de matchs restants (estimation basée sur le calendrier)
        total_matches_season = 38
        
        # Calculer les projections pour les attaquants et milieux QUI MARQUENT
        top_scorers = df_players[
            (df_players['Poste_simplifie'].isin(['FWD', 'MID'])) &
            (df_players['Buts'] >= 3) &  # Au moins 3 buts
            (df_players['Matchs'] >= 5)  # Au moins 5 matchs joués
        ].copy()
        
        if len(top_scorers) == 0:
            st.warning("Pas assez de données pour faire des prédictions.")
        else:
            # Calculer la moyenne de buts par match
            top_scorers['Buts_par_match'] = top_scorers['Buts'] / top_scorers['Matchs']
            
            # Ne garder que ceux avec une moyenne décente (>0.15 buts/match)
            top_scorers = top_scorers[top_scorers['Buts_par_match'] >= 0.15]
            
            # Estimation des matchs restants pour chaque joueur (38 - matchs joués)
            top_scorers['Matchs_restants'] = total_matches_season - top_scorers['Matchs']
            
            # Projection de buts en fin de saison
            top_scorers['Projection_buts'] = (
                top_scorers['Buts'] + 
                (top_scorers['Buts_par_match'] * top_scorers['Matchs_restants'])
            ).round(1)
            
            # Top 10 des projections
            top_10_projections = top_scorers.nlargest(10, 'Projection_buts')
            
            # Graphique des projections
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_10_projections['Joueur'],
                y=top_10_projections['Buts'],
                name='Buts actuels',
                marker_color='lightblue',
                text=top_10_projections['Buts'],
                textposition='auto',
            ))
            
            fig.add_trace(go.Bar(
                x=top_10_projections['Joueur'],
                y=top_10_projections['Projection_buts'] - top_10_projections['Buts'],
                name='Buts supplémentaires projetés',
                marker_color='darkblue',
                text=(top_10_projections['Projection_buts'] - top_10_projections['Buts']).round(1),
                textposition='auto',
            ))
            
            fig.update_layout(
                barmode='stack',
                title="Projection de buts en fin de saison",
                xaxis_title="Joueur",
                yaxis_title="Nombre de buts",
                xaxis_tickangle=-45,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.markdown("### 📊 Détails des projections")
            
            st.info("💡 **Méthodologie :** Projection basée sur la moyenne de buts par match des joueurs ayant marqué au moins 3 buts cette saison.")
            
            projection_display = top_10_projections[[
                'Joueur', 'Equipe_principale', 'Poste_simplifie', 'Buts', 'Matchs', 
                'Buts_par_match', 'Matchs_restants', 'Projection_buts'
            ]].copy()
            
            projection_display['Buts_par_match'] = projection_display['Buts_par_match'].round(2)
            projection_display.columns = [
                'Joueur', 'Équipe', 'Poste', 'Buts actuels', 'Matchs joués', 
                'Moy. buts/match', 'Matchs restants', 'Total projeté'
            ]
            
            st.dataframe(
                projection_display.reset_index(drop=True),
                use_container_width=True,
                height=400
            )
            
            # Insights
            best_projection = top_10_projections.iloc[0]
            st.success(f"""
            🎯 **Meilleur buteur projeté :** {best_projection['Joueur']} ({best_projection['Equipe_principale']})
            - Buts actuels : {best_projection['Buts']:.0f}
            - Projection totale : **{best_projection['Projection_buts']:.1f} buts**
            - Moyenne : {best_projection['Buts_par_match']:.2f} buts/match
            - Buts supplémentaires attendus : {(best_projection['Projection_buts'] - best_projection['Buts']):.1f}
            """)
    
    # PAGE 7 : Détecteur de talents cachés
    elif page == "💎 Talents cachés":
        st.header("💎 Détecteur de talents cachés")
        
        st.markdown("""
        **Critères de détection :**
        - ⚡ Score de forme élevé (>6.5/10)
        - ⏱️ Temps de jeu limité (<60% des minutes disponibles)
        - 🎯 Performances prometteuses
        """)
        
        # Calculer le temps de jeu en %
        max_minutes_possible = df_players['Matchs'] * 90
        df_players['Pct_temps_jeu'] = (df_players['Minutes'] / max_minutes_possible * 100).round(1)
        
        # Critères de talents cachés
        hidden_gems = df_players[
            (df_players['Score_Forme'] > 6.5) &
            (df_players['Pct_temps_jeu'] < 60) &
            (df_players['Matchs'] >= 5)  # Au moins 5 matchs joués
        ].copy()
        
        hidden_gems = hidden_gems.sort_values('Score_Forme', ascending=False)
        
        if len(hidden_gems) == 0:
            st.warning("Aucun talent caché détecté avec ces critères.")
        else:
            st.success(f"🔍 **{len(hidden_gems)} talents cachés** détectés !")
            
            # Graphique
            fig = px.scatter(
                hidden_gems.head(20),
                x='Pct_temps_jeu',
                y='Score_Forme',
                size='Buts',
                color='Poste_simplifie',
                hover_name='Joueur',
                hover_data={
                    'Equipe_principale': True,
                    'Buts': True,
                    'Passes_decisives': True,
                    'Pct_temps_jeu': ':.1f',
                    'Score_Forme': ':.1f'
                },
                title="Talents cachés : Score vs Temps de jeu",
                labels={
                    'Pct_temps_jeu': 'Temps de jeu (%)',
                    'Score_Forme': 'Score de forme (/10)',
                    'Poste_simplifie': 'Poste'
                },
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Top 10 talents cachés
            st.markdown("### 🌟 Top 10 talents cachés")
            
            for idx, player in hidden_gems.head(10).iterrows():
                with st.expander(f"⭐ {player['Joueur']} - {player['Equipe_principale']} ({player['Poste_simplifie']})"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Score de forme", f"{player['Score_Forme']:.1f}/10")
                    
                    with col2:
                        st.metric("Temps de jeu", f"{player['Pct_temps_jeu']:.1f}%")
                    
                    with col3:
                        st.metric("Buts", player['Buts'])
                    
                    with col4:
                        st.metric("Passes", player['Passes_decisives'])
                    
                    st.markdown(f"""
                    **Analyse :**
                    - {player['Matchs']} matchs joués ({player['Minutes']} minutes)
                    - Malgré un temps de jeu limité, affiche un excellent score de forme
                    - Pourrait devenir titulaire avec plus d'opportunités
                    """)
    
    # PAGE 8 : Évolution de la forme
    elif page == "📈 Évolution forme":
        st.header("📈 Évolution de la forme des joueurs")
        
        st.markdown("### 📊 Sélectionner des joueurs à comparer")
        
        # Sélection de joueurs
        all_players_names = sorted(df_players['Joueur'].unique())
        
        selected_players = st.multiselect(
            "Choisir jusqu'à 5 joueurs",
            all_players_names,
            default=all_players_names[:3] if len(all_players_names) >= 3 else all_players_names,
            max_selections=5
        )
        
        if selected_players:
            # Créer un graphique d'évolution simulé
            # Note : On simule l'évolution car on n'a pas les données match par match dans player_form_scores
            
            st.info("📝 Note : Les données d'évolution sont basées sur les statistiques disponibles")
            
            # Affichage des stats actuelles des joueurs sélectionnés
            comparison_data = df_players[df_players['Joueur'].isin(selected_players)][[
                'Joueur', 'Equipe_principale', 'Poste_simplifie', 'Score_Forme', 
                'Matchs', 'Minutes', 'Buts', 'Passes_decisives'
            ]]
            
            st.markdown("### 📋 Comparaison des joueurs sélectionnés")
            
            # Graphique en barres comparatif
            fig = go.Figure()
            
            for _, player in comparison_data.iterrows():
                fig.add_trace(go.Bar(
                    name=player['Joueur'],
                    x=['Score Forme', 'Buts', 'Passes', 'Matchs/10'],
                    y=[
                        player['Score_Forme'],
                        player['Buts'],
                        player['Passes_decisives'],
                        player['Matchs'] / 10  # Divisé par 10 pour l'échelle
                    ],
                ))
            
            fig.update_layout(
                barmode='group',
                title="Comparaison des statistiques",
                yaxis_title="Valeur",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau détaillé
            st.dataframe(
                comparison_data.reset_index(drop=True),
                use_container_width=True
            )
            
            # Radar chart des compétences
            st.markdown("### 🎯 Profil de performance")
            
            fig_radar = go.Figure()
            
            for _, player in comparison_data.iterrows():
                # Normaliser les valeurs pour le radar
                buts_norm = min(player['Buts'] / 10 * 10, 10)
                passes_norm = min(player['Passes_decisives'] / 5 * 10, 10)
                matchs_norm = min(player['Matchs'] / 24 * 10, 10)
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=[player['Score_Forme'], buts_norm, passes_norm, matchs_norm, player['Score_Forme']],
                    theta=['Score Forme', 'Buts', 'Passes', 'Régularité', 'Score Forme'],
                    fill='toself',
                    name=player['Joueur']
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
        else:
            st.info("👆 Sélectionnez des joueurs pour voir leur évolution")
    
    # PAGE 9 : Prochains matchs
    elif page == "📅 Prochains matchs":
        st.header("📅 Prochains matchs")
        
        df_scheduled['datetime'] = pd.to_datetime(df_scheduled['datetime'])
        df_scheduled_sorted = df_scheduled.sort_values('datetime').head(20)
        
        st.subheader("🗓️ Calendrier des 20 prochains matchs")
        
        for idx, match in df_scheduled_sorted.iterrows():
            col1, col2, col3, col4 = st.columns([3, 1, 3, 2])
            
            with col1:
                st.markdown(f"**{match['home_team_name']}**")
            
            with col2:
                st.markdown("🆚")
            
            with col3:
                st.markdown(f"**{match['away_team_name']}**")
            
            with col4:
                date_str = match['datetime'].strftime('%d/%m/%Y %H:%M')
                st.markdown(f"📅 {date_str}")
            
            st.markdown("---")
    
    # PAGE 10 : Générateur de composition
    elif page == "⚽ Générateur de composition":
        st.header("⚽ Générateur de composition optimale")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Nettoyer les noms d'équipes (enlever les multiples équipes)
            unique_teams = sorted(df_players['Equipe_principale'].str.split(',').str[0].unique())
            selected_team = st.selectbox("Choisir une équipe", unique_teams)
        
        with col2:
            formation = st.selectbox("Choisir une formation", ['4-3-3', '4-2-3-1', '3-5-2'])
        
        if st.button("🔄 Générer la composition", type="primary"):
            
            # Définir les besoins selon la formation
            if formation == '4-3-3':
                needs = {'GK': 1, 'DEF': 4, 'MID': 3, 'FWD': 3}
            elif formation == '4-2-3-1':
                needs = {'GK': 1, 'DEF': 4, 'MID': 5, 'FWD': 1}
            elif formation == '3-5-2':
                needs = {'GK': 1, 'DEF': 3, 'MID': 5, 'FWD': 2}
            
            # Générer le XI
            team_players = df_players[
                df_players['Equipe_principale'].str.contains(selected_team, na=False, regex=False)
            ]
            
            if len(team_players) == 0:
                st.error(f"Aucun joueur trouvé pour {selected_team}")
            else:
                st.markdown(f"### 🏟️ {selected_team} - Formation {formation}")
                st.markdown("---")
                
                best_xi = []
                all_selected_ids = set()
                
                for poste, count in needs.items():
                    # Filtrer les joueurs disponibles (pas encore sélectionnés)
                    available_players = team_players[
                        ~team_players.index.isin(all_selected_ids)
                    ]
                    
                    players_at_pos = available_players[
                        available_players['Poste_simplifie'] == poste
                    ].nlargest(count, 'Score_Forme')
                    
                    # Si pas assez de joueurs à ce poste (surtout pour FWD)
                    if len(players_at_pos) < count and poste == 'FWD':
                        # Compléter avec les meilleurs milieux offensifs disponibles
                        missing = count - len(players_at_pos)
                        backup_players = available_players[
                            (available_players['Poste_simplifie'] == 'MID') & 
                            (~available_players.index.isin(players_at_pos.index))
                        ].nlargest(missing, 'Score_Forme')
                        
                        if len(backup_players) > 0:
                            st.info(f"⚠️ Seulement {len(players_at_pos)} attaquant(s) pur(s). Complété avec {len(backup_players)} milieu(x) offensif(s).")
                            players_at_pos = pd.concat([players_at_pos, backup_players])
                    
                    st.subheader(f"**{poste}**")
                    
                    for _, player in players_at_pos.iterrows():
                        all_selected_ids.add(player.name)
                        
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                        
                        with col1:
                            st.markdown(f"**{player['Joueur']}**")
                        
                        with col2:
                            st.metric("Score", f"{player['Score_Forme']:.1f}")
                        
                        with col3:
                            st.markdown(f"{player['Matchs']} matchs")
                        
                        with col4:
                            st.markdown(f"⚽ {player['Buts']} | 🎯 {player['Passes_decisives']}")
                    
                    st.markdown("---")
                
                # Score moyen du XI
                selected_indices = list(all_selected_ids)
                if len(selected_indices) > 0:
                    best_xi_scores = team_players.loc[selected_indices, 'Score_Forme'].tolist()
                    avg_xi_score = sum(best_xi_scores) / len(best_xi_scores)
                    
                    st.success(f"✅ Score moyen du XI : {avg_xi_score:.1f}/10")

except FileNotFoundError as e:
    st.error("⚠️ Erreur : Fichiers de données manquants.")
    st.info("Veuillez d'abord exécuter le script `04_calcul_forme_joueurs_v2.py` pour générer les données.")
    st.code("python 04_calcul_forme_joueurs_v2.py")

# Footer
st.markdown("---")
st.markdown("**ScoutOnze** - Plateforme d'aide à la décision football | Données : Premier League 2025-2026")
