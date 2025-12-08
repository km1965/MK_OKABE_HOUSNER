import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ResultsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        
        # Titre
        title = ctk.CTkLabel(self, text="Résultats", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Zone de texte pour afficher les résultats
        self.results_text = ctk.CTkTextbox(self, width=500, height=300, font=ctk.CTkFont(size=12))
        self.results_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame pour le graphique
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configuration des poids pour redimensionnement
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = None
    
    def display_results(self, results):
        """Affiche les résultats de calcul"""
        self.results_text.delete("1.0", "end")
        
        # Déterminer la norme utilisée
        seismic_code = results.get('seismic_code', 'EC8')
        code_display = "EC8 France 🇫🇷" if seismic_code == 'EC8' else "RPS 2011 Maroc 🇲🇦"
        
        # Labels selon la norme
        if seismic_code == 'EC8':
            zone_label = "Zone sismique"
            importance_label = "Catégorie importance"
            soil_label = "Classe de sol"
            coef_label = "Coefficient r"
        else:  # RPS2011
            zone_label = "Zone sismique"
            importance_label = "Classe d'importance"
            soil_label = "Classe de site"
            coef_label = "Coefficient R"
        
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║         CALCUL POUSSÉE DYNAMIQUE - MONONOBE-OKABE            ║
║                    Norme: {code_display:^28}              ║
╚══════════════════════════════════════════════════════════════╝

📊 PARAMÈTRES D'ENTRÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Géométrie:
  • Hauteur du mur:           {results['height']:.2f} m
  • Inclinaison parement β:   {results['beta']:.2f}°
  • Pente du remblai i:       {results['backfill_slope']:.2f}°

Sol:
  • Angle de frottement φ:    {results['phi']:.2f}°
  • Frottement sol-mur δ:     {results['delta']:.2f}°
  • Poids volumique γ:        {results['gamma']:.2f} kN/m³

Séisme {code_display}:
  • {zone_label:23} {results['zone']}
  • {importance_label:23} {results['importance']}
  • {soil_label:23} {results['soil_class']}
  • {coef_label:23} {results['r_factor']:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 COEFFICIENTS SISMIQUES
  • kh (horizontal):          {results['kh']:.4f}
  • kv (vertical):            {results['kv']:.4f}
  • θ (angle sismique):       {results['theta']:.2f}°

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RÉSULTATS - POUSSÉE DES TERRES (Mononobe-Okabe)
  • Kae (coefficient):        {results['kae']:.4f}
  • Pae (poussée totale):     {results['pae']:.2f} kN/m
  • Point d'application:      {results['height']/3:.2f} m depuis la base

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Ajouter section Housner si eau présente
        if results.get('has_water', False):
            text += f"""
💧 POUSSÉE HYDRODYNAMIQUE (Housner)

Composante IMPULSIVE:
  • Masse impulsive mi:       {results['mi']:.2f} t/m
  • Période Ti:               ≈ 0 s (mur rigide)
  • Accélération Ai:          {results['kh']:.3f} g
  • Pression Pi:              {results['Pi']:.2f} kN/m
  • Hauteur application hi:   {results['hi']:.2f} m

Composante CONVECTIVE:
  • Masse convective mc:      {results['mc']:.2f} t/m
  • Période Tc:               {results['Tc']:.2f} s
  • Pression Pc:              {results['Pc']:.2f} kN/m
  • Hauteur application hc:   {results['hc']:.2f} m

Combinaison ({results.get('combination_method', 'SRSS')}):
  • Pw (total hydro):         {results['Pw']:.2f} kN/m

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 POUSSÉE TOTALE SISMIQUE
  • Pae (terres):             {results['pae']:.2f} kN/m
  • Pw (eau):                 {results['Pw']:.2f} kN/m
  • Ptotal = Pae + Pw:        {results['Ptotal']:.2f} kN/m

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏗️ VÉRIFICATION STABILITÉ (E.L.U. Sismique)

1. GLISSEMENT (Fs >= 1.5)
  • Fs calculé:               {results.get('Fs_sliding', 0):.2f}
  • Statut:                   {'✅ OK' if results.get('Fs_sliding', 0) >= 1.5 else '❌ NON CONFORME'}

2. RENVERSEMENT (Fr >= 1.5)
  • Fr calculé:               {results.get('Fr_overturning', 0):.2f}
  • Statut:                   {'✅ OK' if results.get('Fr_overturning', 0) >= 1.5 else '❌ NON CONFORME'}

3. PORTANCE (Contrainte au sol)
  • Excentrement e:           {results.get('eccentricity', 0):.3f} m (Limite: {results.get('width_B', 0)/3:.3f} m)
  • Contrainte Réf (Meyerhof):{results.get('sigma_ref', 0):.2f} kPa
  • Contrainte Max (Navier):  {results.get('sigma_max', 0):.2f} kPa
  • Statut Excentrement:      {'✅ OK' if results.get('eccentricity', 0) < results.get('width_B', 0)/3 else '❌ DÉCOLLEMENT EXCESSIF'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏗️ VÉRIFICATION STABILITÉ (E.L.U. Sismique)

1. GLISSEMENT (Fs >= 1.5)
  • Fs calculé:               {results.get('Fs_sliding', 0):.2f}
  • Statut:                   {'✅ OK' if results.get('Fs_sliding', 0) >= 1.5 else '❌ NON CONFORME'}

2. RENVERSEMENT (Fr >= 1.5)
  • Fr calculé:               {results.get('Fr_overturning', 0):.2f}
  • Statut:                   {'✅ OK' if results.get('Fr_overturning', 0) >= 1.5 else '❌ NON CONFORME'}

3. PORTANCE (Contrainte au sol)
  • Excentrement e:           {results.get('eccentricity', 0):.3f} m (Limite: {results.get('width_B', 0)/3:.3f} m)
  • Contrainte Réf (Meyerhof):{results.get('sigma_ref', 0):.2f} kPa
  • Contrainte Max (Navier):  {results.get('sigma_max', 0):.2f} kPa
  • Statut Excentrement:      {'✅ OK' if results.get('eccentricity', 0) < results.get('width_B', 0)/3 else '❌ DÉCOLLEMENT EXCESSIF'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")
        
        # Dessiner le schéma
        self.draw_wall_diagram(results)
    
    def draw_wall_diagram(self, results):
        """Dessine un schéma du mur avec la poussée"""
        # Supprimer l'ancien canvas s'il existe
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Créer une nouvelle figure
        fig, ax = plt.subplots(figsize=(6, 5), facecolor='#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        
        H = results['height']
        beta_rad = np.radians(results['beta'])
        i_rad = np.radians(results['backfill_slope'])
        
        # Dessiner le mur
        wall_base = 0.3
        wall_x = [0, wall_base * np.tan(beta_rad), wall_base * np.tan(beta_rad), 0, 0]
        wall_y = [0, H, H, 0, 0]
        ax.fill(wall_x, wall_y, color='#4a4a4a', edgecolor='white', linewidth=2, label='Mur')
        
        # Dessiner le remblai
        backfill_length = H * 2
        backfill_x = [wall_base * np.tan(beta_rad), wall_base * np.tan(beta_rad) + backfill_length, 
                      wall_base * np.tan(beta_rad) + backfill_length, wall_base * np.tan(beta_rad)]
        backfill_y = [H, H + backfill_length * np.tan(i_rad), 0, 0]
        ax.fill(backfill_x, backfill_y, color='#8b7355', alpha=0.6, label='Remblai')
        
        # Dessiner la poussée (flèche)
        force_y = H / 3  # Point d'application à H/3
        force_scale = results['pae'] / 100  # Échelle pour visualisation
        ax.arrow(wall_base * np.tan(beta_rad), force_y, force_scale, 0, 
                head_width=H*0.08, head_length=force_scale*0.2, fc='red', ec='red', linewidth=3,
                label=f"Pae = {results['pae']:.1f} kN/m")
        
        # Annotations
        ax.text(wall_base * np.tan(beta_rad) / 2, H / 2, f'H = {H}m', 
               color='white', ha='center', fontsize=10, weight='bold')
        
        ax.set_xlim(-0.5, backfill_length + 1)
        ax.set_ylim(-0.5, H + 1)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, color='gray')
        ax.legend(loc='upper right', facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        plt.title('Schéma du Mur et Poussée', color='white', fontsize=14, weight='bold')
        plt.xlabel('Distance (m)', color='white')
        plt.ylabel('Hauteur (m)', color='white')
        plt.tight_layout()
        
        # Intégrer dans le frame
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def display_text(self, text):
        """Affiche un texte brut dans la zone de résultats"""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")
        
        # Effacer le graphique si présent
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

    def display_error(self, message):
        """Affiche un message d'erreur"""
        self.display_text(f"❌ ERREUR :\n\n{message}")

    def draw_frame_diagram(self, results):
        """
        Dessine le schéma du cadre avec les diagrammes M, N.
        
        :param results: Dictionnaire contenant les résultats du calcul tank
        """
        # Supprimer l'ancien canvas s'il existe
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Créer une figure avec 2 sous-graphiques côte à côte
        fig, axes = plt.subplots(1, 2, figsize=(10, 5), facecolor='#2b2b2b')
        
        # --- Sous-graphique 1: Schéma du cadre avec charges ---
        ax1 = axes[0]
        ax1.set_facecolor('#2b2b2b')
        
        # Dimensions
        W = results.get('tank_width', 4.0)
        H = results.get('tank_height', 3.0)
        th = results.get('th_wall', 0.25)
        
        # Cadre (axes neutres)
        frame_x = [0, 0, W, W, 0]
        frame_y = [0, H, H, 0, 0]
        ax1.plot(frame_x, frame_y, 'c-', linewidth=4, label='Cadre')
        
        # Épaisseurs (remplissage)
        # Voile gauche
        ax1.fill([-th/2, th/2, th/2, -th/2], [0, 0, H, H], color='#555555', alpha=0.8)
        # Voile droit
        ax1.fill([W-th/2, W+th/2, W+th/2, W-th/2], [0, 0, H, H], color='#555555', alpha=0.8)
        # Traverse sup
        ax1.fill([0, W, W, 0], [H-th/2, H-th/2, H+th/2, H+th/2], color='#555555', alpha=0.8)
        # Radier
        ax1.fill([0, W, W, 0], [-th/2, -th/2, th/2, th/2], color='#555555', alpha=0.8)
        
        # Poussée des terres (flèches à gauche)
        Pae = results.get('pae', 0)
        if Pae > 0:
            n_arrows = 5
            for i in range(n_arrows):
                y_pos = H * (i + 0.5) / n_arrows
                arrow_len = 0.5 + 0.5 * i / n_arrows  # Trapézoïdale
                ax1.arrow(-arrow_len - 0.3, y_pos, arrow_len, 0, 
                         head_width=0.1, head_length=0.1, fc='orange', ec='orange')
            ax1.text(-1.5, H/2, f'Pae\n{Pae:.0f} kN/m', color='orange', ha='center', fontsize=9)
        
        # Poussée eau intérieure (flèches vers l'extérieur)
        hw = results.get('water_level_in', 0)
        if hw > 0:
            n_arrows = 4
            for i in range(n_arrows):
                y_pos = hw * (i + 0.5) / n_arrows
                arrow_len = 0.3 + 0.3 * i / n_arrows
                # Vers la gauche
                ax1.arrow(th/2 + 0.1, y_pos, arrow_len, 0, 
                         head_width=0.08, head_length=0.05, fc='blue', ec='blue')
            ax1.fill([th/2, th/2, th/2 + 0.1, th/2 + 0.1], [0, hw, hw, 0], 
                    color='blue', alpha=0.3, label='Eau')
        
        # Points A, B, C, D
        ax1.plot(0, H, 'ro', markersize=10)
        ax1.text(-0.3, H + 0.2, 'A', color='white', fontsize=12, fontweight='bold')
        ax1.plot(W, H, 'ro', markersize=10)
        ax1.text(W + 0.1, H + 0.2, 'B', color='white', fontsize=12, fontweight='bold')
        ax1.plot(W, 0, 'ro', markersize=10)
        ax1.text(W + 0.1, -0.3, 'C', color='white', fontsize=12, fontweight='bold')
        ax1.plot(0, 0, 'ro', markersize=10)
        ax1.text(-0.3, -0.3, 'D', color='white', fontsize=12, fontweight='bold')
        
        ax1.set_xlim(-2, W + 2)
        ax1.set_ylim(-1, H + 1)
        ax1.set_aspect('equal')
        ax1.set_title('Schéma du Cadre', color='white', fontsize=12, fontweight='bold')
        ax1.tick_params(colors='white')
        ax1.grid(True, alpha=0.2, color='gray')
        for spine in ax1.spines.values():
            spine.set_color('white')
        
        # --- Sous-graphique 2: Diagramme des Moments ---
        ax2 = axes[1]
        ax2.set_facecolor('#2b2b2b')
        
        M_A = results.get('M_A', 0)
        M_D = results.get('M_D', 0)
        M_mid = results.get('M_mid', 0)
        
        # Échelle pour les moments
        M_scale = max(abs(M_A), abs(M_D), abs(M_mid), 1) / 1.5
        
        # Cadre de référence (traits fins)
        ax2.plot([0, 0, W, W, 0], [0, H, H, 0, 0], 'c--', linewidth=1, alpha=0.5)
        
        # Diagramme des moments sur le voile gauche (entre D et A)
        # Moment M_D en bas, M_A en haut
        y_voile = np.linspace(0, H, 20)
        # Distribution parabolique simplifiée
        M_voile = M_D + (M_A - M_D) * (y_voile / H)
        x_voile = -M_voile / M_scale
        ax2.fill_betweenx(y_voile, 0, x_voile, color='red', alpha=0.5)
        ax2.plot(x_voile, y_voile, 'r-', linewidth=2)
        
        # Annotations moments
        ax2.text(-M_D/M_scale - 0.3, 0.2, f'{M_D:.0f}', color='yellow', fontsize=9)
        ax2.text(-M_A/M_scale - 0.3, H - 0.2, f'{M_A:.0f}', color='yellow', fontsize=9)
        
        # Traverse supérieure
        if M_mid != 0:
            x_trav = np.linspace(0, W, 20)
            # Moment parabolique sur traverse
            M_trav = M_A + (M_mid - M_A) * 4 * (x_trav/W) * (1 - x_trav/W)
            y_trav = H + M_trav / M_scale
            ax2.fill_between(x_trav, H, y_trav, color='red', alpha=0.5)
            ax2.plot(x_trav, y_trav, 'r-', linewidth=2)
            ax2.text(W/2, H + M_mid/M_scale + 0.2, f'{M_mid:.0f}', color='yellow', fontsize=9, ha='center')
        
        ax2.set_xlim(-3, W + 3)
        ax2.set_ylim(-1, H + 2)
        ax2.set_aspect('equal')
        ax2.set_title('Diagramme des Moments [kNm]', color='white', fontsize=12, fontweight='bold')
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.2, color='gray')
        for spine in ax2.spines.values():
            spine.set_color('white')
        
        plt.tight_layout()
        
        # Intégrer dans le frame
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

