import flet as ft
import math
import random
from math import sqrt

import socket
import qrcode
import webbrowser

def get_local_ip():
    """Récupère l'adresse IP locale de l'ordinateur"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Générer un QR code
local_ip = get_local_ip()
url = f"http://{local_ip}:8000"
qr = qrcode.make(url)
qr.save("science_app_qrcode.png")

print(f"\n" + "="*50)
print(f"📱 Pour visualiser sur Android:")
print(f"="*50)
print(f"1. Assurez-vous que votre téléphone est sur le même Wi-Fi")
print(f"2. Scannez le QR code 'science_app_qrcode.png' avec l'app Flet")
print(f"3. Ou entrez l'URL: {url}")
print(f"="*50 + "\n")

# Optionnel: ouvrir le QR code automatiquement
webbrowser.open("science_app_qrcode.png")

def main(page: ft.Page):
    page.title = "Science en une App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 420
    page.window_height = 7500
    page.scroll = ft.ScrollMode.AUTO  # Permet le défilement
    
    # ==============================
    # SOUS-TITRE DE L'APPLICATION
    # ==============================
    SUBTITLE = "Labo IA CAEB-NATI 2026"
    
    # Fonction pour créer un AppBar avec bouton retour texte
    def create_app_bar(title, back_function):
        return ft.AppBar(
            title=ft.Column([
                ft.Text(title, size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ft.Text(SUBTITLE, size=10, color=ft.Colors.WHITE70),
            ], spacing=10),
            leading=ft.TextButton("← Retour", on_click=back_function, style=ft.ButtonStyle(color=ft.Colors.WHITE)),
            bgcolor=ft.Colors.BLUE_800,
            toolbar_height=60
        )
    
    # ==============================
    # JEU DE CALCUL MENTAL (CORRIGÉ)
    # ==============================
    def jeu_calcul_mental(page):
        # Variables du jeu
        maximum = 0
        temps_max = 0
        score = 0
        vies = 3
        question_num = 0
        current_a = 0
        current_b = 0
        current_operation = ""
        current_resultat = 0
        timer_active = False
        timer_value = 0
        partie_commencee = False
        
        def start_game(e):
            nonlocal maximum, temps_max, score, vies, question_num, partie_commencee
            niveau = niveau_dropdown.value
            
            if niveau == "1":
                maximum = 10
                temps_max = 15
            elif niveau == "2":
                maximum = 500
                temps_max = 10
            elif niveau == "3":
                maximum = 100
                temps_max = 5
            else:
                resultat_text.value = "Niveau invalide."
                page.update()
                return
            
            score = 0
            vies = 3
            question_num = 0
            partie_commencee = True
            score_text.value = f"Score: {score} | Vies: {vies}"
            niveau_dropdown.disabled = True
            start_btn.disabled = True
            page.update()
            show_question()
        
        def show_question():
            nonlocal current_a, current_b, current_operation, current_resultat, timer_value, timer_active, question_num
            if vies <= 0:
                end_game()
                return
            
            if question_num >= 10:
                end_game()
                return
            
            current_a = random.randint(1, maximum)
            current_b = random.randint(1, maximum)
            current_operation = random.choice(["+", "-", "*", "/"])
            
            if current_operation == "/":
                current_b = random.randint(1, max(2, maximum//2))
                current_a = current_b * random.randint(1, maximum // current_b)
                current_resultat = current_a // current_b
            elif current_operation == "+":
                current_resultat = current_a + current_b
            elif current_operation == "-":
                current_resultat = current_a - current_b
            elif current_operation == "*":
                current_resultat = current_a * current_b
            
            question_text.value = f"Question {question_num + 1}/10\n\n{current_a} {current_operation} {current_b} = ?"
            reponse_field.value = ""
            reponse_field.disabled = False
            valider_btn.disabled = False
            timer_text.value = f"⏱️ Temps restant: {temps_max}s"
            page.update()
            
            # Démarrer le timer
            timer_value = temps_max
            timer_active = True
            
            def update_timer():
                nonlocal timer_value, timer_active, vies
                if timer_active and timer_value > 0 and partie_commencee:
                    timer_value -= 1
                    timer_text.value = f"⏱️ Temps restant: {timer_value}s"
                    page.update()
                    if timer_value == 0:
                        timer_active = False
                        vies -= 1
                        resultat_text.value = f"⏰ Trop lent! -1 vie. Vies restantes: {vies}"
                        page.update()
                        page.after(1500, lambda: show_question() if vies > 0 and question_num < 10 else end_game())
                    else:
                        page.after(1000, update_timer)
            
            page.after(1000, update_timer)
        
        def check_answer(e):
            nonlocal score, vies, question_num, timer_active
            if not partie_commencee:
                return
            
            timer_active = False
            
            try:
                reponse = int(reponse_field.value)
                if reponse == current_resultat:
                    score += 100
                    resultat_text.value = f"✅ Bonne réponse! +100 points"
                else:
                    vies -= 1
                    score -= 50
                    resultat_text.value = f"❌ Mauvaise réponse! La bonne réponse était: {current_resultat} -50 points"
                
                score_text.value = f"Score: {score} | Vies: {vies}"
                question_num += 1
                reponse_field.disabled = True
                valider_btn.disabled = True
                page.update()
                
                if vies > 0 and question_num < 10:
                    page.after(1500, show_question)
                else:
                    page.after(1500, end_game)
                    
            except ValueError:
                resultat_text.value = "⚠️ Entrez un nombre valide!"
                page.update()
        
        def end_game():
            nonlocal partie_commencee
            partie_commencee = False
            
            if vies <= 0:
                message = f"💀 GAME OVER!\nScore final: {score}\nVies restantes: {vies}"
            else:
                message = f"🎉 FIN DU JEU!\nScore final: {score}\nVies restantes: {vies}"
            
            if score >= 800:
                message += "\n🏆 Excellent joueur!"
            elif score >= 500:
                message += "\n👍 Très bon score!"
            else:
                message += "\n💪 Continue à t'entraîner!"
            
            question_text.value = message
            reponse_field.disabled = True
            valider_btn.disabled = True
            niveau_dropdown.disabled = False
            start_btn.disabled = False
            timer_text.value = ""
            page.update()
        
        niveau_dropdown = ft.Dropdown(
            width=250,
            options=[
                ft.dropdown.Option("1", "1 - Facile (1-10, 15s)"),
                ft.dropdown.Option("2", "2 - Moyen (1-50, 10s)"),
                ft.dropdown.Option("3", "3 - Difficile (1-100, 5s)"),
            ],
            label="Choisissez le niveau"
        )
        
        start_btn = ft.ElevatedButton("Commencer le jeu", on_click=start_game, width=250)
        score_text = ft.Text("Score: 0 | Vies: 3", size=16, weight=ft.FontWeight.BOLD)
        question_text = ft.Text("", size=20, text_align=ft.TextAlign.CENTER)
        reponse_field = ft.TextField(label="Votre réponse", width=250, disabled=True)
        valider_btn = ft.ElevatedButton("Valider", on_click=check_answer, width=250, disabled=True)
        timer_text = ft.Text("", size=16, color=ft.Colors.RED)
        resultat_text = ft.Text("", size=14)
        
        page.clean()
        page.add(
            create_app_bar("Jeu de Calcul Mental", lambda e: menu_jeux(page)),
            ft.Column([
                ft.Text("🎮 Jeu de Calcul Mental", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                niveau_dropdown,
                start_btn,
                score_text,
                question_text,
                reponse_field,
                valider_btn,
                timer_text,
                resultat_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        )
    
    # ==============================
    # JEU DEVINETTE
    # ==============================
    def jeu_devinette(page):
        nombre_secret = 0
        maximum = 0
        tentatives = 0
        jeu_actif = False
        
        def start_game(e):
            nonlocal nombre_secret, maximum, tentatives, jeu_actif
            niveau = niveau_dropdown.value
            
            if niveau == "f":
                maximum = 100
            elif niveau == "m":
                maximum = 500
            elif niveau == "d":
                maximum = 1000
            else:
                resultat_text.value = "Niveau invalide."
                page.update()
                return
            
            nombre_secret = random.randint(1, maximum)
            tentatives = 0
            jeu_actif = True
            instruction_text.value = f"🔢 Je pense à un nombre entre 1 et {maximum}"
            reponse_field.value = ""
            reponse_field.disabled = False
            valider_btn.disabled = False
            resultat_text.value = ""
            niveau_dropdown.disabled = True
            start_btn.disabled = True
            page.update()
        
        def verifier_reponse(e):
            nonlocal tentatives, jeu_actif
            if not jeu_actif:
                return
            
            try:
                choix = int(reponse_field.value)
                tentatives += 1
                
                if choix < nombre_secret:
                    resultat_text.value = f"📈 Trop petit! (Essai #{tentatives})"
                elif choix > nombre_secret:
                    resultat_text.value = f"📉 Trop grand! (Essai #{tentatives})"
                else:
                    resultat_text.value = f"🎉 Bravo! Tu as trouvé en {tentatives} tentatives!"
                    jeu_actif = False
                    reponse_field.disabled = True
                    valider_btn.disabled = True
                    niveau_dropdown.disabled = False
                    start_btn.disabled = False
                
                page.update()
            except:
                resultat_text.value = "⚠️ Entrez un nombre valide!"
                page.update()
        
        niveau_dropdown = ft.Dropdown(
            width=250,
            options=[
                ft.dropdown.Option("f", "Facile (1 à 100)"),
                ft.dropdown.Option("m", "Moyen (1 à 500)"),
                ft.dropdown.Option("d", "Difficile (1 à 1000)"),
            ],
            label="Choisissez le niveau"
        )
        
        start_btn = ft.ElevatedButton("Commencer", on_click=start_game, width=250)
        instruction_text = ft.Text("", size=16)
        reponse_field = ft.TextField(label="Votre nombre", width=250, disabled=True)
        valider_btn = ft.ElevatedButton("Valider", on_click=verifier_reponse, width=250, disabled=True)
        resultat_text = ft.Text("", size=16)
        
        page.clean()
        page.add(
            create_app_bar("Jeu Devine le Nombre", lambda e: menu_jeux(page)),
            ft.Column([
                ft.Text("🎲 Devine le nombre", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                niveau_dropdown,
                start_btn,
                instruction_text,
                reponse_field,
                valider_btn,
                resultat_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        )
    
    # ==============================
    # MENU JEUX
    # ==============================
    def menu_jeux(page):
        page.clean()
        page.add(
            create_app_bar("Jeux", lambda e: accueil(page)),
            ft.Column([
                ft.Text("🎮 Menu Jeux", size=28, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Jeu de Calcul Mental", on_click=lambda e: jeu_calcul_mental(page), width=280, height=50),
                ft.ElevatedButton("Jeu Devine le Nombre", on_click=lambda e: jeu_devinette(page), width=280, height=50),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        )
    
    # ==============================
    # DICTIONNAIRE DES ELEMENTS CHIMIQUES
    # ==============================
    elements = {
        "Hydrogène": {"symbole": "H", "masse": 1.008, "numero": 1},
        "Hélium": {"symbole": "He", "masse": 4.0026, "numero": 2},
        "Lithium": {"symbole": "Li", "masse": 6.94, "numero": 3},
        "Béryllium": {"symbole": "Be", "masse": 9.0122, "numero": 4},
        "Bore": {"symbole": "B", "masse": 10.81, "numero": 5},
        "Carbone": {"symbole": "C", "masse": 12.011, "numero": 6},
        "Azote": {"symbole": "N", "masse": 14.007, "numero": 7},
        "Oxygène": {"symbole": "O", "masse": 15.999, "numero": 8},
        "Fluor": {"symbole": "F", "masse": 18.998, "numero": 9},
        "Néon": {"symbole": "Ne", "masse": 20.180, "numero": 10},
        "Sodium": {"symbole": "Na", "masse": 22.990, "numero": 11},
        "Magnésium": {"symbole": "Mg", "masse": 24.305, "numero": 12},
        "Aluminium": {"symbole": "Al", "masse": 26.982, "numero": 13},
        "Silicium": {"symbole": "Si", "masse": 28.085, "numero": 14},
        "Phosphore": {"symbole": "P", "masse": 30.974, "numero": 15},
        "Soufre": {"symbole": "S", "masse": 32.06, "numero": 16},
        "Chlore": {"symbole": "Cl", "masse": 35.45, "numero": 17},
        "Argon": {"symbole": "Ar", "masse": 39.948, "numero": 18},
        "Potassium": {"symbole": "K", "masse": 39.098, "numero": 19},
        "Calcium": {"symbole": "Ca", "masse": 40.078, "numero": 20},
        "Fer": {"symbole": "Fe", "masse": 55.845, "numero": 26},
        "Cuivre": {"symbole": "Cu", "masse": 63.546, "numero": 29},
        "Zinc": {"symbole": "Zn", "masse": 65.38, "numero": 30},
        "Argent": {"symbole": "Ag", "masse": 107.87, "numero": 47},
        "Or": {"symbole": "Au", "masse": 196.97, "numero": 79},
        "Plomb": {"symbole": "Pb", "masse": 207.2, "numero": 82},
    }
    
    # ==============================
    # MENU CHIMIE
    # ==============================
    def menu_chimie(page):
        def concentration_molaire():
            def calculer(e):
                try:
                    n = float(n_field.value)
                    v = float(v_field.value)
                    c = n / v
                    resultat.value = f"Concentration molaire = {c:.2f} mol/L"
                    page.update()
                except:
                    resultat.value = "Erreur: vérifiez les valeurs"
                    page.update()
            
            n_field = ft.TextField(label="Nombre de moles (mol)", width=280)
            v_field = ft.TextField(label="Volume (L)", width=280)
            resultat = ft.Text("", size=16)
            
            page.clean()
            page.add(
                create_app_bar("Concentration molaire", lambda e: menu_chimie(page)),
                ft.Column([
                    ft.Text("C = n / V", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    n_field, v_field,
                    ft.ElevatedButton("Calculer", on_click=calculer),
                    resultat
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            )
        
        def concentration_massique():
            def calculer(e):
                try:
                    m = float(m_field.value)
                    v = float(v_field.value)
                    c = m / v
                    resultat.value = f"Concentration massique = {c:.2f} g/L"
                    page.update()
                except:
                    resultat.value = "Erreur: vérifiez les valeurs"
                    page.update()
            
            m_field = ft.TextField(label="Masse (g)", width=280)
            v_field = ft.TextField(label="Volume (L)", width=280)
            resultat = ft.Text("", size=16)
            
            page.clean()
            page.add(
                create_app_bar("Concentration massique", lambda e: menu_chimie(page)),
                ft.Column([
                    ft.Text("Cm = m / V", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    m_field, v_field,
                    ft.ElevatedButton("Calculer", on_click=calculer),
                    resultat
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            )
        
        def tableau_periodique():
            def rechercher(e):
                type_recherche = recherche_type.value
                terme = recherche_field.value
                trouve = False
                
                for nom, data in elements.items():
                    if type_recherche == "Nom" and nom.lower() == terme.lower():
                        resultat.value = f"Nom: {nom}\nSymbole: {data['symbole']}\nNuméro: {data['numero']}\nMasse: {data['masse']} g/mol"
                        trouve = True
                        break
                    elif type_recherche == "Symbole" and data['symbole'].lower() == terme.lower():
                        resultat.value = f"Nom: {nom}\nSymbole: {data['symbole']}\nNuméro: {data['numero']}\nMasse: {data['masse']} g/mol"
                        trouve = True
                        break
                    elif type_recherche == "Numéro" and str(data['numero']) == terme:
                        resultat.value = f"Nom: {nom}\nSymbole: {data['symbole']}\nNuméro: {data['numero']}\nMasse: {data['masse']} g/mol"
                        trouve = True
                        break
                
                if not trouve:
                    resultat.value = "Élément non trouvé"
                page.update()
            
            recherche_type = ft.Dropdown(
                width=150,
                options=[
                    ft.dropdown.Option("Nom"),
                    ft.dropdown.Option("Symbole"),
                    ft.dropdown.Option("Numéro"),
                ],
                value="Nom"
            )
            recherche_field = ft.TextField(label="Rechercher", width=250)
            resultat = ft.Text("", size=16)
            
            page.clean()
            page.add(
                create_app_bar("Tableau périodique", lambda e: menu_chimie(page)),
                ft.Column([
                    ft.Text("Tableau périodique des éléments", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([recherche_type, recherche_field], alignment=ft.MainAxisAlignment.CENTER),
                    ft.ElevatedButton("Rechercher", on_click=rechercher),
                    resultat
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            )
        
        page.clean()
        page.add(
            create_app_bar("Chimie", lambda e: accueil(page)),
            ft.Column([
                ft.Text("🧪 Menu Chimie", size=28, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Concentration molaire (C=n/V)", on_click=lambda e: concentration_molaire(), width=280, height=50),
                ft.ElevatedButton("Concentration massique (Cm=m/V)", on_click=lambda e: concentration_massique(), width=280, height=50),
                ft.ElevatedButton("Tableau périodique", on_click=lambda e: tableau_periodique(), width=280, height=50),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        )
    
    # ==============================
    # ====== PHYSIQUE ===============
    # ==============================
    
    def menu_physique(page):
        def electricite():
            def intensite():
                def calculer(e):
                    try:
                        n = float(n_field.value)
                        N = float(N_field.value)
                        Ic = float(Ic_field.value)
                        I = (n * Ic) / N
                        resultat.value = f"Intensité I = {I:.2f} A"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                n_field = ft.TextField(label="Division lue", width=250)
                N_field = ft.TextField(label="Nombre total de divisions", width=250)
                Ic_field = ft.TextField(label="Calibre choisi (A)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Intensité du courant", lambda e: electricite()),
                    ft.Column([n_field, N_field, Ic_field, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def tension():
                def calculer(e):
                    try:
                        n = float(n_field.value)
                        N = float(N_field.value)
                        Uc = float(Uc_field.value)
                        U = (n * Uc) / N
                        resultat.value = f"Tension U = {U:.2f} V"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                n_field = ft.TextField(label="Division lue", width=250)
                N_field = ft.TextField(label="Nombre total de divisions", width=250)
                Uc_field = ft.TextField(label="Calibre choisi (V)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Tension électrique", lambda e: electricite()),
                    ft.Column([n_field, N_field, Uc_field, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def resistance_serie():
                def calculer(e):
                    try:
                        r1 = float(r1_field.value)
                        r2 = float(r2_field.value)
                        Re = r1 + r2
                        resultat.value = f"Résistance équivalente = {Re:.2f} Ω"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                r1_field = ft.TextField(label="Résistance R1 (Ω)", width=250)
                r2_field = ft.TextField(label="Résistance R2 (Ω)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Résistance en série", lambda e: electricite()),
                    ft.Column([r1_field, r2_field, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def resistance_parallele():
                def calculer(e):
                    try:
                        r1 = float(r1_field.value)
                        r2 = float(r2_field.value)
                        Re = (r1 * r2) / (r1 + r2)
                        resultat.value = f"Résistance équivalente = {Re:.2f} Ω"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                r1_field = ft.TextField(label="Résistance R1 (Ω)", width=250)
                r2_field = ft.TextField(label="Résistance R2 (Ω)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Résistance en parallèle", lambda e: electricite()),
                    ft.Column([r1_field, r2_field, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            page.clean()
            page.add(
                create_app_bar("Électricité", lambda e: menu_physique(page)),
                ft.Column([
                    ft.Text("⚡ Électricité", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Intensité du courant", on_click=lambda e: intensite(), width=280),
                    ft.ElevatedButton("Tension électrique", on_click=lambda e: tension(), width=280),
                    ft.ElevatedButton("Résistance en série", on_click=lambda e: resistance_serie(), width=280),
                    ft.ElevatedButton("Résistance en dérivation", on_click=lambda e: resistance_parallele(), width=280),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            )
        
        def cinematique():
            def vitesse():
                def calculer(e):
                    try:
                        d = float(distance.value)
                        t = float(temps.value)
                        v = d / t
                        resultat.value = f"Vitesse = {v:.2f} m/s"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                distance = ft.TextField(label="Distance (m)", width=250)
                temps = ft.TextField(label="Temps (s)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Vitesse", lambda e: cinematique()),
                    ft.Column([distance, temps, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def energie_cinetique():
                def calculer(e):
                    try:
                        m = float(masse.value)
                        v = float(vitesse.value)
                        Ec = (m * v**2) / 2
                        resultat.value = f"Énergie cinétique = {Ec:.2f} J"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                masse = ft.TextField(label="Masse (kg)", width=250)
                vitesse = ft.TextField(label="Vitesse (m/s)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Énergie cinétique", lambda e: cinematique()),
                    ft.Column([masse, vitesse, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def travail():
                def calculer(e):
                    try:
                        F = float(force.value)
                        d = float(distance.value)
                        angle = float(angle_field.value)
                        W = F * d * math.cos(math.radians(angle))
                        resultat.value = f"Travail = {W:.2f} J"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                force = ft.TextField(label="Force (N)", width=250)
                distance = ft.TextField(label="Distance (m)", width=250)
                angle_field = ft.TextField(label="Angle (degrés)", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Travail", lambda e: cinematique()),
                    ft.Column([force, distance, angle_field, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            page.clean()
            page.add(
                create_app_bar("Cinématique", lambda e: menu_physique(page)),
                ft.Column([
                    ft.Text("📐 Cinématique", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Vitesse (v = d/t)", on_click=lambda e: vitesse(), width=280),
                    ft.ElevatedButton("Énergie cinétique (Ec = ½mv²)", on_click=lambda e: energie_cinetique(), width=280),
                    ft.ElevatedButton("Travail (W = F×d×cosθ)", on_click=lambda e: travail(), width=280),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            )
        
        page.clean()
        page.add(
            create_app_bar("Physique", lambda e: accueil(page)),
            ft.Column([
                ft.Text("⚡ Menu Physique", size=28, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Électricité", on_click=lambda e: electricite(), width=280, height=50),
                ft.ElevatedButton("Cinématique", on_click=lambda e: cinematique(), width=280, height=50),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        )
    
    # ==============================
    # MATHÉMATIQUES - FIGURES GÉOMÉTRIQUES COMPLÈTES
    # ==============================
    
    def menu_maths(page):
        # ===== STATISTIQUES =====
        def statistiques():
            valeurs = []
            
            def ajouter_valeur(e):
                try:
                    val = float(valeur_field.value)
                    valeurs.append(val)
                    liste_valeurs.value = f"Valeurs: {valeurs}"
                    valeur_field.value = ""
                    page.update()
                except:
                    resultat.value = "Entrez un nombre valide"
                    page.update()
            
            def calculer_stats(e):
                if len(valeurs) == 0:
                    resultat.value = "Ajoutez des valeurs d'abord"
                    page.update()
                    return
                
                moyenne = sum(valeurs) / len(valeurs)
                minimum = min(valeurs)
                maximum = max(valeurs)
                valeurs_triees = sorted(valeurs)
                n = len(valeurs_triees)
                if n % 2 == 0:
                    mediane = (valeurs_triees[n//2 - 1] + valeurs_triees[n//2]) / 2
                else:
                    mediane = valeurs_triees[n//2]
                variance = sum((x - moyenne)**2 for x in valeurs) / n
                ecart_type = sqrt(variance)
                
                resultat.value = f"""
📊 Résultats:
Moyenne: {moyenne:.2f}
Médiane: {mediane:.2f}
Minimum: {minimum}
Maximum: {maximum}
Variance: {variance:.2f}
Écart-type: {ecart_type:.2f}
"""
                page.update()
            
            valeur_field = ft.TextField(label="Valeur", width=150)
            liste_valeurs = ft.Text("Valeurs: []", size=14)
            resultat = ft.Text("", size=14)
            
            page.clean()
            page.add(
                create_app_bar("Statistiques", lambda e: menu_maths(page)),
                ft.Column([
                    ft.Text("📊 Statistiques", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([valeur_field, ft.ElevatedButton("+ Ajouter", on_click=ajouter_valeur)]),
                    liste_valeurs,
                    ft.ElevatedButton("Calculer", on_click=calculer_stats),
                    resultat
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            )
        
        # ===== ÉQUATIONS =====
        def equations():
            def premier_degre():
                def calculer(e):
                    try:
                        a = float(a_field.value)
                        if a == 0:
                            resultat.value = "a doit être différent de 0"
                            page.update()
                            return
                        b = float(b_field.value)
                        x = -b / a
                        resultat.value = f"Solution: x = {x:.2f}"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                a_field = ft.TextField(label="a (ax + b = 0)", width=250)
                b_field = ft.TextField(label="b", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Équation 1er degré", lambda e: equations()),
                    ft.Column([a_field, b_field, ft.ElevatedButton("Résoudre", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def second_degre():
                def calculer(e):
                    try:
                        a = float(a_field.value)
                        if a == 0:
                            resultat.value = "a doit être différent de 0"
                            page.update()
                            return
                        b = float(b_field.value)
                        c = float(c_field.value)
                        D = b**2 - 4*a*c
                        
                        if D > 0:
                            x1 = (-b - sqrt(D)) / (2*a)
                            x2 = (-b + sqrt(D)) / (2*a)
                            resultat.value = f"Δ = {D:.2f}\nx1 = {x1:.2f}\nx2 = {x2:.2f}"
                        elif D == 0:
                            x0 = -b / (2*a)
                            resultat.value = f"Δ = 0\nSolution double: x0 = {x0:.2f}"
                        else:
                            resultat.value = f"Δ = {D:.2f}\nPas de solution réelle"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                a_field = ft.TextField(label="a (ax² + bx + c = 0)", width=250)
                b_field = ft.TextField(label="b", width=250)
                c_field = ft.TextField(label="c", width=250)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Équation 2nd degré", lambda e: equations()),
                    ft.Column([a_field, b_field, c_field, ft.ElevatedButton("Résoudre", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            page.clean()
            page.add(
                create_app_bar("Équations", lambda e: menu_maths(page)),
                ft.Column([
                    ft.Text("📐 Résolution d'équations", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Premier degré (ax + b = 0)", on_click=lambda e: premier_degre(), width=280),
                    ft.ElevatedButton("Second degré (ax² + bx + c = 0)", on_click=lambda e: second_degre(), width=280),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
            )
        
        # ===== FIGURES GÉOMÉTRIQUES (COMPLÈTES) =====
        def figures():
            def triangle():
                def calculer_perimetre(e):
                    try:
                        c1 = float(c1_field.value)
                        c2 = float(c2_field.value)
                        c3 = float(c3_field.value)
                        p = c1 + c2 + c3
                        resultat.value = f"Périmètre = {p:.2f} cm"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                def calculer_aire(e):
                    try:
                        base = float(base_field.value)
                        hauteur = float(hauteur_field.value)
                        aire = (base * hauteur) / 2
                        resultat.value = f"Aire = {aire:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                c1_field = ft.TextField(label="Côté 1 (cm)", width=200)
                c2_field = ft.TextField(label="Côté 2 (cm)", width=200)
                c3_field = ft.TextField(label="Côté 3 (cm)", width=200)
                base_field = ft.TextField(label="Base (cm)", width=200)
                hauteur_field = ft.TextField(label="Hauteur (cm)", width=200)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Triangle", lambda e: figures()),
                    ft.Column([
                        ft.Text("Triangle", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Périmètre:", weight=ft.FontWeight.BOLD),
                        c1_field, c2_field, c3_field,
                        ft.ElevatedButton("Calculer Périmètre", on_click=calculer_perimetre),
                        ft.Divider(),
                        ft.Text("Aire:", weight=ft.FontWeight.BOLD),
                        base_field, hauteur_field,
                        ft.ElevatedButton("Calculer Aire", on_click=calculer_aire),
                        resultat
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            
            def carre():
                def calculer(e):
                    try:
                        cote = float(cote_field.value)
                        if choix.value == "Périmètre":
                            resultat.value = f"Périmètre = {4 * cote:.2f} cm"
                        else:
                            resultat.value = f"Aire = {cote**2:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                cote_field = ft.TextField(label="Côté (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Périmètre"), ft.dropdown.Option("Aire")], value="Périmètre")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Carré", lambda e: figures()),
                    ft.Column([cote_field, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def rectangle():
                def calculer(e):
                    try:
                        L = float(longueur.value)
                        l = float(largeur.value)
                        if choix.value == "Périmètre":
                            resultat.value = f"Périmètre = {2 * (L + l):.2f} cm"
                        else:
                            resultat.value = f"Aire = {L * l:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                longueur = ft.TextField(label="Longueur (cm)", width=200)
                largeur = ft.TextField(label="Largeur (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Périmètre"), ft.dropdown.Option("Aire")], value="Périmètre")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Rectangle", lambda e: figures()),
                    ft.Column([longueur, largeur, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def cylindre():
                def calculer(e):
                    try:
                        r = float(rayon.value)
                        h = float(hauteur.value)
                        if choix.value == "Aire totale":
                            aire = 2 * math.pi * r * (r + h)
                            resultat.value = f"Aire totale = {aire:.2f} cm²"
                        else:
                            volume = math.pi * r**2 * h
                            resultat.value = f"Volume = {volume:.2f} cm³"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                rayon = ft.TextField(label="Rayon (cm)", width=200)
                hauteur = ft.TextField(label="Hauteur (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Aire totale"), ft.dropdown.Option("Volume")], value="Aire totale")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Cylindre", lambda e: figures()),
                    ft.Column([rayon, hauteur, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def cercle():
                def calculer(e):
                    try:
                        r = float(rayon.value)
                        if choix.value == "Périmètre":
                            resultat.value = f"Périmètre = {2 * math.pi * r:.2f} cm"
                        else:
                            resultat.value = f"Aire = {math.pi * r**2:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                rayon = ft.TextField(label="Rayon (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Périmètre"), ft.dropdown.Option("Aire")], value="Périmètre")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Cercle", lambda e: figures()),
                    ft.Column([rayon, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def trapeze():
                def calculer_perimetre(e):
                    try:
                        gb = float(gb_field.value)
                        pb = float(pb_field.value)
                        c1 = float(c1_field.value)
                        c2 = float(c2_field.value)
                        p = gb + pb + c1 + c2
                        resultat.value = f"Périmètre = {p:.2f} cm"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                def calculer_aire(e):
                    try:
                        gb = float(gb_field.value)
                        pb = float(pb_field.value)
                        h = float(h_field.value)
                        aire = ((gb + pb) * h) / 2
                        resultat.value = f"Aire = {aire:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                gb_field = ft.TextField(label="Grande base (cm)", width=200)
                pb_field = ft.TextField(label="Petite base (cm)", width=200)
                c1_field = ft.TextField(label="Côté 1 (cm)", width=200)
                c2_field = ft.TextField(label="Côté 2 (cm)", width=200)
                h_field = ft.TextField(label="Hauteur (cm)", width=200)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Trapèze", lambda e: figures()),
                    ft.Column([
                        ft.Text("Trapèze", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Périmètre:", weight=ft.FontWeight.BOLD),
                        gb_field, pb_field, c1_field, c2_field,
                        ft.ElevatedButton("Calculer Périmètre", on_click=calculer_perimetre),
                        ft.Divider(),
                        ft.Text("Aire:", weight=ft.FontWeight.BOLD),
                        gb_field, pb_field, h_field,
                        ft.ElevatedButton("Calculer Aire", on_click=calculer_aire),
                        resultat
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            
            def pavedroit():
                def calculer(e):
                    try:
                        L = float(longueur.value)
                        l = float(largeur.value)
                        h = float(hauteur.value)
                        if choix.value == "Aire totale":
                            aire = 2 * (L*l + L*h + l*h)
                            resultat.value = f"Aire totale = {aire:.2f} cm²"
                        else:
                            volume = L * l * h
                            resultat.value = f"Volume = {volume:.2f} cm³"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                longueur = ft.TextField(label="Longueur (cm)", width=200)
                largeur = ft.TextField(label="Largeur (cm)", width=200)
                hauteur = ft.TextField(label="Hauteur (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Aire totale"), ft.dropdown.Option("Volume")], value="Aire totale")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Pavé droit", lambda e: figures()),
                    ft.Column([longueur, largeur, hauteur, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def cube():
                def calculer(e):
                    try:
                        a = float(arete.value)
                        if choix.value == "Aire totale":
                            aire = 6 * a**2
                            resultat.value = f"Aire totale = {aire:.2f} cm²"
                        else:
                            volume = a**3
                            resultat.value = f"Volume = {volume:.2f} cm³"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                arete = ft.TextField(label="Arête (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Aire totale"), ft.dropdown.Option("Volume")], value="Aire totale")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Cube", lambda e: figures()),
                    ft.Column([arete, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def parallelogramme():
                def calculer_perimetre(e):
                    try:
                        base = float(base_field.value)
                        cote = float(cote_field.value)
                        p = 2 * (base + cote)
                        resultat.value = f"Périmètre = {p:.2f} cm"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                def calculer_aire(e):
                    try:
                        base = float(base_field.value)
                        hauteur = float(hauteur_field.value)
                        aire = base * hauteur
                        resultat.value = f"Aire = {aire:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                base_field = ft.TextField(label="Base (cm)", width=200)
                cote_field = ft.TextField(label="Côté (cm)", width=200)
                hauteur_field = ft.TextField(label="Hauteur (cm)", width=200)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Parallélogramme", lambda e: figures()),
                    ft.Column([
                        ft.Text("Parallélogramme", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Périmètre:", weight=ft.FontWeight.BOLD),
                        base_field, cote_field,
                        ft.ElevatedButton("Calculer Périmètre", on_click=calculer_perimetre),
                        ft.Divider(),
                        ft.Text("Aire:", weight=ft.FontWeight.BOLD),
                        base_field, hauteur_field,
                        ft.ElevatedButton("Calculer Aire", on_click=calculer_aire),
                        resultat
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            
            def losange():
                def calculer_perimetre(e):
                    try:
                        cote = float(cote_field.value)
                        p = 4 * cote
                        resultat.value = f"Périmètre = {p:.2f} cm"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                def calculer_aire(e):
                    try:
                        d1 = float(d1_field.value)
                        d2 = float(d2_field.value)
                        aire = (d1 * d2) / 2
                        resultat.value = f"Aire = {aire:.2f} cm²"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                cote_field = ft.TextField(label="Côté (cm)", width=200)
                d1_field = ft.TextField(label="Grande diagonale (cm)", width=200)
                d2_field = ft.TextField(label="Petite diagonale (cm)", width=200)
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Losange", lambda e: figures()),
                    ft.Column([
                        ft.Text("Losange", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Périmètre:", weight=ft.FontWeight.BOLD),
                        cote_field,
                        ft.ElevatedButton("Calculer Périmètre", on_click=calculer_perimetre),
                        ft.Divider(),
                        ft.Text("Aire:", weight=ft.FontWeight.BOLD),
                        d1_field, d2_field,
                        ft.ElevatedButton("Calculer Aire", on_click=calculer_aire),
                        resultat
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            
            def cone():
                def calculer(e):
                    try:
                        r = float(rayon.value)
                        if choix.value == "Aire totale":
                            g = float(generatrice.value)
                            aire = math.pi * r * (r + g)
                            resultat.value = f"Aire totale = {aire:.2f} cm²"
                        else:
                            h = float(hauteur.value)
                            volume = (math.pi * r**2 * h) / 3
                            resultat.value = f"Volume = {volume:.2f} cm³"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                rayon = ft.TextField(label="Rayon (cm)", width=200)
                generatrice = ft.TextField(label="Génératrice (cm)", width=200)
                hauteur = ft.TextField(label="Hauteur (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Aire totale"), ft.dropdown.Option("Volume")], value="Aire totale")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Cône", lambda e: figures()),
                    ft.Column([rayon, generatrice, hauteur, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            def sphere():
                def calculer(e):
                    try:
                        r = float(rayon.value)
                        if choix.value == "Aire":
                            aire = 4 * math.pi * r**2
                            resultat.value = f"Aire = {aire:.2f} cm²"
                        else:
                            volume = (4/3) * math.pi * r**3
                            resultat.value = f"Volume = {volume:.2f} cm³"
                        page.update()
                    except:
                        resultat.value = "Erreur: vérifiez les valeurs"
                        page.update()
                
                rayon = ft.TextField(label="Rayon (cm)", width=200)
                choix = ft.Dropdown(width=150, options=[ft.dropdown.Option("Aire"), ft.dropdown.Option("Volume")], value="Aire")
                resultat = ft.Text("", size=16)
                
                page.clean()
                page.add(
                    create_app_bar("Sphère", lambda e: figures()),
                    ft.Column([rayon, choix, ft.ElevatedButton("Calculer", on_click=calculer), resultat],
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                )
            
            page.clean()
            page.add(
                create_app_bar("Figures géométriques", lambda e: menu_maths(page)),
                ft.Column([
                    ft.Text("🔷 Figures géométriques", size=24, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("🔺 Triangle", on_click=lambda e: triangle(), width=250),
                    ft.ElevatedButton("⬛ Carré", on_click=lambda e: carre(), width=250),
                    ft.ElevatedButton("📏 Rectangle", on_click=lambda e: rectangle(), width=250),
                    ft.ElevatedButton("🟢 Cercle", on_click=lambda e: cercle(), width=250),
                    ft.ElevatedButton("🧴 Cylindre", on_click=lambda e: cylindre(), width=250),
                    ft.ElevatedButton("📐 Trapèze", on_click=lambda e: trapeze(), width=250),
                    ft.ElevatedButton("📦 Pavé droit", on_click=lambda e: pavedroit(), width=250),
                    ft.ElevatedButton("🧊 Cube", on_click=lambda e: cube(), width=250),
                    ft.ElevatedButton("🔷 Parallélogramme", on_click=lambda e: parallelogramme(), width=250),
                    ft.ElevatedButton("💎 Losange", on_click=lambda e: losange(), width=250),
                    ft.ElevatedButton("📐 Cône", on_click=lambda e: cone(), width=250),
                    ft.ElevatedButton("🌍 Sphère", on_click=lambda e: sphere(), width=250),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
            )
        
        page.clean()
        page.add(
            create_app_bar("Mathématiques", lambda e: accueil(page)),
            ft.Column([
                ft.Text("📐 Menu Mathématiques", size=28, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("📊 Statistiques", on_click=lambda e: statistiques(), width=280, height=50),
                ft.ElevatedButton("📐 Résolution d'équations", on_click=lambda e: equations(), width=280, height=50),
                ft.ElevatedButton("🔷 Figures géométriques", on_click=lambda e: figures(), width=280, height=50),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
        )
    
    # ==============================
    # ACCUEIL
    # ==============================
    def accueil(page):
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("🧪 Science en une App 🧬", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(SUBTITLE, size=20, color=ft.Colors.WHITE70),
                    ft.Divider(color=ft.Colors.WHITE54),
                    ft.Text("Choisissez une matière :", size=18, color=ft.Colors.WHITE),
                    ft.ElevatedButton("📐 Mathématique", on_click=lambda e: menu_maths(page), width=250, height=50),
                    ft.ElevatedButton("⚡ Physique", on_click=lambda e: menu_physique(page), width=250, height=50),
                    ft.ElevatedButton("🧪 Chimie", on_click=lambda e: menu_chimie(page), width=250, height=50),
                    ft.ElevatedButton("🎮 Jeux", on_click=lambda e: menu_jeux(page), width=250, height=50),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.Colors.BLUE_800, ft.Colors.PURPLE_800]
                )
            )
        )
    
    # Démarrer l'application
    accueil(page)

ft.app(target=main)