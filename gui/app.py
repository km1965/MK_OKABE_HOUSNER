import customtkinter as ctk
from gui.inputs import InputFrame
from gui.tank_inputs import TankInputFrame
from gui.results import ResultsFrame
from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.ec8_france import EC8France
from core.rps2011_maroc import RPS2011Maroc
from core.housner import Housner, WaterParameters
from core.stability import StabilityVerifier
from core.frame_analysis import RectangularFrame, FrameGeometry, FrameResults
from core.tank_verifications import TankVerifications, ConcreteProperties, SteelProperties, SectionProperties, LoadCombinations, RPS2011SeismicVerifications
from utils.persistence import ProjectManager
from tkinter import Menu, filedialog
import sys
import math

class MononobeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("Poussée Dynamique - Mononobe-Okabe EC8")
        self.geometry("1400x800")
        
        # Gestion de la fermeture propre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # État du fichier
        self.current_file = None
        
        # Création du menu
        self.create_menu()
        
        # Configuration de la grille
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Titre principal
        title = ctk.CTkLabel(main_frame, 
                            text="📐 CALCUL DE POUSSÉE DYNAMIQUE DES TERRES\nMéthode Mononobe-Okabe (EC8 - Annexe Nationale France)",
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Frame gauche (Inputs)
        left_frame = ctk.CTkFrame(main_frame, width=600)
        left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Sélecteur de Mode
        self.mode_var = ctk.StringVar(value="Mur de Soutènement")
        self.mode_selector = ctk.CTkSegmentedButton(left_frame, 
                                                   values=["Mur de Soutènement", "Bâche à Eau / Cadre"],
                                                   variable=self.mode_var,
                                                   command=self.toggle_mode)
        self.mode_selector.pack(pady=(10, 5), padx=10, fill="x")
        
        # Container pour les inputs (Scrollable)
        self.input_container = ctk.CTkScrollableFrame(left_frame, width=580)
        self.input_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame Mur (InputFrame existant)
        self.input_frame = InputFrame(self.input_container)
        self.input_frame.pack(fill="both", expand=True)
        
        # Frame Bâche (Nouveau)
        self.tank_frame = TankInputFrame(self.input_container)
        # On ne le pack pas tout de suite (caché par défaut)
        
        # Frame droit (Résultats)
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        self.results_frame = ResultsFrame(right_frame)
        self.results_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Boutons d'action
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        calc_button = ctk.CTkButton(button_frame, text="🧮 CALCULER", 
                                   command=self.calculate,
                                   width=200, height=40,
                                   font=ctk.CTkFont(size=16, weight="bold"))
        calc_button.pack(side="left", padx=10)
        
        export_button = ctk.CTkButton(button_frame, text="📄 EXPORTER PDF", 
                                     command=self.export_pdf,
                                     width=200, height=40,
                                     font=ctk.CTkFont(size=16, weight="bold"))
        export_button.pack(side="left", padx=10)
        
        analysis_button = ctk.CTkButton(button_frame, text="📈 ANALYSE PARAMÉTRIQUE", 
                                       command=self.open_analysis,
                                       width=240, height=40,
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       fg_color="#2B8A3E", hover_color="#216E31")
        analysis_button.pack(side="left", padx=10)
        
        clear_button = ctk.CTkButton(button_frame, text="🔄 RÉINITIALISER", 
                                    command=self.reset,
                                    width=200, height=40,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    fg_color="gray")
        clear_button.pack(side="left", padx=10)
    
    def toggle_mode(self, value):
        """Change le mode d'affichage (Mur / Bâche)"""
        if value == "Mur de Soutènement":
            self.tank_frame.pack_forget()
            self.input_frame.pack(fill="both", expand=True)
            self.title("Poussée Dynamique - Mur de Soutènement")
        else:
            self.input_frame.pack_forget()
            self.tank_frame.pack(fill="both", expand=True)
            self.title("Poussée Dynamique - Bâche à Eau / Cadre Enterré")
    def create_menu(self):
        """Crée la barre de menu"""
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # Menu Fichier
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        file_menu.add_command(label="Nouveau", command=self.new_project)
        file_menu.add_command(label="Ouvrir...", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Enregistrer", command=self.save_project)
        file_menu.add_command(label="Enregistrer sous...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing)
        
        # Menu Aide
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

    def new_project(self):
        """Nouveau projet (réinitialise les champs)"""
        self.reset()
        self.current_file = None
        self.title("Poussée Dynamique - Nouveau Projet")

    def open_project(self):
        """Ouvre un projet existant"""
        filename = filedialog.askopenfilename(
            title="Ouvrir un projet",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            data = ProjectManager.load_project(filename)
            if data:
                # Détecter le mode du projet
                if data.get('mode') == 'tank' or 'tank_width' in data:
                    # Mode Bâche
                    self.mode_var.set("Bâche à Eau / Cadre")
                    self.toggle_mode("Bâche à Eau / Cadre")
                    self.tank_frame.set_values(data)
                else:
                    # Mode Mur
                    self.mode_var.set("Mur de Soutènement")
                    self.toggle_mode("Mur de Soutènement")
                    self.input_frame.set_values(data)
                
                self.current_file = filename
                self.title(f"Poussée Dynamique - {filename}")
                
    def save_project(self):
        """Sauvegarde le projet courant"""
        if self.current_file:
            # Détecter le mode actuel
            if self.mode_var.get() == "Bâche à Eau / Cadre":
                values = self.tank_frame.get_values()
                values['mode'] = 'tank'
            else:
                values = self.input_frame.get_values()
                values['mode'] = 'wall'
            
            if ProjectManager.save_project(values, self.current_file):
                print(f"Projet sauvegardé : {self.current_file}")
        else:
            self.save_project_as()
            
    def save_project_as(self):
        """Sauvegarde sous..."""
        filename = filedialog.asksaveasfilename(
            title="Enregistrer le projet",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            # Détecter le mode actuel
            if self.mode_var.get() == "Bâche à Eau / Cadre":
                values = self.tank_frame.get_values()
                values['mode'] = 'tank'
            else:
                values = self.input_frame.get_values()
            if ProjectManager.save_project(values, filename):
                self.current_file = filename
                self.title(f"Poussée Dynamique - {filename}")

    def show_about(self):
        """Affiche la fenêtre À propos"""
        about_window = ctk.CTkToplevel(self)
        about_window.title("À propos")
        about_window.geometry("400x300")
        
        ctk.CTkLabel(about_window, text="Mononobe-Okabe Calculator", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(about_window, text="Version 2.1 (Module Bâche)").pack()
        ctk.CTkLabel(about_window, text="© 2025 - Génie Civil").pack(pady=20)
    def calculate_tank(self):
        """Calcul spécifique pour la bâche à eau (Statique + Sismique)"""
        try:
            # Validation des entrées
            is_valid, errors = self.tank_frame.validate_inputs()
            if not is_valid:
                error_msg = "⚠️ ERREURS DE SAISIE :\n\n" + "\n".join(f"• {e}" for e in errors)
                self.results_frame.display_error(error_msg)
                return
            
            values = self.tank_frame.get_values()
            
            # 1. Géométrie du cadre
            geo = FrameGeometry(
                width=values['tank_width'],
                height=values['tank_height'],
                th_top=values['th_top'],
                th_bot=values['th_bot'],
                th_wall=values['th_wall'],
                depth=values['tank_length']
            )
            
            frame = RectangularFrame(geo, E=30e6) # E béton
            
            # ========================================
            # ANALYSE MULTI-CAS DE CHARGES
            # ========================================
            
            H_mur = values['tank_height']
            phi_rad = math.radians(values['phi'])
            Ka = math.tan(math.pi/4 - phi_rad/2)**2
            
            # --- CAS 1: VIDE + TERRES (Max compression traverse) ---
            q_dead_top = values['th_top'] * values['gamma_concrete']
            q_soil_top = values['soil_cover'] * values['gamma_soil']
            q_top_total = q_dead_top + q_soil_top
            
            res_vertical = frame.solve_uniform_load_top(q_top_total)
            
            # Poussée terres statique
            q_earth_top_stat = Ka * values['gamma_soil'] * values['soil_cover']
            q_earth_bot_stat = Ka * values['gamma_soil'] * (values['soil_cover'] + H_mur)
            res_earth_static = frame.solve_earth_pressure(q_earth_top_stat, q_earth_bot_stat)
            
            # Sollicitations CAS 1 (Vide)
            cas1_M_A = res_vertical.M_A + res_earth_static.M_A
            cas1_M_D = res_earth_static.M_D
            cas1_N_top = res_earth_static.N_top  # Compression
            
            # --- CAS 2: PLEIN STATIQUE (Max traction traverse) ---
            q_water_bot = 10.0 * values['water_level_in']
            res_water_static = frame.solve_hydrostatic_load_walls(q_water_bot)
            
            # Sollicitations CAS 2 (Plein)
            cas2_M_A = res_vertical.M_A + res_earth_static.M_A - res_water_static.M_A
            cas2_M_D = res_earth_static.M_D - res_water_static.M_D
            cas2_N_top = res_water_static.N_top - res_earth_static.N_top  # Traction
            
            # --- CAS 3: PLEIN + SÉISME (Cas dimensionnant) ---
            
            # Coefficients sismiques
            seismic_code = values.get('seismic_code', 'EC8')
            
            if seismic_code == 'EC8':
                kh = EC8France.calculate_kh(
                    zone=values['zone'],
                    category=values['importance'],
                    soil_class=values['soil_class'],
                    r_factor=values['r_factor']
                )
                kv = EC8France.calculate_kv(kh, values['zone'])
            else: # RPS2011
                kh = RPS2011Maroc.calculate_kh(
                    zone=values['zone'],
                    classe=values['importance'],
                    site=values['soil_class'],
                    r_factor=values['r_factor']
                )
                kv = RPS2011Maroc.calculate_kv(kh)
            
            # Mononobe-Okabe
            wall_dummy = WallGeometry(height=H_mur, batter_angle=0, backfill_slope=0)
            soil_params = SoilParameters(phi=values['phi'], delta=values['delta'], gamma=values['gamma_soil'])
            seismic_params = SeismicParameters(kh=kh, kv=kv)
            
            Kae = MononobeOkabe.calculate_kae(wall_dummy, soil_params, seismic_params)
            
            q_earth_top_dyn = Kae * values['gamma_soil'] * values['soil_cover'] * (1 - kv)
            q_earth_bot_dyn = Kae * values['gamma_soil'] * (values['soil_cover'] + H_mur) * (1 - kv)
            Pae_dyn = (q_earth_top_dyn + q_earth_bot_dyn) / 2 * H_mur
            
            # Calcul de la poussée statique (pour afficher l'incrément)
            Pa_static = (q_earth_top_stat + q_earth_bot_stat) / 2 * H_mur
            delta_Pae = Pae_dyn - Pa_static
            
            res_earth_seismic = frame.solve_earth_pressure(q_earth_top_dyn, q_earth_bot_dyn)
            
            # Housner
            res_housner = FrameResults()
            housner_results = {}
            
            if values['water_level_in'] > 0:
                water_params = WaterParameters(
                    hw=values['water_level_in'],
                    L=values['tank_width'],
                    gamma_w=10.0
                )
                
                mi = Housner.calculate_impulsive_mass(water_params)
                mc = Housner.calculate_convective_mass(water_params)
                Tc = Housner.calculate_convective_period(water_params)
                
                Ai = kh * 9.81
                Ac = kh * 9.81 * 0.4 if Tc > 1.0 else kh * 9.81
                
                Pi = mi * Ai
                Pc = mc * Ac
                
                hi = Housner.get_impulsive_height(water_params)
                hc = Housner.get_convective_height(water_params)
                
                h_app_i = hi + values['th_bot']/2
                h_app_c = hc + values['th_bot']/2
                
                res_impulsive = frame.solve_point_load_walls(Pi, h_app_i)
                res_convective = frame.solve_point_load_walls(Pc, h_app_c)
                
                res_housner.M_A = math.sqrt(res_impulsive.M_A**2 + res_convective.M_A**2)
                res_housner.M_D = math.sqrt(res_impulsive.M_D**2 + res_convective.M_D**2)
                res_housner.N_top = math.sqrt(res_impulsive.N_top**2 + res_convective.N_top**2)
                res_housner.N_bot = math.sqrt(res_impulsive.N_bot**2 + res_convective.N_bot**2)
                
                # Poussée hydrostatique (pour affichage PDF)
                P_hydro_static = 0.5 * 10.0 * values['water_level_in']**2
                
                housner_results = {
                    'mi': mi, 'mc': mc, 'Pi': Pi, 'Pc': Pc, 
                    'hi': hi, 'hc': hc, 
                    'P_hydro_static': P_hydro_static
                }
            
            # Sollicitations CAS 3 (Plein + Séisme)
            cas3_M_A = abs(res_vertical.M_A + res_earth_seismic.M_A - (res_water_static.M_A + res_housner.M_A))
            cas3_M_D = abs(res_earth_seismic.M_D - (res_water_static.M_D + res_housner.M_D))
            cas3_N_top = (res_water_static.N_top + res_housner.N_top) - res_earth_seismic.N_top
            
            # ENVELOPPE DES CAS
            M_A_env = max(abs(cas1_M_A), abs(cas2_M_A), cas3_M_A)
            M_D_env = max(abs(cas1_M_D), abs(cas2_M_D), cas3_M_D)
            N_top_env = max(abs(cas1_N_top), abs(cas2_N_top), abs(cas3_N_top))
            
            # Cas dimensionnant pour affichage (Plein + Séisme)
            M_A_tot = cas3_M_A
            M_D_tot = cas3_M_D
            N_top_tot = cas3_N_top
            
            # Flottaison
            flotation = frame.check_flotation(values['water_level_out'], values['gamma_concrete'])
            
            # --- D. VÉRIFICATIONS ---
            L_radier = values['tank_length']
            B_radier = values['tank_width'] + values['th_wall']
            A_radier = L_radier * B_radier
            
            V_horizontal = Pae_dyn * L_radier
            if housner_results:
                V_horizontal += (housner_results['Pi'] + housner_results['Pc']) * 0.4
            
            W_stab = flotation['weight']
            
            sliding = TankVerifications.check_sliding(
                V_horizontal=V_horizontal,
                W_total=W_stab,
                friction_coef=values.get('friction_coef', 0.5),
                A_base=A_radier
            )
            
            M_base = M_D_tot * L_radier
            bearing = TankVerifications.check_bearing_capacity(
                N_total=W_stab,
                M_total=M_base,
                L=L_radier,
                B=B_radier,
                sigma_adm=values.get('sigma_adm', 200.0)
            )
            
            # Ferraillage
            concrete = ConcreteProperties(fc28=values['fc28'])
            steel = SteelProperties(fyk=values.get('fyk', 500.0))
            section_wall = SectionProperties(b=1.0, h=values['th_wall'], enrobage=values.get('enrobage', 0.04))
            
            M_Ed_wall = M_D_env  # Enveloppe
            reinf_wall = TankVerifications.calculate_flexural_reinforcement(
                M_Ed=M_Ed_wall, section=section_wall, concrete=concrete, steel=steel
            )
            
            section_slab = SectionProperties(b=1.0, h=values['th_bot'], enrobage=values.get('enrobage', 0.04))
            reinf_slab = TankVerifications.calculate_flexural_reinforcement(
                M_Ed=M_D_env, section=section_slab, concrete=concrete, steel=steel
            )
            
            # Effort tranchant
            V_Ed_wall = Pae_dyn + (housner_results.get('Pi', 0) + housner_results.get('Pc', 0)) * 0.4 if housner_results else Pae_dyn
            shear_wall = TankVerifications.check_shear(
                V_Ed=V_Ed_wall, section=section_wall, concrete=concrete, steel=steel, As_long=reinf_wall['As_required']
            )
            
            # Fissuration ELS (w_max = 0.2mm pour étanchéité)
            M_ser = M_D_env * 0.7  # Approx ELS ≈ 0.7 * ELU
            cracking = TankVerifications.check_cracking(
                M_ser=M_ser,
                section=section_wall,
                concrete=concrete,
                steel=steel,
                As_provided=reinf_wall['As_required'],
                w_max=0.2
            )
            
            # ========================================
            # VÉRIFICATIONS RPS 2011 AVANCÉES
            # ========================================
            
            # Effort Tranchant de Base (RPS 2011 Art. 6.2)
            base_shear = RPS2011SeismicVerifications.calculate_base_shear(
                W_total=W_stab,
                zone=values['zone'],
                site=values['soil_class'],
                classe_importance=values['importance'],
                K=2.0  # Coefficient réservoirs
            )
            
            # COMBINAISON DES FORCES SISMIQUES (Correction)
            # V_total = V_base (Inertie Structure) + Pae (Poussée Terres Dyn) + Ph (Hydrodynamique)
            V_inertie = base_shear['V_design']
            V_terres = Pae_dyn * L_radier
            V_hydro = (housner_results.get('Pi', 0) + housner_results.get('Pc', 0)) * L_radier if housner_results else 0
            
            # Somme des efforts horizontaux pour la stabilité
            V_total_seismic = V_inertie + V_terres + V_hydro
            
            # Vérification Renversement (RPS 2011 Art. 9.2.1)
            # On prend une hauteur d'application pondérée ou conservative
            # V_inertie à 0.6H, V_terres à H/3 (approx), V_hydro à hi/hc
            # Pour simplifier et être conservatif ici, on applique V_inertie à 0.6H
            H_app = H_mur * 0.6 
            
            # Recalcul du moment de renversement total
            M_overturning_inertie = V_inertie * H_app
            M_overturning_terres = V_terres * (H_mur / 3) # Point application approx Pae
            M_overturning_hydro = V_hydro * (0.4 * H_mur) # Point application approx
            
            # Si on veut utiliser la méthode check_overturning existante qui prend V et H_app global
            # On calcule un H_app équivalent ou on passe le moment directement si possible (à voir dans core)
            # Ici on passe V_total_seismic et un H_app moyen pondéré
            
            if V_total_seismic > 0:
                H_app_equiv = (M_overturning_inertie + M_overturning_terres + M_overturning_hydro) / V_total_seismic
            else:
                H_app_equiv = H_app

            overturning = RPS2011SeismicVerifications.check_overturning(
                W_total=W_stab,
                V_design=V_total_seismic,
                B=B_radier,
                H_app=H_app_equiv
            )
            
            # Mise à jour pour affichage/export
             # On sauvegarde les valeurs détaillées
            base_shear['V_inertie'] = V_inertie
            base_shear['V_terres'] = V_terres
            base_shear['V_hydro'] = V_hydro
            base_shear['V_total'] = V_total_seismic
            
            # Rigidité Radier
            raft_rigidity = RPS2011SeismicVerifications.check_raft_rigidity(
                L=L_radier,
                B=B_radier,
                e=values['th_bot']
            )
            
            # Déplacements
            E_beton = 30e6  # kPa
            I_mur = 1.0 * values['th_wall']**3 / 12  # m⁴ pour 1m de largeur
            displacement = RPS2011SeismicVerifications.check_displacement(
                V_design=base_shear['V_design'],
                H=H_mur,
                E=E_beton,
                I_section=I_mur
            )
            
            # Flexion Composée Voile (N + M)
            N_voile = N_top_tot  # Effort normal dans le voile
            combined = RPS2011SeismicVerifications.check_combined_bending(
                N_Ed=N_voile,
                M_Ed=M_D_env,
                section=section_wall,
                concrete=concrete,
                steel=steel
            )
            
            # Poinçonnement Radier (aux angles)
            N_poinc = W_stab / 4  # Charge sur 1/4
            u_1 = 4 * 2 * section_slab.d + 4 * values['th_wall']  # Périmètre critique
            punching = RPS2011SeismicVerifications.check_punching(
                N_Ed=N_poinc,
                d=section_slab.d,
                u_1=u_1,
                concrete=concrete
            )
            
            # Glissement Interface Voile-Radier (EC2 6.2.5)
            z_interface = 0.9 * section_wall.d
            interface = RPS2011SeismicVerifications.check_interface_sliding(
                V_Ed=V_Ed_wall,
                b_i=values['th_wall'],
                z=z_interface,
                concrete=concrete,
                steel=steel
            )
            
            # ========================================
            # VÉRIFICATION POTEAUX (si présents)
            # ========================================
            column_result = None
            n_poteaux_x = int(values.get('n_poteaux_x', 0))
            n_poteaux_z = int(values.get('n_poteaux_z', 0))
            n_poteaux_total = n_poteaux_x * n_poteaux_z
            
            if n_poteaux_total > 0:
                # Hauteur poteaux = z_dalle (au-dessus TN)
                h_poteau = values.get('z_dalle', 2.0)
                L_0 = 0.7 * h_poteau  # Longueur flambement (bi-encastré ≈ 0.7L)
                
                # Charge sur poteaux = dalle + exploitation
                A_dalle = values['tank_width'] * values['tank_length']
                G_dalle = values['th_top'] * values['gamma_concrete'] * A_dalle
                Q_dalle = values.get('Q_dalle', 2.5) * A_dalle
                
                # Charge ELU par poteau
                N_Ed_poteau = (1.35 * G_dalle + 1.5 * Q_dalle) / n_poteaux_total
                
                column_result = RPS2011SeismicVerifications.check_column(
                    N_Ed=N_Ed_poteau,
                    L_0=L_0,
                    a=values.get('dim_poteau_a', 0.30),
                    b=values.get('dim_poteau_b', 0.30),
                    concrete=concrete,
                    steel=steel
                )
            
            # Résultats à afficher
            results_text = "=== RÉSULTATS BÂCHE SEMI-ENTERRÉE (RPS 2011) ===\n\n"
            results_text += f"Norme : {seismic_code} (Zone {values['zone']})\n"
            results_text += f"Coeff. Sismiques : kh={kh:.3f}, kv={kv:.3f}\n"
            if n_poteaux_total > 0:
                results_text += f"Configuration : Voiles 0 à -{values.get('z_base', 3.0)}m | Poteaux 0 à +{values.get('z_dalle', 2.0)}m\n\n"
            else:
                results_text += "\n"
            
            results_text += "--- ENVELOPPE CAS DE CHARGES ---\n"
            results_text += f"Cas 1 (Vide) : M_A={abs(cas1_M_A):.1f}, M_D={abs(cas1_M_D):.1f} kNm\n"
            results_text += f"Cas 2 (Plein): M_A={abs(cas2_M_A):.1f}, M_D={abs(cas2_M_D):.1f} kNm\n"
            results_text += f"Cas 3 (Séisme): M_A={cas3_M_A:.1f}, M_D={cas3_M_D:.1f} kNm\n"
            results_text += f"→ Enveloppe : M_D = {M_D_env:.1f} kNm\n\n"
            
            results_text += "--- MONONOBE-OKABE ---\n"
            results_text += f"Coeff. Poussée Dyn (Kae) : {Kae:.3f}\n"
            results_text += f"Poussée Totale (Pae) : {Pae_dyn:.2f} kN/m\n\n"
            
            if housner_results:
                results_text += "--- HOUSNER ---\n"
                results_text += f"Pression Impulsive Pi : {housner_results['Pi']:.1f} kN\n"
                results_text += f"Pression Convective Pc : {housner_results['Pc']:.1f} kN\n\n"
            
            results_text += "--- SOLLICITATIONS (ELU Sismique) ---\n"
            results_text += f"Moment Coin Sup (M_A) : {M_A_tot:.1f} kNm\n"
            results_text += f"Moment Pied Voile (M_D): {M_D_tot:.1f} kNm\n"
            results_text += f"Effort Tranchant Voile : {V_Ed_wall:.1f} kN\n"
            results_text += f"Effort Normal Traverse : {N_top_tot:.1f} kN ({'Traction' if N_top_tot>0 else 'Compression'})\n\n"
            
            results_text += "--- STABILITÉ ---\n"
            results_text += f"Flottaison Fs = {flotation['Fs']:.2f} ({flotation['status']})\n"
            results_text += f"Glissement Fs = {sliding['Fs_glissement']:.2f} ({sliding['status']})\n"
            results_text += f"Portance σmax = {bearing['sigma_max']:.1f} kPa ({bearing['status']})\n\n"
            
            results_text += "--- FERRAILLAGE (ELU) ---\n"
            results_text += f"Voile As = {reinf_wall['As_required_cm2']:.2f} cm²/m ({reinf_wall['status']})\n"
            results_text += f"Radier As = {reinf_slab['As_required_cm2']:.2f} cm²/m ({reinf_slab['status']})\n"
            results_text += f"Voile Effort Tranchant : VEd={shear_wall['V_Ed']:.1f} kN, VRd,c={shear_wall['VRd_c']:.1f} kN ({shear_wall['status']})\n"
            if shear_wall['Asw_required'] > 0:
                results_text += f"  → Asw = {shear_wall['Asw_required']:.2f} cm² / 200mm\n"
            
            results_text += f"\n--- FISSURATION (ELS) ---\n"
            results_text += f"Ouverture fissure wk = {cracking['wk']:.3f} mm (limite: {cracking['wk_lim']} mm)\n"
            results_text += f"Statut : {cracking['status']}\n"
            
            # Vérifications RPS 2011 avancées
            results_text += f"\n--- ANALYSE SISMIQUE RPS 2011 ---\n"
            results_text += f"Effort Tranchant Base : V = {base_shear['V_design']:.1f} kN ({base_shear['status']})\n"
            results_text += f"  Formule : V = (A×D×I×S/K)×W = ({base_shear['A']}×{base_shear['D']}×{base_shear['I']}×{base_shear['S']}/{base_shear['K']})×{W_stab:.0f}\n"
            results_text += f"Renversement : Fs = {overturning['Fs_renversement']:.2f} ({overturning['status']})\n"
            results_text += f"Déplacement en tête : δ = {displacement['delta_max']:.2f} mm (limite: {displacement['delta_lim']:.2f} mm) ({displacement['status']})\n"
            
            results_text += f"\n--- VÉRIFICATIONS RADIER ---\n"
            results_text += f"Rigidité : L/e = {raft_rigidity['ratio_L_e']:.1f} → {raft_rigidity['classification']}\n"
            results_text += f"Poinçonnement : vEd/vRd = {punching['ratio']:.2f} ({punching['status']})\n"
            results_text += f"\n--- VÉRIFICATIONS VOILES ---\n"
            results_text += f"Flexion Composée : {combined['flexion_type']}\n"
            results_text += f"  N = {combined['N_Ed']:.1f} kN, M = {combined['M_Ed']:.1f} kNm, e = {combined['excentricite']:.0f} mm\n"
            results_text += f"  As requis = {combined['As_required_cm2']:.2f} cm²/m ({combined['status']})\n"
            results_text += f"Interface Voile-Radier : vEdi = {interface['v_Edi']:.3f} MPa ({interface['status']})\n"
            if interface['Asv_required_cm2'] > 0:
                results_text += f"  → Armatures couture Asv = {interface['Asv_required_cm2']:.2f} cm²/m\n"
            
            # Poteaux (si présents)
            if column_result:
                results_text += f"\n--- VÉRIFICATION POTEAUX ---\n"
                results_text += f"Nombre : {n_poteaux_total} ({n_poteaux_x}×{n_poteaux_z})\n"
                results_text += f"Section : {column_result['section']}\n"
                results_text += f"Hauteur : {values.get('z_dalle', 2.0):.2f} m (L₀={column_result['L_0']:.2f} m)\n"
                results_text += f"Charge par poteau N_Ed = {column_result['N_Ed']:.1f} kN\n"
                results_text += f"Élancement λ = {column_result['lambda']:.0f} (λ_lim = {column_result['lambda_lim']:.0f})\n"
                if column_result['needs_second_order']:
                    results_text += f"  → Effets 2nd ordre : e₂ = {column_result['e_2']:.0f} mm\n"
                results_text += f"As requis = {column_result['As_required_cm2']:.2f} cm² ({column_result['status']})\n"
            
            # Affichage
            self.results_frame.display_text(results_text)
            
            # Sauvegarder pour l'export PDF
            self.last_results = {
                **values,
                'mode': 'tank',
                'kh': kh, 'kv': kv, 'kae': Kae,
                'pae': Pae_dyn,
                'cas1_M_D': cas1_M_D, 'cas2_M_D': cas2_M_D, 'cas3_M_D': cas3_M_D,
                'M_D_env': M_D_env,
                'Fs_flotation': flotation['Fs'],
                'status_flotation': flotation['status'],
                'weight_total': flotation['weight'],
                'buoyancy': flotation['buoyancy'],
                'Fs_glissement': sliding['Fs_glissement'],
                'status_glissement': sliding['status'],
                'sigma_max': bearing['sigma_max'],
                'sigma_min': bearing['sigma_min'],
                'status_portance': bearing['status'],
                'As_wall': reinf_wall['As_required_cm2'],
                'As_slab': reinf_slab['As_required_cm2'],
                'V_Ed_wall': shear_wall['V_Ed'],
                'VRd_c': shear_wall['VRd_c'],
                'n_poteaux': n_poteaux_total,
                'column_result': column_result,
                'Asw_required': shear_wall['Asw_required'],
                'wk': cracking['wk'],
                # RPS 2011 Avancées
                'V_base': base_shear['V_design'],
                'V_base_formula': base_shear['formula'],
                'Fs_renversement': overturning['Fs_renversement'],
                'M_stab': overturning['M_stab'],
                'M_renverse': overturning['M_renverse'],
                'delta_max': displacement['delta_max'],
                'delta_lim': displacement['delta_lim'],
                'raft_classification': raft_rigidity['classification'],
                'raft_ratio': raft_rigidity['ratio_L_e'],
                'Pa_static': Pa_static,
                'delta_Pae': delta_Pae,
                'P_hydro_static': housner_results.get('P_hydro_static', 0) if housner_results else 0,
                'punching_ratio': punching['ratio'],
                'punching_status': punching['status'],
                'combined_As': combined['As_required_cm2'],
                'combined_type': combined['flexion_type'],
                'interface_vEdi': interface['v_Edi'],
                'interface_Asv': interface['Asv_required_cm2'],
                'interface_status': interface['status'],
                'wk_status': cracking['status'],
                'M_A': M_A_tot,
                'M_mid': res_vertical.M_top_mid,
                'M_D': M_D_tot,
                'N_top': N_top_tot,
                'N_bot': 0.0
            }
            if housner_results:
                self.last_results.update(housner_results)
            
            # Dessiner le schéma du cadre avec diagrammes
            self.results_frame.draw_frame_diagram(self.last_results)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.results_frame.display_error(str(e))

    def calculate(self):
        """Effectue le calcul selon le mode choisi"""
        if self.mode_var.get() == "Bâche à Eau / Cadre":
            self.calculate_tank()
            return

        """Effectue le calcul de la poussée dynamique (Mur)"""
        try:
            # Récupérer les valeurs
            values = self.input_frame.get_values()
            
            # Créer les objets
            # Pour le dessin et la géométrie physique
            wall = WallGeometry(
                height=values['height'],
                batter_angle=values['beta'],
                backfill_slope=values['backfill_slope']
            )
            # Pour le calcul (si h_backfill différent)
            # Si h_backfill n'est pas défini (vieux json), on utilise height
            h_calc = values.get('h_backfill', values['height'])
            wall_calc = WallGeometry(
                height=h_calc,
                batter_angle=values['beta'],
                backfill_slope=values['backfill_slope']
            )
            
            soil = SoilParameters(
                phi=values['phi'],
                delta=values['delta'],
                gamma=values['gamma']
            )
            
            # Calculer kh et kv selon la norme choisie
            seismic_code = values.get('seismic_code', 'EC8')
            
            if seismic_code == 'EC8':
                # Calcul selon EC8 France
                kh = EC8France.calculate_kh(
                    zone=values['zone'],
                    category=values['importance'],
                    soil_class=values['soil_class'],
                    r_factor=values['r_factor']
                )
                
                kv = 0.0
                if values['use_kv']:
                    kv = EC8France.calculate_kv(kh, values['zone'])
            
            else:  # RPS2011
                # Calcul selon RPS 2011 Maroc
                kh = RPS2011Maroc.calculate_kh(
                    zone=values['zone'],
                    classe=values['importance'],
                    site=values['soil_class'],
                    r_factor=values['r_factor']
                )
                
                kv = 0.0
                if values['use_kv']:
                    kv = RPS2011Maroc.calculate_kv(kh)
            
            seismic = SeismicParameters(kh=kh, kv=kv)
            
            # Calculer Kae et Pae
            kae = MononobeOkabe.calculate_kae(wall_calc, soil, seismic)
            pae = MononobeOkabe.calculate_pae(kae, wall_calc, soil, seismic)
            
            # Calcul Housner si eau présente
            Pi, Pc, Pw, mi, mc, Tc, hi, hc = 0, 0, 0, 0, 0, 0, 0, 0
            
            if values.get('has_water', False):
                # Créer paramètres eau
                water = WaterParameters(
                    hw=values['hw'],
                    L=values['L'],
                    gamma_w=values['gamma_w']
                )
                
                # Masses
                mi = Housner.calculate_impulsive_mass(water)
                mc = Housner.calculate_convective_mass(water)
                
                # Périodes
                Tc = Housner.calculate_convective_period(water)
                
                # Accélérations spectrales
                # Impulsive: mur rigide donc Ti ≈ 0, on prend Ai = kh × g
                Ai = kh * 9.81  # m/s²
                
                # Convective: utiliser le spectre de réponse
                if seismic_code == 'EC8':
                    Ac_g = EC8France.get_spectral_acceleration(
                        T=Tc,
                        zone=values['zone'],
                        category=values['importance'],
                        soil_class=values['soil_class']
                    )
                else:  # RPS2011
                    # Pour RPS2011, utiliser une approximation simplifiée
                    # ou implémenter le spectre RPS complet
                    # Ici on approxime avec une décroissance
                    if Tc > 1.0:
                        Ac_g = kh * 0.4  # Approximation pour longue période
                    else:
                        Ac_g = kh * 0.7
                
                Ac = Ac_g * 9.81  # Conversion en m/s²
                
                # Pressions
                Pi = Housner.calculate_impulsive_pressure(water, Ai)
                Pc = Housner.calculate_convective_pressure(water, Ac)
                
                # Combinaison
                method = values.get('combination_method', 'SRSS')
                Pw = Housner.calculate_total_pressure(Pi, Pc, method)
                
                # Hauteurs d'application
                hi = Housner.get_impulsive_height(water)
                hc = Housner.get_convective_height(water)
            
            # 5. Vérification Stabilité
            # Préparer les forces pour le module de stabilité
            forces = {
                'Pae_h': pae * math.cos(math.radians(values['delta'] + values['beta'])),
                'Pae_v': pae * math.sin(math.radians(values['delta'] + values['beta'])),
                'Pw': Pw,
                'height': values['height'],
                'hw': values.get('hw', 0.0)
            }
            
            seismic_params = {'kh': kh, 'kv': kv}
            
            verifier = StabilityVerifier(values, forces, seismic_params)
            sliding = verifier.check_sliding()
            overturning = verifier.check_overturning()
            bearing = verifier.check_bearing()
            
            # Préparer les résultats complets
            results = {
                **values,
                'kh': kh,
                'kv': kv,
                'theta': math.degrees(seismic.theta),
                'kae': kae,
                'pae': pae,
                # Housner
                'has_water': values.get('has_water', False),
                'Pi': Pi,
                'Pc': Pc,
                'Pw': Pw,
                'mi': mi,
                'mc': mc,
                'Tc': Tc,
                'hi': hi,
                'hc': hc,
                'Ptotal': pae + Pw,
                # Stabilité
                'Fs_sliding': sliding['Fs'],
                'Fr_overturning': overturning['Fr'],
                'sigma_ref': bearing['sigma_ref'],
                'sigma_max': bearing['sigma_max'],
                'eccentricity': bearing['e'],
                'B_eff': bearing['B_eff']
            }
            
            # Sauvegarder pour l'export PDF
            self.last_results = results
            
            # Afficher les résultats
            self.results_frame.display_results(results)
            
            # Sauvegarder pour export
            self.last_results = results
            
        except Exception as e:
            # Afficher l'erreur
            error_window = ctk.CTkToplevel(self)
            error_window.title("Erreur")
            error_window.geometry("400x150")
            
            error_label = ctk.CTkLabel(error_window, 
                                      text=f"❌ Erreur lors du calcul:\n{str(e)}",
                                      font=ctk.CTkFont(size=14))
            error_label.pack(pady=30, padx=20)
            
            ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
            ok_button.pack(pady=10)
    
    def export_pdf(self):
        """Exporte les résultats en PDF"""
        if not hasattr(self, 'last_results'):
            # Aucun calcul effectué
            return
        
        # TODO: Implémenter l'export PDF avec reportlab
        info_window = ctk.CTkToplevel(self)
        info_window.title("Export PDF")
        info_window.geometry("300x100")
        
        info_label = ctk.CTkLabel(info_window, text="🚧 Fonctionnalité en cours de développement")
        info_label.pack(pady=30)
    
    def on_closing(self):
        """Gestion propre de la fermeture de l'application"""
        self.quit()
        self.destroy()
        sys.exit(0)

    def reset(self):
        """Réinitialise l'application"""
        self.destroy()
        app = MononobeApp()
        app.mainloop()
    
    def open_analysis(self):
        """Ouvre la fenêtre d'analyse paramétrique"""
        if not hasattr(self, 'last_results'):
            # Si pas de calcul fait, essayer de récupérer les valeurs actuelles
            try:
                current_inputs = self.input_frame.get_values()
            except:
                # Valeurs par défaut si échec
                current_inputs = {
                    'height': 5.0, 'beta': 0.0, 'backfill_slope': 0.0,
                    'phi': 30.0, 'delta': 20.0, 'gamma': 18.0,
                    'seismic_code': 'EC8', 'zone': '3', 'importance': 'II',
                    'soil_class': 'C', 'r_factor': 2.0,
                    'has_water': False
                }
        else:
            current_inputs = self.last_results
            
        from gui.analysis_window import AnalysisWindow
        AnalysisWindow(self, current_inputs)

    def export_pdf(self):
        """Exporte les résultats en PDF"""
        if not hasattr(self, 'last_results'):
            # Aucun calcul effectué
            error_window = ctk.CTkToplevel(self)
            error_window.title("Erreur")
            error_window.geometry("400x120")
            
            error_label = ctk.CTkLabel(error_window, 
                                      text="⚠️ Aucun calcul à exporter\nVeuillez d'abord effectuer un calcul",
                                      font=ctk.CTkFont(size=14))
            error_label.pack(pady=30, padx=20)
            
            ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
            ok_button.pack(pady=10)
            return
        
        try:
            # Demander le nom de fichier
            from tkinter import filedialog
            from datetime import datetime
            import os
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Note_Calcul_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if not filename:
                return
            
            # Générer le PDF
            from utils.report_generator import PDFReportGenerator
            
            generator = PDFReportGenerator(filename)
            
            # Page de garde
            code_display = "EC8 France 🇫🇷" if self.last_results.get('seismic_code') == 'EC8' else "RPS 2011 Maroc 🇲🇦"
            project_info = {
                'title': 'NOTE DE CALCUL',
                'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'code': code_display
            }
            generator.add_cover_page(project_info)
            
            # Données d'entrée
            generator.add_input_section(self.last_results)
            
            # Résultats
            generator.add_results_section(self.last_results)
            
            # Stabilité
            generator.add_stability_section(self.last_results)
            
            # Schéma du cadre (Tank mode only)
            generator.add_frame_diagram(self.last_results)
            
            # Références
            generator.add_references()
            
            # Génération
            pdf_path = generator.generate()
            
            # Message de succès
            success_window = ctk.CTkToplevel(self)
            success_window.title("Export réussi")
            success_window.geometry("500x180")
            
            label = ctk.CTkLabel(success_window, 
                                text=f"✅ PDF généré avec succès !\n\n{os.path.basename(pdf_path)}",
                                font=ctk.CTkFont(size=14))
            label.pack(pady=20, padx=20)
            
            # Bouton Ouvrir
            open_btn = ctk.CTkButton(success_window, text="📄 Ouvrir le PDF",
                                    command=lambda: os.startfile(pdf_path),
                                    width=200, height=40,
                                    font=ctk.CTkFont(size=14, weight="bold"))
            open_btn.pack(pady=10)
            
            # Bouton Fermer
            close_btn = ctk.CTkButton(success_window, text="Fermer",
                                     command=success_window.destroy,
                                     width=200, height=40)
            close_btn.pack(pady=5)
            
        except Exception as e:
            # Erreur lors de l'export
            error_window = ctk.CTkToplevel(self)
            error_window.title("Erreur")
            error_window.geometry("450x150")
            
            error_label = ctk.CTkLabel(error_window, 
                                      text=f"❌ Erreur lors de l'export PDF:\n{str(e)}",
                                      font=ctk.CTkFont(size=13))
            error_label.pack(pady=30, padx=20)
            
            ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
            ok_button.pack(pady=10)

    def on_closing(self):
        """Gestion propre de la fermeture de l'application"""
        try:
            # Annuler tous les after callbacks en attente
            for after_id in self.tk.call('after', 'info'):
                try:
                    self.after_cancel(after_id)
                except:
                    pass
        except:
            pass
        
        try:
            self.quit()
        except:
            pass
        
        try:
            self.destroy()
        except:
            pass
        
        # Force exit pour éviter les erreurs résiduelles
        import sys
        sys.exit(0)

def main():
    app = MononobeApp()
    app.mainloop()

if __name__ == "__main__":
    main()
