"""
Générateur de rapports PDF pour notes de calcul
Utilise ReportLab pour créer des PDF professionnels
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
import tempfile

# Import matplotlib avec gestion du backend
import matplotlib
# Sauvegarder le backend actuel et utiliser Agg pour la génération PDF
_original_backend = matplotlib.get_backend()
try:
    matplotlib.use('Agg')
except:
    pass
import matplotlib.pyplot as plt
import numpy as np

class PDFReportGenerator:
    """Générateur de rapports PDF pour calculs de poussée sismique"""
    
    def __init__(self, filename: str):
        """
        Initialise le générateur PDF
        
        :param filename: Nom du fichier PDF à générer
        """
        self.filename = filename
        self.story = []
        self.styles = getSampleStyleSheet()
        
        # Styles personnalisés
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Crée les styles personnalisés pour le document"""
        
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-titre
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#555555'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#1f4788'),
            borderPadding=5,
            backColor=colors.HexColor('#f0f4f8')
        ))
        
        # Note: BodyText existe déjà dans ReportLab, on l'utilise directement
        # On n'a pas besoin de style de formule pour ce rapport
    
    
    def add_cover_page(self, project_info: dict):
        """
        Ajoute la page de garde
        
        :param project_info: Dict avec 'title', 'date', 'code', etc.
        """
        # Espaceur du haut
        self.story.append(Spacer(1, 4*cm))
        
        # Titre principal
        title = Paragraph(project_info.get('title', 'Note de Calcul'), self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 1*cm))
        
        # Sous-titre
        subtitle = Paragraph(
            "Calcul de Poussée Sismique<br/>Méthode Mononobe-Okabe + Housner",
            self.styles['SubTitle']
        )
        self.story.append(subtitle)
        self.story.append(Spacer(1, 3*cm))
        
        # Tableau d'informations
        info_data = [
            ['Date:', project_info.get('date', datetime.now().strftime('%d/%m/%Y'))],
            ['Norme sismique:', project_info.get('code', 'EC8 France')],
            ['Logiciel:', 'Mononobe-Okabe Calculator v2.0'],
        ]
        
        info_table = Table(info_data, colWidths=[6*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 12),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(info_table)
        self.story.append(PageBreak())
    
    def add_input_section(self, inputs: dict):
        """
        Ajoute la section des données d'entrée
        
        :param inputs: Dictionnaire avec toutes les données d'entrée
        """
        # En-tête de section
        header = Paragraph("1. DONNÉES D'ENTRÉE", self.styles['SectionHeader'])
        self.story.append(header)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Norme sismique
        code_text = f"<b>Norme sismique :</b> {inputs.get('seismic_code', 'EC8')} "
        if inputs.get('seismic_code') == 'EC8':
            code_text += "🇫🇷 (EC8 France)"
        else:
            code_text += "🇲🇦 (RPS 2011 Maroc)"
        
        self.story.append(Paragraph(code_text, self.styles['BodyText']))
        self.story.append(Spacer(1, 0.3*cm))
        
        # Géométrie
        if inputs.get('mode') == 'tank':
            geom_data = [
                ['<b>GÉOMÉTRIE BÂCHE</b>', ''],
                ['Largeur Lx', f"{inputs.get('tank_width', 0):.2f} m"],
                ['Hauteur H', f"{inputs.get('tank_height', 0):.2f} m"],
                ['Profondeur Lz', f"{inputs.get('tank_length', 0):.2f} m"],
                ['Ép. Dalle Sup', f"{inputs.get('th_top', 0):.2f} m"],
                ['Ép. Radier', f"{inputs.get('th_bot', 0):.2f} m"],
                ['Ép. Voiles', f"{inputs.get('th_wall', 0):.2f} m"],
                ['Couverture Sol', f"{inputs.get('soil_cover', 0):.2f} m"],
            ]
        else:
            geom_data = [
                ['<b>GÉOMÉTRIE DU MUR</b>', ''],
                ['Hauteur H', f"{inputs.get('height', 0):.2f} m"],
                ['Inclinaison parement β', f"{inputs.get('beta', 0):.2f}°"],
                ['Pente du remblai i', f"{inputs.get('backfill_slope', 0):.2f}°"],
            ]
        
        geom_table = Table(geom_data, colWidths=[10*cm, 6*cm])
        geom_table.setStyle(self._get_table_style())
        self.story.append(geom_table)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Sol
        soil_data = [
            ['<b>PARAMÈTRES DU SOL</b>', ''],
            ['Angle de frottement φ', f"{inputs.get('phi', 0):.2f}°"],
            ['Angle de frottement sol-mur δ', f"{inputs.get('delta', 0):.2f}°"],
            ['Poids volumique γ', f"{inputs.get('gamma', 0):.2f} kN/m³"],
        ]
        
        soil_table = Table(soil_data, colWidths=[10*cm, 6*cm])
        soil_table.setStyle(self._get_table_style())
        self.story.append(soil_table)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Séisme
        seismic_data = [
            ['<b>PARAMÈTRES SISMIQUES</b>', ''],
            ['Zone sismique', str(inputs.get('zone', ''))],
        ]
        
        # Labels selon la norme
        if inputs.get('seismic_code') == 'EC8':
            seismic_data.extend([
                ['Catégorie d\'importance', inputs.get('importance', '')],
                ['Classe de sol', inputs.get('soil_class', '')],
                ['Coefficient r', f"{inputs.get('r_factor', 2.0):.2f}"],
            ])
        else:  # RPS2011
            seismic_data.extend([
                ['Classe d\'importance', inputs.get('importance', '')],
                ['Classe de site', inputs.get('soil_class', '')],
                ['Coefficient R', f"{inputs.get('r_factor', 2.0):.2f}"],
            ])
        
        seismic_table = Table(seismic_data, colWidths=[10*cm, 6*cm])
        seismic_table.setStyle(self._get_table_style())
        self.story.append(seismic_table)
        
        # Eau (si présent)
        if inputs.get('has_water', False):
            self.story.append(Spacer(1, 0.5*cm))
            water_data = [
                ['<b>PRÉSENCE D\'EAU (HOUSNER)</b>', ''],
                ['Hauteur d\'eau hw', f"{inputs.get('hw', 0):.2f} m"],
                ['Largeur réservoir L', f"{inputs.get('L', 0):.2f} m"],
                ['Masse volumique γw', f"{inputs.get('gamma_w', 10.0):.2f} kN/m³"],
                ['Méthode de combinaison', inputs.get('combination_method', 'SRSS')],
            ]
            
            water_table = Table(water_data, colWidths=[10*cm, 6*cm])
            water_table.setStyle(self._get_table_style())
            self.story.append(water_table)
        
        self.story.append(Spacer(1, 1*cm))
    
    def add_results_section(self, results: dict):
        """
        Ajoute la section des résultats
        
        :param results: Dictionnaire avec tous les résultats
        """
        # En-tête
        header = Paragraph("2. RÉSULTATS DU CALCUL", self.styles['SectionHeader'])
        self.story.append(header)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Si Mode Bâche
        if results.get('mode') == 'tank':
            # Sollicitations
            sol_data = [
                ['<b>SOLLICITATIONS (ELS/ELU)</b>', ''],
                ['Moment Coin Sup (M_A)', f"{results.get('M_A', 0):.1f} kNm"],
                ['Moment Travée Sup (M_mid)', f"{results.get('M_mid', 0):.1f} kNm"],
                ['Moment Pied Voile (M_D)', f"{results.get('M_D', 0):.1f} kNm"],
                ['Traction Traverse (N_top)', f"{results.get('N_top', 0):.1f} kN"],
                ['Traction Radier (N_bot)', f"{results.get('N_bot', 0):.1f} kN"],
            ]
            
            sol_table = Table(sol_data, colWidths=[10*cm, 6*cm])
            sol_table.setStyle(self._get_table_style())
            self.story.append(sol_table)
            
            # Housner pour Bâche
            if results.get('Pi'):
                self.story.append(Spacer(1, 0.5*cm))
                hydro_data = [
                    ['<b>POUSSÉE HYDRODYNAMIQUE (Housner)</b>', ''],
                    ['<i>Composante Impulsive</i>', ''],
                    ['  Masse mi', f"{results.get('mi', 0):.2f} t/m"],
                    ['  Pression Pi', f"{results.get('Pi', 0):.2f} kN/m"],
                    ['  Hauteur hi', f"{results.get('hi', 0):.2f} m"],
                    ['<i>Composante Convective</i>', ''],
                    ['  Masse mc', f"{results.get('mc', 0):.2f} t/m"],
                    ['  Période Tc', f"{results.get('Tc', 0):.2f} s"],
                    ['  Pression Pc', f"{results.get('Pc', 0):.2f} kN/m"],
                    ['  Hauteur hc', f"{results.get('hc', 0):.2f} m"],
                ]
                hydro_table = Table(hydro_data, colWidths=[10*cm, 6*cm])
                hydro_table.setStyle(self._get_table_style())
                self.story.append(hydro_table)
            
            self.story.append(Spacer(1, 1*cm))
            return

        # Coefficients sismiques
        coef_data = [
            ['<b>COEFFICIENTS SISMIQUES</b>', ''],
            ['kh (horizontal)', f"{results.get('kh', 0):.4f}"],
            ['kv (vertical)', f"{results.get('kv', 0):.4f}"],
            ['θ (angle sismique)', f"{results.get('theta', 0):.2f}°"],
        ]
        
        coef_table = Table(coef_data, colWidths=[10*cm, 6*cm])
        coef_table.setStyle(self._get_table_style())
        self.story.append(coef_table)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Poussée des terres
        terre_data = [
            ['<b>POUSSÉE DES TERRES (Mononobe-Okabe)</b>', ''],
            ['Coefficient Kae', f"{results.get('kae', 0):.4f}"],
            ['Poussée Pae', f"{results.get('pae', 0):.2f} kN/m"],
            ['Point d\'application', f"{results.get('height', 0)/3:.2f} m depuis la base"],
        ]
        
        terre_table = Table(terre_data, colWidths=[10*cm, 6*cm])
        terre_table.setStyle(self._get_table_style())
        self.story.append(terre_table)
        
        # Poussée hydrodynamique (si eau)
        if results.get('has_water', False):
            self.story.append(Spacer(1, 0.5*cm))
            
            hydro_data = [
                ['<b>POUSSÉE HYDRODYNAMIQUE (Housner)</b>', ''],
                ['<i>Composante Impulsive</i>', ''],
                ['  Masse mi', f"{results.get('mi', 0):.2f} t/m"],
                ['  Pression Pi', f"{results.get('Pi', 0):.2f} kN/m"],
                ['  Hauteur hi', f"{results.get('hi', 0):.2f} m"],
                ['<i>Composante Convective</i>', ''],
                ['  Masse mc', f"{results.get('mc', 0):.2f} t/m"],
                ['  Période Tc', f"{results.get('Tc', 0):.2f} s"],
                ['  Pression Pc', f"{results.get('Pc', 0):.2f} kN/m"],
                ['  Hauteur hc', f"{results.get('hc', 0):.2f} m"],
                ['<i>Total (SRSS)</i>', ''],
                ['  Pw', f"{results.get('Pw', 0):.2f} kN/m"],
            ]
            
            hydro_table = Table(hydro_data, colWidths=[10*cm, 6*cm])
            hydro_table.setStyle(self._get_table_style())
            self.story.append(hydro_table)
            
            # Total
            self.story.append(Spacer(1, 0.5*cm))
            total_data = [
                ['<b>POUSSÉE TOTALE SISMIQUE</b>', ''],
                ['Ptotal = Pae + Pw', f"<b>{results.get('Ptotal', 0):.2f} kN/m</b>"],
            ]
            
            total_table = Table(total_data, colWidths=[10*cm, 6*cm])
            total_table.setStyle(self._get_total_table_style())
            self.story.append(total_table)
        
        self.story.append(Spacer(1, 1*cm))

    def add_stability_section(self, results: dict):
        """Ajoute la section de vérification de stabilité"""
        header = Paragraph("3. VÉRIFICATION DE STABILITÉ", self.styles['SectionHeader'])
        self.story.append(header)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Si Mode Bâche
        if results.get('mode') == 'tank':
            stab_data = [
                ['<b>CRITÈRE</b>', '<b>VALEUR</b>', '<b>LIMITE</b>', '<b>STATUT</b>'],
                ['Flottaison (Fs)', f"{results.get('Fs_flotation', 0):.2f}", ">= 1.10", results.get('status_flotation', '')],
                ['Glissement (Fs)', f"{results.get('Fs_glissement', 0):.2f}", ">= 1.50", results.get('status_glissement', '')],
                ['Portance σmax', f"{results.get('sigma_max', 0):.1f} kPa", f"<= {results.get('sigma_adm', 200):.0f} kPa", results.get('status_portance', '')],
            ]
            
            stab_table = Table(stab_data, colWidths=[5*cm, 4*cm, 4*cm, 3*cm])
            stab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.beige]),
            ]))
            self.story.append(stab_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # Section Cas de Charges
            cases_header = Paragraph("4. ENVELOPPE CAS DE CHARGES", self.styles['SectionHeader'])
            self.story.append(cases_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            cases_data = [
                ['<b>CAS</b>', '<b>DESCRIPTION</b>', '<b>M_D (kNm)</b>'],
                ['Cas 1', 'Vide + Terres', f"{abs(results.get('cas1_M_D', 0)):.1f}"],
                ['Cas 2', 'Plein Statique', f"{abs(results.get('cas2_M_D', 0)):.1f}"],
                ['Cas 3', 'Plein + Séisme', f"{results.get('cas3_M_D', 0):.1f}"],
                ['<b>Enveloppe</b>', '<b>M_D dimensionnant</b>', f"<b>{results.get('M_D_env', 0):.1f}</b>"],
            ]
            
            cases_table = Table(cases_data, colWidths=[3*cm, 6*cm, 4*cm])
            cases_table.setStyle(self._get_table_style())
            self.story.append(cases_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # Section Ferraillage
            reinf_header = Paragraph("5. FERRAILLAGE (ELU)", self.styles['SectionHeader'])
            self.story.append(reinf_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            reinf_data = [
                ['<b>ÉLÉMENT</b>', '<b>As requis</b>', '<b>DISPOSITION</b>'],
                ['Voile (Pied)', f"{results.get('As_wall', 0):.2f} cm²/m", 'Face intérieure'],
                ['Radier (Travée)', f"{results.get('As_slab', 0):.2f} cm²/m", 'Nappe inférieure'],
            ]
            
            reinf_table = Table(reinf_data, colWidths=[5*cm, 5*cm, 6*cm])
            reinf_table.setStyle(self._get_table_style())
            self.story.append(reinf_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # Section Effort Tranchant
            shear_header = Paragraph("6. EFFORT TRANCHANT (EC2 6.2)", self.styles['SectionHeader'])
            self.story.append(shear_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            VEd = results.get('V_Ed_wall', 0)
            VRdc = results.get('VRd_c', 0)
            Asw = results.get('Asw_required', 0)
            shear_status = "OK" if VEd <= VRdc else "Armatures transversales requises"
            
            shear_data = [
                ['<b>PARAMÈTRE</b>', '<b>VALEUR</b>', '<b>STATUT</b>'],
                ['Effort tranchant VEd', f"{VEd:.1f} kN", '-'],
                ['Résistance VRd,c', f"{VRdc:.1f} kN", shear_status],
            ]
            if Asw > 0:
                shear_data.append(['Armatures Asw', f"{Asw:.2f} cm² / 200mm", 'Nécessaire'])
            
            shear_table = Table(shear_data, colWidths=[5*cm, 5*cm, 6*cm])
            shear_table.setStyle(self._get_table_style())
            self.story.append(shear_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # Section Fissuration ELS
            crack_header = Paragraph("7. FISSURATION ELS (EC2 7.3.4)", self.styles['SectionHeader'])
            self.story.append(crack_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            wk = results.get('wk', 0)
            wk_status = results.get('wk_status', 'OK')
            
            crack_data = [
                ['<b>PARAMÈTRE</b>', '<b>VALEUR</b>', '<b>LIMITE</b>', '<b>STATUT</b>'],
                ['Ouverture fissure wk', f"{wk:.3f} mm", '≤ 0.20 mm', wk_status],
            ]
            
            crack_table = Table(crack_data, colWidths=[5*cm, 4*cm, 3*cm, 4*cm])
            crack_table.setStyle(self._get_table_style())
            self.story.append(crack_table)
            
            # Note étanchéité
            note = Paragraph(
                "<i>Note : Pour les ouvrages de rétention d'eau, l'ouverture de fissure maximale "
                "est limitée à 0.2 mm selon EC2-3 (classe d'étanchéité 1).</i>",
                self.styles['BodyText']
            )
            self.story.append(Spacer(1, 0.3*cm))
            self.story.append(note)
            self.story.append(Spacer(1, 0.5*cm))
            
            # ===== SECTION 8: ANALYSE SISMIQUE RPS 2011 =====
            rps_header = Paragraph("8. ANALYSE SISMIQUE RPS 2011", self.styles['SectionHeader'])
            self.story.append(rps_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            rps_data = [
                ['<b>PARAMÈTRE</b>', '<b>VALEUR</b>', '<b>STATUT</b>'],
                ['Effort Tranchant Base V', f"{results.get('V_base', 0):.1f} kN", results.get('V_base_formula', '-')],
                ['Renversement Fs', f"{results.get('Fs_renversement', 0):.2f}", 'OK' if results.get('Fs_renversement', 0) >= 1.5 else 'NON VÉRIFIÉ'],
                ['Dépl. en tête δ', f"{results.get('delta_max', 0):.2f} mm", f"Limite: {results.get('delta_lim', 0):.2f} mm"],
            ]
            
            rps_table = Table(rps_data, colWidths=[5*cm, 5*cm, 6*cm])
            rps_table.setStyle(self._get_table_style())
            self.story.append(rps_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # ===== SECTION 9: VÉRIFICATIONS RADIER =====
            raft_header = Paragraph("9. VÉRIFICATIONS RADIER", self.styles['SectionHeader'])
            self.story.append(raft_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            raft_data = [
                ['<b>VÉRIFICATION</b>', '<b>VALEUR</b>', '<b>STATUT</b>'],
                ['Rigidité (L/e)', f"{results.get('raft_ratio', 0):.1f}", results.get('raft_classification', '-')],
                ['Poinçonnement (vEd/vRd)', f"{results.get('punching_ratio', 0):.2f}", results.get('punching_status', '-')],
            ]
            
            raft_table = Table(raft_data, colWidths=[5*cm, 5*cm, 6*cm])
            raft_table.setStyle(self._get_table_style())
            self.story.append(raft_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # ===== SECTION 10: VÉRIFICATIONS VOILES =====
            wall_header = Paragraph("10. VÉRIFICATIONS VOILES", self.styles['SectionHeader'])
            self.story.append(wall_header)
            self.story.append(Spacer(1, 0.3*cm))
            
            wall_data = [
                ['<b>VÉRIFICATION</b>', '<b>RÉSULTAT</b>', '<b>STATUT</b>'],
                ['Flexion Composée', results.get('combined_type', '-'), f"As = {results.get('combined_As', 0):.2f} cm²/m"],
                ['Interface Voile-Radier', f"vEdi = {results.get('interface_vEdi', 0):.3f} MPa", results.get('interface_status', '-')],
            ]
            if results.get('interface_Asv', 0) > 0:
                wall_data.append(['Armatures couture', f"Asv = {results.get('interface_Asv', 0):.2f} cm²/m", 'Requises'])
            
            wall_table = Table(wall_data, colWidths=[5*cm, 5*cm, 6*cm])
            wall_table.setStyle(self._get_table_style())
            self.story.append(wall_table)
            self.story.append(Spacer(1, 0.5*cm))
            
            # ===== SECTION 11: VÉRIFICATIONS POTEAUX (Si présents) =====
            column_result = results.get('column_result')
            if column_result:
                col_header = Paragraph("11. VÉRIFICATIONS POTEAUX", self.styles['SectionHeader'])
                self.story.append(col_header)
                self.story.append(Spacer(1, 0.3*cm))
                
                col_data = [
                    ['<b>PARAMÈTRE</b>', '<b>VALEUR</b>', '<b>STATUT</b>'],
                    ['Charge Axiale N_Ed', f"{column_result['N_Ed']:.1f} kN", '-'],
                    ['Élancement λ', f"{column_result['lambda']:.1f} (λlim={column_result['lambda_lim']:.1f})", 'Flambement' if column_result['needs_second_order'] else 'OK'],
                    ['Effet 2nd Ordre e2', f"{column_result['e_2']:.1f} mm", 'Pris en compte' if column_result['needs_second_order'] else '-'],
                    ['Armatures As min', f"{column_result['As_min_cm2']:.2f} cm²", 'Calculé selon EC2 9.5.2'],
                    ['Armatures As requis', f"{column_result['As_required_cm2']:.2f} cm²", column_result['status']],
                ]
                
                col_table = Table(col_data, colWidths=[5*cm, 5*cm, 6*cm])
                col_table.setStyle(self._get_table_style())
                self.story.append(col_table)
                self.story.append(Spacer(1, 1*cm))
            self.story.append(Spacer(1, 1*cm))
            return

        # Glissement
        sliding_status = "OK" if results.get('Fs_sliding', 0) >= 1.5 else "NON CONFORME"
        
        # Renversement
        overturning_status = "OK" if results.get('Fr_overturning', 0) >= 1.5 else "NON CONFORME"
        
        # Portance
        eccentricity_status = "OK" if results.get('eccentricity', 0) < results.get('width_B', 0)/3 else "DECOLLEMENT"
        
        stab_data = [
            ['<b>CRITÈRE</b>', '<b>VALEUR</b>', '<b>LIMITE</b>', '<b>STATUT</b>'],
            ['Glissement (Fs)', f"{results.get('Fs_sliding', 0):.2f}", ">= 1.50", sliding_status],
            ['Renversement (Fr)', f"{results.get('Fr_overturning', 0):.2f}", ">= 1.50", overturning_status],
            ['Excentrement (e)', f"{results.get('eccentricity', 0):.3f} m", f"< {results.get('width_B', 0)/3:.3f} m", eccentricity_status],
            ['Contrainte Sol (sigma_ref)', f"{results.get('sigma_ref', 0):.2f} kPa", "-", "-"],
            ['Contrainte Max (sigma_max)', f"{results.get('sigma_max', 0):.2f} kPa", "-", "-"],
        ]
        
        stab_table = Table(stab_data, colWidths=[5*cm, 4*cm, 3*cm, 4*cm])
        stab_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.beige]),
        ]))
        self.story.append(stab_table)
        self.story.append(Spacer(1, 1*cm))
    
    def add_references(self):
        """Ajoute les références normatives"""
        header = Paragraph("4. RÉFÉRENCES", self.styles['SectionHeader'])
        self.story.append(header)
        self.story.append(Spacer(1, 0.5*cm))
        
        refs = [
            "• EN 1998-5:2004 - Eurocode 8 : Fondations et murs de soutènement",
            "• EN 1998-4:2006 - Eurocode 8 : Silos, réservoirs et canalisations",
            "• Arrêté du 22 octobre 2010 - Classification parasismique France",
            "• RPS 2011 - Règlement Parasismique Marocain",
            "• Housner, G.W. (1963) - The dynamic behavior of water tanks",
        ]
        
        for ref in refs:
            self.story.append(Paragraph(ref, self.styles['BodyText']))
        
        self.story.append(Spacer(1, 1*cm))
    
    def _get_table_style(self):
        """Style standard pour les tableaux"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
    
    def _get_total_table_style(self):
        """Style pour le tableau de total"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d14')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 2, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ])
    
    def add_frame_diagram(self, results: dict):
        """
        Ajoute le schéma du cadre avec diagramme des moments au PDF.
        
        :param results: Dictionnaire contenant les résultats du calcul tank
        """
        if results.get('mode') != 'tank':
            return
        
        header = Paragraph("8. SCHÉMA STRUCTURAL", self.styles['SectionHeader'])
        self.story.append(header)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Générer la figure matplotlib
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # --- Schéma du cadre ---
        ax1 = axes[0]
        W = results.get('tank_width', 4.0)
        H = results.get('tank_height', 3.0)
        th = results.get('th_wall', 0.25)
        
        # Cadre
        ax1.plot([0, 0, W, W, 0], [0, H, H, 0, 0], 'b-', linewidth=3, label='Cadre')
        
        # Épaisseurs
        ax1.fill([-th/2, th/2, th/2, -th/2], [0, 0, H, H], color='gray', alpha=0.7)
        ax1.fill([W-th/2, W+th/2, W+th/2, W-th/2], [0, 0, H, H], color='gray', alpha=0.7)
        ax1.fill([0, W, W, 0], [H-th/2, H-th/2, H+th/2, H+th/2], color='gray', alpha=0.7)
        ax1.fill([0, W, W, 0], [-th/2, -th/2, th/2, th/2], color='gray', alpha=0.7)
        
        # Poussée terres
        Pae = results.get('pae', 0)
        if Pae > 0:
            for i in range(5):
                y = H * (i + 0.5) / 5
                arrow_len = 0.4 + 0.3 * i / 5
                ax1.arrow(-arrow_len - 0.2, y, arrow_len, 0, head_width=0.08, head_length=0.08, fc='orange', ec='orange')
            ax1.text(-1.2, H/2, f'Pae\n{Pae:.0f} kN/m', ha='center', fontsize=9, color='darkorange')
        
        # Points A, B, C, D
        ax1.plot(0, H, 'ro', markersize=8)
        ax1.text(-0.2, H + 0.15, 'A', fontsize=10, fontweight='bold')
        ax1.plot(W, H, 'ro', markersize=8)
        ax1.text(W + 0.1, H + 0.15, 'B', fontsize=10, fontweight='bold')
        ax1.plot(W, 0, 'ro', markersize=8)
        ax1.text(W + 0.1, -0.2, 'C', fontsize=10, fontweight='bold')
        ax1.plot(0, 0, 'ro', markersize=8)
        ax1.text(-0.2, -0.2, 'D', fontsize=10, fontweight='bold')
        
        ax1.set_xlim(-1.5, W + 1.5)
        ax1.set_ylim(-0.5, H + 0.8)
        ax1.set_aspect('equal')
        ax1.set_title('Schéma du Cadre', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('Largeur (m)')
        ax1.set_ylabel('Hauteur (m)')
        
        # --- Diagramme des moments COMPLET ---
        ax2 = axes[1]
        M_A = results.get('M_A', 0)  # Coin sup gauche
        M_D = results.get('M_D', 0)  # Pied voile gauche  
        M_mid = results.get('M_mid', 0)  # Mi-travée traverse sup
        
        # Échelle pour les moments
        M_scale = max(abs(M_A), abs(M_D), abs(M_mid), 1) / 1.2
        
        # Cadre de référence (axes neutres)
        ax2.plot([0, 0, W, W, 0], [0, H, H, 0, 0], 'b-', linewidth=2, alpha=0.7)
        
        # --- Voile Gauche (D→A) ---
        y_left = np.linspace(0, H, 30)
        M_left = M_D + (M_A - M_D) * (y_left / H)
        x_left = -M_left / M_scale
        ax2.fill_betweenx(y_left, 0, x_left, color='red', alpha=0.4)
        ax2.plot(x_left, y_left, 'r-', linewidth=2)
        
        # --- Voile Droit (C→B) - Symétrique ---
        x_right = W + M_left / M_scale
        ax2.fill_betweenx(y_left, W, x_right, color='red', alpha=0.4)
        ax2.plot(x_right, y_left, 'r-', linewidth=2)
        
        # --- Traverse Supérieure (A→B) - Moment parabolique ---
        x_top = np.linspace(0, W, 30)
        # Distribution parabolique: M_A aux coins, M_mid au centre
        M_top = M_A + (M_mid - M_A) * 4 * (x_top / W) * (1 - x_top / W)
        y_top = H + M_top / M_scale
        ax2.fill_between(x_top, H, y_top, color='red', alpha=0.4)
        ax2.plot(x_top, y_top, 'r-', linewidth=2)
        
        # --- Radier (D→C) - Moment parabolique similaire ---
        M_bot = M_D + (M_mid * 0.8 - M_D) * 4 * (x_top / W) * (1 - x_top / W)
        y_bot = -M_bot / M_scale
        ax2.fill_between(x_top, 0, y_bot, color='blue', alpha=0.3)
        ax2.plot(x_top, y_bot, 'b-', linewidth=2)
        
        # Annotations des moments
        ax2.annotate(f'{M_D:.0f}', xy=(0, 0), xytext=(-0.8, -0.3), fontsize=9, color='darkred', fontweight='bold')
        ax2.annotate(f'{M_A:.0f}', xy=(0, H), xytext=(-0.8, H + 0.2), fontsize=9, color='darkred', fontweight='bold')
        ax2.annotate(f'{M_mid:.0f}', xy=(W/2, H), xytext=(W/2, H + abs(M_mid)/M_scale + 0.3), fontsize=9, color='darkred', fontweight='bold', ha='center')
        
        # Points A, B, C, D
        for pt, (px, py) in [('A', (0, H)), ('B', (W, H)), ('C', (W, 0)), ('D', (0, 0))]:
            ax2.plot(px, py, 'ko', markersize=6)
            ax2.text(px + (-0.15 if px == 0 else 0.1), py + 0.1, pt, fontsize=9, fontweight='bold')
        
        # Légende couleurs
        ax2.text(W + 0.5, H * 0.7, 'Rouge:\nVoiles &\nTraverse', fontsize=8, color='darkred')
        ax2.text(W + 0.5, H * 0.3, 'Bleu:\nRadier', fontsize=8, color='darkblue')
        
        ax2.set_xlim(-2, W + 2.5)
        ax2.set_ylim(-1.5, H + 2)
        ax2.set_aspect('equal')
        ax2.set_title('Diagramme des Moments [kNm]', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel('Largeur (m)')
        ax2.set_ylabel('Hauteur (m)')
        
        plt.tight_layout()
        
        # Sauvegarder dans un fichier temporaire (compatible Windows)
        tmp_dir = tempfile.gettempdir()
        tmp_path = os.path.join(tmp_dir, f'frame_diagram_{os.getpid()}.png')
        fig.savefig(tmp_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        # Stocker le chemin pour nettoyage ultérieur
        self._temp_files = getattr(self, '_temp_files', [])
        self._temp_files.append(tmp_path)
        
        # Ajouter l'image au PDF
        img = Image(tmp_path, width=16*cm, height=7*cm)
        self.story.append(img)
        self.story.append(Spacer(1, 0.5*cm))
        
        # Légende
        legend = Paragraph(
            "<i>Figure : Schéma du cadre (gauche) et diagramme des moments fléchissants (droite). "
            "Les zones rouges représentent les moments sollicitant les fibres intérieures.</i>",
            self.styles['BodyText']
        )
        self.story.append(legend)
        self.story.append(Spacer(1, 1*cm))
    
    def generate(self) -> str:
        """
        Génère le PDF final
        
        :return: Chemin du fichier généré
        """
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        doc.build(self.story)
        
        # Nettoyer les fichiers temporaires après génération
        for tmp_file in getattr(self, '_temp_files', []):
            try:
                os.unlink(tmp_file)
            except:
                pass
        
        return self.filename
