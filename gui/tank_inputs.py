import customtkinter as ctk

class TankInputFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.inputs = {}
        self._create_widgets()

    def _create_widgets(self):
        # Titre
        title = ctk.CTkLabel(self, text="Paramètres de la Bâche / Cadre", 
                           font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")
        
        row = 1
        
        # --- Géométrie ---
        self.add_section_header(row, "GÉOMÉTRIE (Dimensions intérieures)")
        row += 1
        
        self.add_input(row, "Largeur Lx (m)", "tank_width", "4.0")
        row += 1
        self.add_input(row, "Hauteur H enterrée (m)", "tank_height", "3.0")
        row += 1
        self.add_input(row, "Profondeur Lz (m)", "tank_length", "5.0")
        row += 1
        
        # --- Niveaux Semi-Enterré ---
        self.add_section_header(row, "NIVEAUX (Semi-Enterré)")
        row += 1
        
        self.add_input(row, "Profondeur base / TN (m)", "z_base", "3.0")
        row += 1
        self.add_input(row, "Hauteur dalle / TN (m)", "z_dalle", "2.0")
        row += 1
        
        # Note explicative
        note = ctk.CTkLabel(self, text="→ Voiles: 0 à z_base | Poteaux: TN à z_dalle", 
                           font=ctk.CTkFont(size=11, slant="italic"),
                           text_color="gray")
        note.grid(row=row, column=0, columnspan=2, padx=10, pady=2, sticky="w")
        row += 1
        
        # --- Poteaux ---
        self.add_section_header(row, "POTEAUX (entre TN et dalle)")
        row += 1
        
        self.add_input(row, "Nombre de poteaux Lx", "n_poteaux_x", "0")
        row += 1
        self.add_input(row, "Nombre de poteaux Lz", "n_poteaux_z", "0")
        row += 1
        self.add_input(row, "Section poteau a (m)", "dim_poteau_a", "0.30")
        row += 1
        self.add_input(row, "Section poteau b (m)", "dim_poteau_b", "0.30")
        row += 1
        
        # --- Épaisseurs ---
        self.add_section_header(row, "ÉPAISSEURS (Béton Armé)")
        row += 1
        
        self.add_input(row, "Dalle Supérieure (m)", "th_top", "0.20")
        row += 1
        self.add_input(row, "Radier (m)", "th_bot", "0.30")
        row += 1
        self.add_input(row, "Voiles (m)", "th_wall", "0.25")
        row += 1
        
        # --- Environnement ---
        self.add_section_header(row, "ENVIRONNEMENT")
        row += 1
        
        self.add_input(row, "Hauteur remblai sur dalle (m)", "soil_cover", "0.50")
        row += 1
        self.add_input(row, "Charge exploitation dalle Q (kN/m²)", "Q_dalle", "2.5")
        row += 1
        self.add_input(row, "Niveau Nappe (depuis bas radier) (m)", "water_level_out", "1.0")
        row += 1
        self.add_input(row, "Niveau Eau Intérieur (m)", "water_level_in", "2.5")
        row += 1
        
        # --- Sol ---
        self.add_section_header(row, "PARAMÈTRES DU SOL")
        row += 1
        
        self.add_input(row, "Angle de frottement φ (°)", "phi", "30.0")
        row += 1
        self.add_input(row, "Angle frottement sol-mur δ (°)", "delta", "20.0")
        row += 1
        self.add_input(row, "Poids volumique sol γ (kN/m3)", "gamma_soil", "18.0")
        row += 1

        # --- Séisme ---
        self.add_section_header(row, "SÉISME")
        row += 1
        
        # Choix de la norme
        label = ctk.CTkLabel(self, text="Norme Sismique", anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        self.seismic_code_var = ctk.StringVar(value="EC8")
        code_combo = ctk.CTkComboBox(self, values=["EC8", "RPS2011"], 
                                    variable=self.seismic_code_var, 
                                    command=self.update_seismic_options,
                                    width=100)
        code_combo.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        self.inputs['seismic_code'] = code_combo
        row += 1
        
        # Zone Sismique
        self.zone_label = ctk.CTkLabel(self, text="Zone Sismique", anchor="w")
        self.zone_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.zone_combo = ctk.CTkComboBox(self, values=["1", "2", "3", "4", "5"], width=100)
        self.zone_combo.set("3")
        self.zone_combo.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        self.inputs['zone'] = self.zone_combo
        row += 1
        
        # Classe de Sol
        self.soil_label = ctk.CTkLabel(self, text="Classe de Sol", anchor="w")
        self.soil_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.soil_combo = ctk.CTkComboBox(self, values=["A", "B", "C", "D", "E"], width=100)
        self.soil_combo.set("C")
        self.soil_combo.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        self.inputs['soil_class'] = self.soil_combo
        row += 1
        
        # Importance
        self.imp_label = ctk.CTkLabel(self, text="Catégorie Importance", anchor="w")
        self.imp_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        self.imp_combo = ctk.CTkComboBox(self, values=["I", "II", "III", "IV"], width=100)
        self.imp_combo.set("II")
        self.imp_combo.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        self.inputs['importance'] = self.imp_combo
        row += 1
        
        # Coefficient de comportement
        self.add_input(row, "Coefficient de comportement q (ou R)", "r_factor", "1.5")
        row += 1
        
        # --- Matériaux ---
        self.add_section_header(row, "MATÉRIAUX")
        row += 1
        
        self.add_input(row, "Résistance Béton fc28 (MPa)", "fc28", "25.0")
        row += 1
        self.add_input(row, "Poids vol. Béton (kN/m3)", "gamma_concrete", "25.0")
        row += 1
        self.add_input(row, "Limite élastique Acier fyk (MPa)", "fyk", "500.0")
        row += 1
        self.add_input(row, "Enrobage (m)", "enrobage", "0.04")
        row += 1
        
        # --- Paramètres Sol Portance ---
        self.add_section_header(row, "PORTANCE DU SOL")
        row += 1
        
        self.add_input(row, "Contrainte admissible σ_adm (kPa)", "sigma_adm", "200.0")
        row += 1
        self.add_input(row, "Coefficient frottement sol/radier", "friction_coef", "0.5")
        row += 1

    def update_seismic_options(self, choice):
        """Met à jour les options selon la norme choisie"""
        if choice == "EC8":
            self.zone_combo.configure(values=["1", "2", "3", "4", "5"])
            self.soil_combo.configure(values=["A", "B", "C", "D", "E"])
            self.imp_combo.configure(values=["I", "II", "III", "IV"])
            self.imp_label.configure(text="Catégorie Importance")
            
            # Valeurs par défaut si invalides
            if self.zone_combo.get() not in ["1", "2", "3", "4", "5"]: self.zone_combo.set("3")
            if self.soil_combo.get() not in ["A", "B", "C", "D", "E"]: self.soil_combo.set("C")
            if self.imp_combo.get() not in ["I", "II", "III", "IV"]: self.imp_combo.set("II")
            
        else: # RPS2011
            self.zone_combo.configure(values=["0", "1", "2", "3", "4", "5"])
            self.soil_combo.configure(values=["S1", "S2", "S3", "S4", "S5"])
            self.imp_combo.configure(values=["I", "II", "III"])
            self.imp_label.configure(text="Classe Importance")
            
            # Valeurs par défaut si invalides
            if self.zone_combo.get() not in ["0", "1", "2", "3", "4", "5"]: self.zone_combo.set("3")
            if self.soil_combo.get() not in ["S1", "S2", "S3", "S4", "S5"]: self.soil_combo.set("S2")
            if self.imp_combo.get() not in ["I", "II", "III"]: self.imp_combo.set("II")

    def add_section_header(self, row, text):
        label = ctk.CTkLabel(self, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                           text_color="gray70")
        label.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="w", padx=5)

    def add_input(self, row, label_text, key, default_value, min_val=None, max_val=None):
        label = ctk.CTkLabel(self, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        entry = ctk.CTkEntry(self, width=100)
        entry.insert(0, default_value)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        
        # Stocker les limites pour validation
        entry._min_val = min_val
        entry._max_val = max_val
        entry._original_fg = entry.cget("fg_color")
        
        # Bind validation on focus out
        entry.bind("<FocusOut>", lambda e, ent=entry: self._validate_entry(ent))
        
        self.inputs[key] = entry
        
    def _validate_entry(self, entry):
        """Valide une entrée et change sa couleur si invalide"""
        try:
            val = float(entry.get())
            is_valid = True
            
            if entry._min_val is not None and val < entry._min_val:
                is_valid = False
            if entry._max_val is not None and val > entry._max_val:
                is_valid = False
            
            if is_valid:
                entry.configure(fg_color=entry._original_fg)
            else:
                entry.configure(fg_color="#ffcccc")  # Rouge clair
                
        except ValueError:
            entry.configure(fg_color="#ffcccc")
    
    def validate_inputs(self) -> tuple[bool, list]:
        """
        Valide la cohérence des entrées.
        Retourne (is_valid, list_of_errors)
        """
        errors = []
        values = self.get_values()
        
        # Contrôles de cohérence
        if values.get('water_level_in', 0) > values.get('tank_height', 0):
            errors.append("Niveau eau intérieur > Hauteur bâche")
            
        if values.get('th_wall', 0) <= 0 or values.get('th_top', 0) <= 0 or values.get('th_bot', 0) <= 0:
            errors.append("Épaisseurs doivent être > 0")
            
        if values.get('phi', 0) <= 0 or values.get('phi', 0) > 45:
            errors.append("Angle φ doit être entre 0° et 45°")
            
        if values.get('delta', 0) > values.get('phi', 0):
            errors.append("Angle δ doit être ≤ φ")
            
        if values.get('enrobage', 0) >= values.get('th_wall', 0) / 2:
            errors.append("Enrobage trop grand par rapport à l'épaisseur")
            
        if values.get('fc28', 0) < 15 or values.get('fc28', 0) > 60:
            errors.append("fc28 doit être entre 15 et 60 MPa")
        
        # Highlight des champs problématiques
        self._highlight_errors(errors, values)
        
        return len(errors) == 0, errors
    
    def _highlight_errors(self, errors, values):
        """Met en évidence les champs avec erreurs"""
        # Reset all
        for key, widget in self.inputs.items():
            if isinstance(widget, ctk.CTkEntry) and hasattr(widget, '_original_fg'):
                widget.configure(fg_color=widget._original_fg)
        
        # Highlight specific errors
        if "Niveau eau intérieur > Hauteur bâche" in errors:
            if 'water_level_in' in self.inputs:
                self.inputs['water_level_in'].configure(fg_color="#ffcccc")
                
        if "Angle δ doit être ≤ φ" in errors:
            if 'delta' in self.inputs:
                self.inputs['delta'].configure(fg_color="#ffcccc")
        
    def get_values(self):
        values = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, ctk.CTkEntry):
                try:
                    values[key] = float(widget.get())
                except ValueError:
                    values[key] = 0.0
            elif isinstance(widget, ctk.CTkComboBox):
                values[key] = widget.get()
            elif isinstance(widget, ctk.CTkCheckBox):
                values[key] = bool(widget.get())
                
        return values

    def set_values(self, values):
        for key, value in values.items():
            if key in self.inputs:
                self.inputs[key].delete(0, "end")
                self.inputs[key].insert(0, str(value))
