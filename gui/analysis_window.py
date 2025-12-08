"""
Fenêtre d'analyse paramétrique
"""
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from core.analysis import ParametricAnalyzer

class AnalysisWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_inputs):
        super().__init__(parent)
        
        self.title("Analyse Paramétrique")
        self.geometry("1000x700")
        
        self.current_inputs = current_inputs
        self.analyzer = ParametricAnalyzer(current_inputs)
        
        # Configuration de la grille
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # === PANNEAU DE GAUCHE (Contrôles) ===
        self.control_frame = ctk.CTkFrame(self, width=300)
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Titre
        ctk.CTkLabel(self.control_frame, text="Paramètres de l'Analyse", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        # Choix du paramètre variable
        ctk.CTkLabel(self.control_frame, text="Paramètre à faire varier :").pack(pady=(10, 5), padx=10, anchor="w")
        
        self.param_var = ctk.StringVar(value="Hauteur du mur H")
        self.param_map = {
            "Hauteur du mur H": "height",
            "Hauteur d'eau hw": "hw",
            "Angle de frottement φ": "phi",
            "Coeff. sismique kh": "kh"
        }
        
        self.param_combo = ctk.CTkComboBox(self.control_frame, 
                                          values=list(self.param_map.keys()),
                                          variable=self.param_var,
                                          command=self.update_range_defaults)
        self.param_combo.pack(pady=5, padx=10, fill="x")
        
        # Plage de variation
        ctk.CTkLabel(self.control_frame, text="Plage de variation :").pack(pady=(20, 5), padx=10, anchor="w")
        
        range_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        range_frame.pack(pady=5, padx=10, fill="x")
        
        # Min
        ctk.CTkLabel(range_frame, text="Min:").grid(row=0, column=0, padx=5)
        self.min_entry = ctk.CTkEntry(range_frame, width=70)
        self.min_entry.grid(row=0, column=1, padx=5)
        
        # Max
        ctk.CTkLabel(range_frame, text="Max:").grid(row=1, column=0, padx=5, pady=10)
        self.max_entry = ctk.CTkEntry(range_frame, width=70)
        self.max_entry.grid(row=1, column=1, padx=5, pady=10)
        
        # Pas (nombre de points)
        ctk.CTkLabel(self.control_frame, text="Nombre de points :").pack(pady=(10, 5), padx=10, anchor="w")
        self.steps_slider = ctk.CTkSlider(self.control_frame, from_=10, to=100, number_of_steps=90)
        self.steps_slider.pack(pady=5, padx=10, fill="x")
        self.steps_slider.set(20)
        
        self.steps_label = ctk.CTkLabel(self.control_frame, text="20 points")
        self.steps_label.pack(pady=0)
        self.steps_slider.configure(command=lambda v: self.steps_label.configure(text=f"{int(v)} points"))
        
        # Bouton Lancer
        self.run_btn = ctk.CTkButton(self.control_frame, text="🚀 LANCER L'ANALYSE", 
                                    command=self.run_analysis,
                                    height=40,
                                    font=ctk.CTkFont(weight="bold"))
        self.run_btn.pack(pady=30, padx=10, fill="x")
        
        # Résultats numériques (résumé)
        self.stats_text = ctk.CTkTextbox(self.control_frame, height=150)
        self.stats_text.pack(pady=10, padx=10, fill="x")
        self.stats_text.configure(state="disabled")
        
        # === PANNEAU DE DROITE (Graphique) ===
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Initialiser le graphique
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Résultats de l'analyse")
        self.ax.set_xlabel("Paramètre")
        self.ax.set_ylabel("Poussée (kN/m)")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialiser les valeurs par défaut
        self.update_range_defaults("Hauteur du mur H")
        
    def update_range_defaults(self, choice):
        """Met à jour les valeurs min/max par défaut selon le paramètre choisi"""
        param = self.param_map[choice]
        current_val = self.current_inputs.get(param, 0.0)
        
        if param == 'height':
            self.min_entry.delete(0, "end"); self.min_entry.insert(0, "2.0")
            self.max_entry.delete(0, "end"); self.max_entry.insert(0, "15.0")
        elif param == 'hw':
            self.min_entry.delete(0, "end"); self.min_entry.insert(0, "0.0")
            self.max_entry.delete(0, "end"); self.max_entry.insert(0, str(self.current_inputs.get('height', 10.0)))
        elif param == 'phi':
            self.min_entry.delete(0, "end"); self.min_entry.insert(0, "20.0")
            self.max_entry.delete(0, "end"); self.max_entry.insert(0, "45.0")
        elif param == 'kh':
            self.min_entry.delete(0, "end"); self.min_entry.insert(0, "0.05")
            self.max_entry.delete(0, "end"); self.max_entry.insert(0, "0.40")
            
    def run_analysis(self):
        """Lance le calcul et met à jour le graphique"""
        try:
            # Récupérer paramètres
            param_key = self.param_map[self.param_combo.get()]
            min_val = float(self.min_entry.get())
            max_val = float(self.max_entry.get())
            steps = int(self.steps_slider.get())
            
            # Exécuter l'analyse
            results = self.analyzer.run_analysis(param_key, min_val, max_val, steps)
            
            # Mettre à jour le graphique
            self.ax.clear()
            
            # Tracer Pae
            self.ax.plot(results['x_values'], results['pae'], label='Pae (Terres)', 
                        color='#8B4513', linewidth=2)
            
            # Tracer Pw (si eau présente)
            if any(v > 0 for v in results['pw']):
                self.ax.plot(results['x_values'], results['pw'], label='Pw (Eau)', 
                            color='#1E90FF', linewidth=2, linestyle='--')
                
                # Tracer Total
                self.ax.plot(results['x_values'], results['ptotal'], label='Ptotal', 
                            color='#DC143C', linewidth=3)
            
            # Configuration axes
            self.ax.set_title(f"Influence de : {self.param_combo.get()}")
            self.ax.set_xlabel(f"{self.param_combo.get()}")
            self.ax.set_ylabel("Poussée (kN/m)")
            self.ax.legend()
            self.ax.grid(True, linestyle='--', alpha=0.7)
            
            self.canvas.draw()
            
            # Mettre à jour stats
            stats = f"Analyse terminée ({steps} points)\n\n"
            stats += f"Variation {param_key}: {min_val} -> {max_val}\n"
            stats += f"Pae max: {max(results['pae']):.2f} kN/m\n"
            if any(v > 0 for v in results['pw']):
                stats += f"Pw max: {max(results['pw']):.2f} kN/m\n"
                stats += f"Ptotal max: {max(results['ptotal']):.2f} kN/m"
            
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats)
            self.stats_text.configure(state="disabled")
            
        except ValueError:
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", "❌ Erreur: Vérifiez les valeurs numériques")
            self.stats_text.configure(state="disabled")
