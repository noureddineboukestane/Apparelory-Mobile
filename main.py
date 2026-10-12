import flet as ft
import sqlite3
import traceback
import time
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

LANGS = {
    "fr": {
        "app_title": "Apparelory Pro", "stats": "Stats", "stock": "Stock", "fourn": "Fournisseurs", "histo": "Histo", "settings": "Paramètres",
        "valeur": "Valeur", "total_pcs": "Total Pièces", "alertes": "Alertes", "notif": "Notifications 🚨", "tout_ok": "Tout est parfait! ✅",
        "reste": "Reste", "seuil": "Seuil", "pcs": "pcs", "add_fourn": "Nouveau Fournisseur", "nom_f": "Nom du représentant", "entreprise": "Nom de l'entreprise", "contact": "Téléphone/Email",
        "save": "Enregistrer", "fourn_added": "Fournisseur ajouté! ✨", "my_stock": "Mon Stock 📦", "add_art": "Nouveau Article",
        "desig": "Désignation", "qte": "Qté", "prix_u": "Prix Unitaire", "prix_v": "Prix de Vente", "client_nom": "Nom du Client", "client_adr": "Adresse du Client",
        "in": "ENTRÉE", "out": "VENTE (SORTIE)", "delete": "SUPPRIMER", "valider": "Valider", "histo_title": "Historique 🕒", "lang": "Langue", "devise": "Devise",
        "dark_mode": "Mode Sombre", "about_us": "À propos de nous", "about_desc": "Apparelory Pro v1.0\nApplication de gestion de stock intelligente.\n© 2026 Apparelory.",
        "save_param": "Sauvegarder", "param_saved": "Paramètres modifiés! 🔄", "facture_title": "🧾 Facture de Vente", "total": "Total", "pdf_success": "PDF Téléchargé avec succès! 📄"
    },
    "ar": {
        "app_title": "Apparelory برو", "stats": "إحصائيات", "stock": "المخزون", "fourn": "الموردين", "histo": "السجل", "settings": "إعدادات",
        "valeur": "القيمة", "total_pcs": "مجموع القطع", "alertes": "تنبيهات", "notif": "إشعارات المخزون 🚨", "tout_ok": "كل شيء مثالي! ✅",
        "reste": "متبقي", "seuil": "الحد الأدنى", "pcs": "قطع", "add_fourn": "مورد جديد", "nom_f": "اسم الممثل", "entreprise": "اسم الشركة", "contact": "الهاتف / البريد",
        "save": "حفظ", "fourn_added": "تمت الإضافة بنجاح! ✨", "my_stock": "مخزوني 📦", "add_art": "منتج جديد",
        "desig": "الاسم", "qte": "الكمية", "prix_u": "ثمن الوحدة", "prix_v": "ثمن البيع", "client_nom": "اسم الزبون", "client_adr": "عنوان الزبون",
        "in": "إدخال", "out": "بيع (إخراج)", "delete": "حذف", "valider": "تأكيد", "histo_title": "السجل 🕒", "lang": "اللغة", "devise": "العملة",
        "dark_mode": "الوضع الليلي", "about_us": "حول التطبيق", "about_desc": "Apparelory برو v1.0\nتطبيق ذكي لإدارة المخزون.\n© 2026 Apparelory.",
        "save_param": "حفظ الإعدادات", "param_saved": "تم تحديث الإعدادات! 🔄", "facture_title": "🧾 فاتورة البيع", "total": "المجموع", "pdf_success": "تم تحميل الفاتورة PDF! 📄"
    },
    "en": {
        "app_title": "Apparelory Pro", "stats": "Stats", "stock": "Stock", "fourn": "Suppliers", "histo": "History", "settings": "Settings",
        "valeur": "Value", "total_pcs": "Total Items", "alertes": "Alerts", "notif": "Notifications 🚨", "tout_ok": "Everything is fine! ✅",
        "reste": "Left", "seuil": "Threshold", "pcs": "pcs", "add_fourn": "New Supplier", "nom_f": "Representative Name", "entreprise": "Company Name", "contact": "Phone/Email",
        "save": "Save", "fourn_added": "Supplier added! ✨", "my_stock": "My Stock 📦", "add_art": "New Item",
        "desig": "Designation", "qte": "Qty", "prix_u": "Unit Price", "prix_v": "Selling Price", "client_nom": "Customer Name", "client_adr": "Customer Address",
        "in": "IN", "out": "SALE (OUT)", "delete": "DELETE", "valider": "Confirm", "histo_title": "History 🕒", "lang": "Language", "devise": "Currency",
        "dark_mode": "Dark Mode", "about_us": "About Us", "about_desc": "Apparelory Pro v1.0\nSmart inventory management app.\n© 2026 Apparelory.",
        "save_param": "Save Settings", "param_saved": "Settings updated! 🔄", "facture_title": "🧾 Sales Invoice", "total": "Total", "pdf_success": "PDF Downloaded! 📄"
    }
}

DB_NAME = 'apparelory_v3.db' 

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS parametres')
    cursor.execute('''CREATE TABLE parametres (id INTEGER PRIMARY KEY CHECK (id = 1), langue TEXT DEFAULT 'fr', devise TEXT DEFAULT 'DH', theme TEXT DEFAULT 'LIGHT')''')
    cursor.execute('INSERT INTO parametres (id, langue, devise, theme) VALUES (1, "fr", "DH", "LIGHT")')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fournisseurs (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, entreprise TEXT, contact TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY AUTOINCREMENT, designation TEXT NOT NULL, fournisseur_id INTEGER, quantite INTEGER NOT NULL, seuil INTEGER NOT NULL, cmup REAL NOT NULL, FOREIGN KEY(fournisseur_id) REFERENCES fournisseurs(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS mouvements (id INTEGER PRIMARY KEY AUTOINCREMENT, article_id INTEGER, type_mvt TEXT, quantite INTEGER, prix_unitaire REAL, date_mouvement DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(article_id) REFERENCES articles(id))''')
    try: cursor.execute("ALTER TABLE fournisseurs ADD COLUMN entreprise TEXT")
    except: pass
    conn.commit()
    conn.close()

def run_query(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

def fetch_query(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_params():
    try:
        res = fetch_query('SELECT langue, devise, theme FROM parametres WHERE id = 1')
        if res: return res[0][0], res[0][1], res[0][2]
    except: pass
    return "fr", "DH", "LIGHT"

def generer_facture_pdf(nom_client, adr_client, article, qte, prix_u, total, devise):
    os.makedirs("factures", exist_ok=True)
    filename = f"factures/facture_{int(time.time())}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, "APPARELORY PRO - FACTURE")
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Date: {time.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, 670, f"Client: {nom_client}")
    c.drawString(50, 650, f"Adresse: {adr_client}")
    c.line(50, 630, 550, 630)
    c.drawString(50, 600, f"Article: {article}")
    c.drawString(50, 580, f"Quantité: {qte}")
    c.drawString(50, 560, f"Prix Unitaire: {prix_u} {devise}")
    c.line(50, 540, 550, 540)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 510, f"Total à payer: {total} {devise}")
    c.save()
    return filename

def main(page: ft.Page):
    try:
        init_db()
        page.title = "Apparelory Pro"
        
        try:
            page.window.width = 450
            page.window.height = 800
        except AttributeError:
            page.window_width = 450
            page.window_height = 800
            
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#121212"
        
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(
            ft.Image(src="logo.png", width=250, fit="contain")
        )
        page.update()
        time.sleep(2) 
        page.clean() 
        
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        
        active_page_index = 0

        def build_app(active_tab_index=0):
            nonlocal active_page_index
            active_page_index = active_tab_index
            page.clean()
            
            curr_lang, curr_dev, curr_theme = get_params()
            t = LANGS.get(curr_lang, LANGS['fr'])
            is_dark = (curr_theme == 'DARK')
            
            page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
            page.bgcolor = "#121212" if is_dark else "#F4F6F9"
            
            page.appbar = ft.AppBar(
                title=ft.Image(src="logo.png", height=40, fit="contain"),
                center_title=True,
                bgcolor=ft.colors.BLACK
            )

            vue_dashboard = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
            vue_fournisseurs = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
            vue_stock = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
            vue_historique = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
            vue_parametres = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)

            liste_fournisseurs = ft.ListView(expand=True, spacing=10)
            def charger_fournisseurs():
                liste_fournisseurs.controls.clear()
                for f in fetch_query('SELECT id, nom, entreprise, contact FROM fournisseurs'):
                    f_id, nom, entreprise, contact = f
                    ent_str = f"🏢 {entreprise} | " if entreprise else ""
                    liste_fournisseurs.controls.append(
                        ft.Card(
                            elevation=2,
                            content=ft.ListTile(
                                leading=ft.CircleAvatar(content=ft.Icon(ft.icons.BUSINESS, color=ft.colors.WHITE), bgcolor=ft.colors.AMBER_700),
                                title=ft.Text(f"{nom}", weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"{ent_str}{contact}"),
                                trailing=ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED, on_click=lambda e, i=f_id: run_query('DELETE FROM fournisseurs WHERE id = ?', (i,)) or charger_fournisseurs() or page.update())
                            )
                        )
                    )
                page.update()

            nom_f_input = ft.TextField(label=t['nom_f'], border_radius=10)
            ent_f_input = ft.TextField(label=t['entreprise'], border_radius=10)
            contact_f_input = ft.TextField(label=t['contact'], border_radius=10)
            
            def ajouter_fournisseur(e):
                if nom_f_input.value:
                    run_query('INSERT INTO fournisseurs (nom, entreprise, contact) VALUES (?, ?, ?)', (nom_f_input.value, ent_f_input.value, contact_f_input.value))
                    nom_f_input.value, ent_f_input.value, contact_f_input.value = "", "", ""
                    charger_fournisseurs()
                    page.snack_bar = ft.SnackBar(ft.Text(t['fourn_added']), bgcolor=ft.colors.GREEN_600)
                    page.snack_bar.open = True
                    page.update()

            vue_fournisseurs.controls.extend([
                ft.Text(t['add_fourn'], size=20, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400 if is_dark else ft.colors.BLUE_GREY_900),
                ft.Column([nom_f_input, ent_f_input, contact_f_input]),
                ft.ElevatedButton(t['save'], on_click=ajouter_fournisseur, bgcolor=ft.colors.AMBER_600, color=ft.colors.BLACK, width=400, height=45),
                ft.Divider(),
                liste_fournisseurs
            ])

            liste_articles = ft.ListView(expand=True, spacing=15)
            def charger_stock():
                liste_articles.controls.clear()
                articles = fetch_query('SELECT a.id, a.designation, f.entreprise, f.nom, a.quantite, a.seuil, a.cmup FROM articles a LEFT JOIN fournisseurs f ON a.fournisseur_id = f.id')
                for art in articles:
                    a_id, desig, f_ent, f_nom, qte, seuil, cmup = art
                    fourn_display = f_ent if f_ent else (f_nom if f_nom else "---")
                    is_alert = qte <= seuil
                    
                    def mvt_stock(e, i=a_id, type_m="ENTREE", q_act=qte, c_act=cmup, article_nom=desig):
                        q_input = ft.TextField(label=t['qte'], keyboard_type=ft.KeyboardType.NUMBER)
                        p_input = ft.TextField(label=t['prix_u'] if type_m=="ENTREE" else t['prix_v'], keyboard_type=ft.KeyboardType.NUMBER)
                        client_name_input = ft.TextField(label=t['client_nom'], visible=(type_m=="SORTIE"))
                        client_adr_input = ft.TextField(label=t['client_adr'], visible=(type_m=="SORTIE"))
                        
                        def valider(e):
                            val_q = int(q_input.value) if q_input.value and q_input.value.isdigit() else 0
                            if val_q > 0:
                                val_p = float(p_input.value) if p_input.value else c_act
                                page.dialog.open = False
                                page.update()
                                if type_m == "ENTREE":
                                    nv_cmup = ((q_act * c_act) + (val_q * val_p)) / (q_act + val_q) if (q_act + val_q) > 0 else val_p
                                    run_query('UPDATE articles SET quantite = quantite + ?, cmup = ? WHERE id = ?', (val_q, nv_cmup, i))
                                    run_query('INSERT INTO mouvements (article_id, type_mvt, quantite, prix_unitaire) VALUES (?, ?, ?, ?)', (i, type_m, val_q, val_p))
                                    build_app(active_tab_index=1)
                                else:
                                    if val_q > q_act:
                                        page.snack_bar = ft.SnackBar(ft.Text("⚠️ Stock insuffisant !"), bgcolor=ft.colors.RED)
                                        page.snack_bar.open = True
                                        page.update()
                                        return
                                    run_query('UPDATE articles SET quantite = quantite - ? WHERE id = ?', (val_q, i))
                                    run_query('INSERT INTO mouvements (article_id, type_mvt, quantite, prix_unitaire) VALUES (?, ?, ?, ?)', (i, "SORTIE", val_q, val_p))
                                    total_vente = val_q * val_p
                                    generer_facture_pdf(client_name_input.value or "Anonyme", client_adr_input.value or "Marrakech", article_nom, val_q, val_p, total_vente, curr_dev)
                                    page.snack_bar = ft.SnackBar(ft.Text(t['pdf_success']), bgcolor=ft.colors.GREEN_600)
                                    page.snack_bar.open = True
                                    build_app(active_tab_index=1)

                        page.dialog = ft.AlertDialog(title=ft.Text(t['in'] if type_m=="ENTREE" else t['out']), content=ft.Column([client_name_input, client_adr_input, q_input, p_input], tight=True), actions=[ft.ElevatedButton(t['valider'], on_click=valider, bgcolor=ft.colors.AMBER_600, color=ft.colors.BLACK)])
                        page.dialog.open = True
                        page.update()

                    liste_articles.controls.append(
                        ft.Card(
                            elevation=3,
                            color=ft.colors.SURFACE,
                            shape=ft.RoundedRectangleBorder(radius=15),
                            content=ft.Container(
                                padding=15,
                                border=ft.border.all(1.5, ft.colors.RED_300 if is_alert else ft.colors.TRANSPARENT),
                                border_radius=15,
                                content=ft.Column([
                                    ft.Row([ft.Icon(ft.icons.LOCAL_MALL, color=ft.colors.RED_500 if is_alert else ft.colors.AMBER_600), ft.Text(desig, weight=ft.FontWeight.BOLD, size=18, expand=True), ft.Text(f"{qte} {t['pcs']}", weight=ft.FontWeight.W_900, size=20, color=ft.colors.RED_600 if is_alert else ft.colors.GREEN_500)]),
                                    ft.Text(f"{t['fourn']}: {fourn_display} | CMUP: {cmup:.2f} {curr_dev}\n{t['seuil']}: {seuil}", size=13),
                                    ft.Divider(height=10),
                                    ft.Row([
                                        ft.TextButton(t['delete'], icon=ft.icons.DELETE, icon_color=ft.colors.RED, style=ft.ButtonStyle(color=ft.colors.RED), on_click=lambda e, i=a_id: run_query('DELETE FROM articles WHERE id = ?', (i,)) or build_app(active_tab_index=1)),
                                        ft.Container(expand=True),
                                        ft.IconButton(ft.icons.REMOVE_CIRCLE, icon_color=ft.colors.ORANGE, icon_size=35, on_click=lambda e, i=a_id, q=qte, c=cmup, d=desig: mvt_stock(e, i, "SORTIE", q, c, d)),
                                        ft.IconButton(ft.icons.ADD_CIRCLE, icon_color=ft.colors.GREEN_500, icon_size=35, on_click=lambda e, i=a_id, q=qte, c=cmup, d=desig: mvt_stock(e, i, "ENTREE", q, c, d)),
                                    ])
                                ])
                            )
                        )
                    )
                page.update()

            vue_stock.controls.extend([ft.Text(t['my_stock'], size=24, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400 if is_dark else ft.colors.BLUE_GREY_900), liste_articles])

            kpi_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=15)
            alertes_col = ft.Column(spacing=10)
            def charger_dashboard():
                kpi_row.controls.clear()
                alertes_col.controls.clear()
                articles = fetch_query('SELECT designation, quantite, seuil, cmup FROM articles')
                valeur_stock = sum([a[1] * a[3] for a in articles]) if articles else 0
                alertes = [a for a in articles if a[1] <= a[2]]
                
                def add_kpi(titre, val, icon, color):
                    kpi_row.controls.append(ft.Card(elevation=2, color=ft.colors.SURFACE, content=ft.Container(content=ft.Column([ft.Icon(icon, color=color, size=30), ft.Text(titre, size=12), ft.Text(val, size=20, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER), padding=15, width=140)))
                
                add_kpi(f"{t['valeur']} ({curr_dev})", f"{valeur_stock:,.0f}", ft.icons.ACCOUNT_BALANCE_WALLET, ft.colors.GREEN_500)
                add_kpi(t['total_pcs'], str(sum([a[1] for a in articles]) if articles else 0), ft.icons.CHECKROOM, ft.colors.AMBER_600)
                add_kpi(t['alertes'], str(len(alertes)), ft.icons.WARNING_ROUNDED, ft.colors.RED_500)
                
                alertes_col.controls.append(ft.Text(t['notif'], size=18, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400 if is_dark else ft.colors.BLUE_GREY_900))
                if alertes:
                    for a in alertes: alertes_col.controls.append(ft.Card(color=ft.colors.RED_900 if is_dark else ft.colors.RED_50, content=ft.ListTile(leading=ft.Icon(ft.icons.ERROR, color=ft.colors.RED_300 if is_dark else ft.colors.RED), title=ft.Text(a[0], weight=ft.FontWeight.BOLD), subtitle=ft.Text(f"{t['reste']} : {a[1]} {t['pcs']} ({t['seuil']} : {a[2]})"))))
                else:
                    alertes_col.controls.append(ft.Text(t['tout_ok'], color=ft.colors.GREEN_400 if is_dark else ft.colors.GREEN, weight=ft.FontWeight.BOLD))
                page.update()
            
            vue_dashboard.controls.extend([kpi_row, ft.Container(height=20), alertes_col])

            liste_historique = ft.ListView(expand=True, spacing=10)
            def charger_historique():
                liste_historique.controls.clear()
                for m in fetch_query('SELECT m.type_mvt, m.quantite, m.prix_unitaire, m.date_mouvement, a.designation FROM mouvements m JOIN articles a ON m.article_id = a.id ORDER BY m.id DESC LIMIT 30'):
                    t_mvt, q, p, d, desig = m
                    clr, icn, txt = (ft.colors.GREEN_600, ft.icons.ADD, t['in']) if t_mvt == "ENTREE" else (ft.colors.ORANGE_600, ft.icons.REMOVE, t['out'])
                    liste_historique.controls.append(ft.ListTile(leading=ft.CircleAvatar(content=ft.Icon(icn, color=ft.colors.WHITE), bgcolor=clr), title=ft.Text(desig, weight=ft.FontWeight.BOLD), subtitle=ft.Text(f"{txt}: {q} {t['pcs']} | {p} {curr_dev}\n{d[:16]}")))
                page.update()
            
            vue_historique.controls.extend([ft.Text(t['histo_title'], size=24, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400 if is_dark else ft.colors.BLUE_GREY_900), liste_historique])

            langue_dd = ft.Dropdown(label=t['lang'], options=[ft.dropdown.Option(key="fr", text="Français"), ft.dropdown.Option(key="en", text="English"), ft.dropdown.Option(key="ar", text="العربية")], value=curr_lang, border_radius=10)
            devise_dd = ft.Dropdown(label=t['devise'], options=[ft.dropdown.Option(key="DH", text="Dirham (DH)"), ft.dropdown.Option(key="€", text="Euro (€)"), ft.dropdown.Option(key="$", text="Dollar ($)")], value=curr_dev, border_radius=10)
            theme_switch = ft.Switch(label=t['dark_mode'], value=is_dark)

            def save_parametres(e):
                run_query('UPDATE parametres SET langue = ?, devise = ?, theme = ? WHERE id = 1', (langue_dd.value, devise_dd.value, 'DARK' if theme_switch.value else 'LIGHT'))
                page.snack_bar = ft.SnackBar(ft.Text("✅ " + t['param_saved']), bgcolor=ft.colors.GREEN_600)
                page.snack_bar.open = True
                build_app(4)
            
            def show_about(e):
                page.dialog = ft.AlertDialog(
                    title=ft.Image(src="logo.png", height=40),
                    content=ft.Text(t['about_desc'], text_align="center"),
                    actions=[ft.TextButton("OK", on_click=lambda ev: setattr(page.dialog, 'open', False) or page.update())]
                )
                page.dialog.open = True
                page.update()
                
            btn_about = ft.TextButton(t['about_us'], icon=ft.icons.INFO, on_click=show_about)
            
            vue_parametres.controls.extend([
                ft.Text(f"{t['settings']} ⚙️", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.AMBER_400 if is_dark else ft.colors.BLUE_GREY_900),
                ft.Card(color=ft.colors.SURFACE, elevation=2, content=ft.Container(padding=20, content=ft.Column([langue_dd, devise_dd, ft.Container(height=10), theme_switch, ft.Container(height=15), ft.ElevatedButton(t['save_param'], on_click=save_parametres, bgcolor=ft.colors.AMBER_600, color=ft.colors.BLACK, width=400, height=45), ft.Divider(height=30), ft.Row([btn_about], alignment="center")])))
            ])

            main_container = ft.Container(content=None, expand=True, padding=15)

            def open_add_article(e):
                f_list = fetch_query('SELECT id, nom, entreprise FROM fournisseurs')
                if not f_list:
                    page.snack_bar = ft.SnackBar(ft.Text("⚠️ أضف مورد (Fournisseur) أولاً!"), bgcolor=ft.colors.RED)
                    page.snack_bar.open = True
                    page.update()
                    return

                d_input = ft.TextField(label=t['desig'])
                f_dropdown = ft.Dropdown(label=t['fourn'], options=[ft.dropdown.Option(key=str(f[0]), text=f"{f[1]} ({f[2]})" if f[2] else f[1]) for f in f_list])
                q_input = ft.TextField(label=t['qte'], keyboard_type=ft.KeyboardType.NUMBER)
                s_input = ft.TextField(label=t['seuil'], keyboard_type=ft.KeyboardType.NUMBER)
                p_input = ft.TextField(label=t['prix_u'], keyboard_type=ft.KeyboardType.NUMBER)

                def save_art(e):
                    if d_input.value and f_dropdown.value and q_input.value and s_input.value and p_input.value:
                        try:
                            # 1. بلوكاج الزر باش ميتكليكاش جوج مرات
                            e.control.disabled = True
                            page.update()

                            fourn_id = int(f_dropdown.value)
                            qte_val = int(q_input.value)
                            seuil_val = int(s_input.value)
                            prix_val = float(p_input.value)
                            
                            # 2. سدان النافذة وتحديث الشاشة فالبلاصة باش متشوفهاش باقة محلولة
                            page.dialog.open = False
                            page.update()

                            last_id = run_query(
                                'INSERT INTO articles (designation, fournisseur_id, quantite, seuil, cmup) VALUES (?, ?, ?, ?, ?)', 
                                (d_input.value, fourn_id, qte_val, seuil_val, prix_val)
                            )
                            run_query(
                                'INSERT INTO mouvements (article_id, type_mvt, quantite, prix_unitaire) VALUES (?, ?, ?, ?)', 
                                (last_id, "ENTREE", qte_val, prix_val)
                            )
                            build_app(active_tab_index=1)
                        except Exception as ex:
                            print("🚨 خطأ فـ حفظ المنتج:", ex)

                page.dialog = ft.AlertDialog(title=ft.Text(t['add_art']), content=ft.Column([d_input, f_dropdown, q_input, s_input, p_input], tight=True), actions=[ft.ElevatedButton(t['save'], on_click=save_art, bgcolor=ft.colors.AMBER_600, color=ft.colors.BLACK)])
                page.dialog.open = True
                page.update()

            fab_add = ft.FloatingActionButton(icon=ft.icons.ADD, bgcolor=ft.colors.AMBER_600, on_click=open_add_article, visible=False)
            page.floating_action_button = fab_add

            vues = [vue_dashboard, vue_stock, vue_fournisseurs, vue_historique, vue_parametres]
            def changer_vue(e): build_app(active_tab_index=e.control.selected_index)

            page.navigation_bar = ft.NavigationBar(
                selected_index=active_page_index,
                destinations=[
                    ft.NavigationDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD, label=t['stats']),
                    ft.NavigationDestination(icon=ft.icons.INVENTORY_2_OUTLINED, selected_icon=ft.icons.INVENTORY_2, label=t['stock']),
                    ft.NavigationDestination(icon=ft.icons.BUSINESS_OUTLINED, selected_icon=ft.icons.BUSINESS, label=t['fourn']),
                    ft.NavigationDestination(icon=ft.icons.HISTORY_OUTLINED, selected_icon=ft.icons.HISTORY, label=t['histo']),
                    ft.NavigationDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label=t['settings']),
                ],
                on_change=changer_vue,
            )

            main_container.content = vues[active_page_index]
            fab_add.visible = (active_page_index == 1)
            page.add(main_container)

            if active_page_index == 0: charger_dashboard()
            elif active_page_index == 1: charger_stock()
            elif active_page_index == 2: charger_fournisseurs()
            elif active_page_index == 3: charger_historique()
            page.update()

        build_app(active_tab_index=0)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    try:
        ft.app(target=main, assets_dir=".")
    except AttributeError:
        ft.run(main)