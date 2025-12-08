import customtkinter as ctk

class InputFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        
        # Variables pour stocker les valeurs
        self.inputs = {}
        self.current_code = "EC8"  # Code par défaut
        
        # Stockage des widgets dynamiques
        self.seismic_widgets = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Titre
        title = ctk.CTkLabel(self, text="Données d'entrée", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        row = 1
        
        # Sélecteur de norme (NOUVEAU)
        code_label = ctk.CTkLabel(self, text="🌍 Norme Sismique", font=ctk.CTkFont(size=16, weight="bold"))
        code_label.grid(row=row, column=0, columnspan=2, pady=(5, 5), sticky="w")
        row += 1
        
        code_selector = ctk.CTkSegmentedButton(
            self,
            values=["EC8 France", "RPS 2011 Maroc"],
            command=self.on_code_change
        )
        code_selector.set("EC8 France")
        code_selector.grid(row=row, column=0, columnspan=2, pady=5, sticky="ew", padx=10)
        self.inputs["code_selector"] = code_selector
        row += 1
        
        # Section Géométrie du Mur
        geo_label = ctk.CTkLabel(self, text="Géométrie du Mur", font=ctk.CTkFont(size=16, weight="bold"))
        geo_label.grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky="w")
        row += 1
        
        self.add_input(row, "Hauteur du mur H (m)", "height", "5.0")
        row += 1
        self.add_input(row, "Hauteur remblai H_sol (m)", "h_backfill", "5.0")
        row += 1
        self.add_input(row, "Inclinaison parement β (deg)", "beta", "0.0")
        row += 1
        self.add_input(row, "Pente du remblai i (deg)", "backfill_slope", "0.0")
        row += 1
        
        # Section Caractéristiques Mur (Stabilité)
        stab_label = ctk.CTkLabel(self, text="Caractéristiques Mur (Stabilité)", font=ctk.CTkFont(size=16, weight="bold"))
        stab_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w")
        row += 1
        
        self.add_input(row, "Largeur semelle B (m)", "width_B", "3.0")
        row += 1
        self.add_input(row, "Poids du mur W (kN/m)", "weight_W", "100.0")
        row += 1
        self.add_input(row, "Frottement base δ_b (deg)", "friction_base", "30.0")
        row += 1
        self.add_input(row, "Cohésion base c (kPa)", "cohesion_base", "0.0")
        row += 1
        
        # Section Sol
        soil_label = ctk.CTkLabel(self, text="Paramètres du Sol (Remblai)", font=ctk.CTkFont(size=16, weight="bold"))
        soil_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w")
        row += 1
        
        self.add_input(row, "Angle de frottement φ (deg)", "phi", "30.0")
        row += 1
        self.add_input(row, "Angle de frottement sol-mur δ (deg)", "delta", "20.0")
        row += 1
        self.add_input(row, "Poids volumique γ (kN/m³)", "gamma", "18.0")
        row += 1
        
        # Section Eau (Housner)
        water_label = ctk.CTkLabel(self, text="💧 Présence d'Eau (Housner)", font=ctk.CTkFont(size=16, weight="bold"))
        water_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w")
        row += 1
        
        # Checkbox pour activer l'eau
        self.inputs["has_water"] = ctk.BooleanVar(value=False)
        water_checkbox = ctk.CTkCheckBox(self, text="Inclure effets hydrodynamiques", 
                                        variable=self.inputs["has_water"],
                                        command=self.on_water_change)
        water_checkbox.grid(row=row, column=0, columnspan=2, pady=5, sticky="w")
        row += 1
        
        # Champs eau (initialement masqués)
        self.water_row_start = row
        self.water_widgets = []
        self.create_water_fields(row)
        row += 4  # Incrémenter pour les 4 champs eau (hw, L, gamma_w, method)
        
        # Masquer par défaut
        for widget in self.water_widgets:
            widget.grid_remove()
        
        # Section Séisme (dynamique selon la norme)
        self.seismic_row_start = row
        self.seismic_label = ctk.CTkLabel(self, text="Paramètres Sismiques EC8 France", font=ctk.CTkFont(size=16, weight="bold"))
        self.seismic_label.grid(row=row, column=0, columnspan=2, pady=(20, 5), sticky="w")
        row += 1
        
        # Création des champs EC8 par défaut
        self.create_ec8_fields(row)
    
    def on_code_change(self, value):
        """Appelé quand l'utilisateur change de norme"""
        # Nettoyer les widgets sismiques existants
        for widget in self.seismic_widgets:
            widget.destroy()
        self.seismic_widgets.clear()
        
        # Supprimer les anciennes entrées sismiques
        keys_to_remove = ["zone", "importance", "soil_class", "r_factor", "use_kv"]
        for key in keys_to_remove:
            if key in self.inputs:
                del self.inputs[key]
        
        # Mettre à jour le titre de section
        if value == "EC8 France":
            self.current_code = "EC8"
            self.seismic_label.configure(text="Paramètres Sismiques EC8 France")
            self.create_ec8_fields(self.seismic_row_start + 1)
        else:  # RPS 2011 Maroc
            self.current_code = "RPS2011"
            self.seismic_label.configure(text="Paramètres Sismiques RPS 2011 🇲🇦")
            self.create_rps_fields(self.seismic_row_start + 1)
    
    def create_ec8_fields(self, start_row):
        """Crée les champs spécifiques EC8 France"""
        row = start_row
        
        # Zone sismique
        label, widget = self.add_dropdown_with_ref(row, "Zone sismique", "zone", ["1", "2", "3", "4", "5"], "3")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Catégorie d'importance
        label, widget = self.add_dropdown_with_ref(row, "Catégorie d'importance", "importance", ["I", "II", "III", "IV"], "II")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Classe de sol
        label, widget = self.add_dropdown_with_ref(row, "Classe de sol", "soil_class", ["A", "B", "C", "D", "E"], "C")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Coefficient r
        label, widget = self.add_input_with_ref(row, "Coefficient de comportement r", "r_factor", "2.0")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Checkbox pour kv
        self.inputs["use_kv"] = ctk.BooleanVar(value=False)
        kv_checkbox = ctk.CTkCheckBox(self, text="Inclure coefficient vertical kv", variable=self.inputs["use_kv"])
        kv_checkbox.grid(row=row, column=0, columnspan=2, pady=5, sticky="w")
        self.seismic_widgets.append(kv_checkbox)
    
    def create_rps_fields(self, start_row):
        """Crée les champs spécifiques RPS 2011 Maroc"""
        row = start_row
        
        # Zone sismique
        label, widget = self.add_dropdown_with_ref(row, "Zone sismique", "zone", ["0", "1", "2", "3", "4", "5"], "3")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Classe d'importance
        label, widget = self.add_dropdown_with_ref(row, "Classe d'importance", "importance", ["I", "II", "III"], "II")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Site (classe de sol)
        label, widget = self.add_dropdown_with_ref(row, "Classe de site", "soil_class", ["S1", "S2", "S3", "S4", "S5"], "S3")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Coefficient R
        label, widget = self.add_input_with_ref(row, "Coefficient de comportement R", "r_factor", "2.0")
        self.seismic_widgets.extend([label, widget])
        row += 1
        
        # Checkbox pour kv (toujours inclus dans RPS avec facteur 0.3)
        self.inputs["use_kv"] = ctk.BooleanVar(value=True)
        kv_checkbox = ctk.CTkCheckBox(self, text="Inclure coefficient vertical kv (RPS: kv=0.3×kh)", 
                                     variable=self.inputs["use_kv"], state="normal")
        kv_checkbox.grid(row=row, column=0, columnspan=2, pady=5, sticky="w")
        self.seismic_widgets.append(kv_checkbox)
    
    def create_water_fields(self, start_row):
        """Crée les champs pour les paramètres d'eau (Housner)"""
        row = start_row
        
        # Hauteur d'eau
        label, widget = self.add_input_with_ref(row, "Hauteur d'eau hw (m)", "hw", "5.0")
        self.water_widgets.extend([label, widget])
        row += 1
        
        # Largeur réservoir
        label, widget = self.add_input_with_ref(row, "Largeur réservoir L (m)", "L", "10.0")
        self.water_widgets.extend([label, widget])
        row += 1
        
        # Masse volumique eau
        label, widget = self.add_input_with_ref(row, "Masse volumique γw (kN/m³)", "gamma_w", "10.0")
        self.water_widgets.extend([label, widget])
        row += 1
        
        # Méthode de combinaison
        label = ctk.CTkLabel(self, text="Méthode de combinaison", anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        dropdown = ctk.CTkComboBox(self, values=["SRSS", "Sommation"], width=150, state="readonly")
        dropdown.set("SRSS")
        dropdown.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        self.inputs["combination_method"] = dropdown
        self.water_widgets.extend([label, dropdown])
    
    def on_water_change(self):
        """Appelé quand l'utilisateur active/désactive l'eau"""
        if self.inputs["has_water"].get():
            # Afficher les champs eau
            for widget in self.water_widgets:
                widget.grid()
        else:
            # Masquer les champs eau
            for widget in self.water_widgets:
                widget.grid_remove()
    
    def add_input(self, row, label_text, key, default_value):
        label = ctk.CTkLabel(self, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        entry = ctk.CTkEntry(self, width=150)
        entry.insert(0, default_value)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        
        self.inputs[key] = entry
    
    def add_input_with_ref(self, row, label_text, key, default_value):
        """Version qui retourne les références pour destruction dynamique"""
        label = ctk.CTkLabel(self, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        entry = ctk.CTkEntry(self, width=150)
        entry.insert(0, default_value)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        
        self.inputs[key] = entry
        return label, entry
    
    def add_dropdown(self, row, label_text, key, values, default_value):
        label = ctk.CTkLabel(self, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        dropdown = ctk.CTkComboBox(self, values=values, width=150, state="readonly")
        dropdown.set(default_value)
        dropdown.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        
        self.inputs[key] = dropdown
    
    def add_dropdown_with_ref(self, row, label_text, key, values, default_value):
        """Version qui retourne les références pour destruction dynamique"""
        label = ctk.CTkLabel(self, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        dropdown = ctk.CTkComboBox(self, values=values, width=150, state="readonly")
        dropdown.set(default_value)
        dropdown.grid(row=row, column=1, padx=10, pady=5, sticky="e")
        
        self.inputs[key] = dropdown
        return label, dropdown
    
    def get_values(self):
        """Récupère toutes les valeurs des inputs"""
        values = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, ctk.CTkEntry):
                try:
                    values[key] = float(widget.get())
                except ValueError:
                    values[key] = 0.0
            elif isinstance(widget, ctk.CTkComboBox):
                values[key] = widget.get()
            elif isinstance(widget, ctk.BooleanVar):
                values[key] = widget.get()
            elif isinstance(widget, ctk.CTkSegmentedButton):
                values[key] = widget.get()
        
        # Ajouter le code actuel
        values['seismic_code'] = self.current_code
        
        return values

    def set_values(self, values):
        """Remplit les champs avec les valeurs fournies"""
        # 1. Gérer le code sismique d'abord (car il change les widgets)
        if 'seismic_code' in values:
            code = values['seismic_code']
            self.code_combo.set(code)
            self.on_code_change(code)
            self.current_code = code
            
        # 2. Gérer l'eau (car elle change les widgets)
        if 'has_water' in values:
            has_water = values['has_water']
            # Convertir bool en int pour BooleanVar si nécessaire, ou juste set
            self.inputs['has_water'].set(has_water)
            self.on_water_change()
            
        # 3. Remplir les autres champs
        for key, value in values.items():
            if key in self.inputs:
                widget = self.inputs[key]
                
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, str(value))
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set(str(value))
                elif isinstance(widget, ctk.BooleanVar):
                    widget.set(value)
                elif isinstance(widget, ctk.CTkCheckBox):
                    if value:
                        widget.select()
                    else:
                        widget.deselect()

