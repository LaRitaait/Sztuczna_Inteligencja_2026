# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import random

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import algorytm_harmoniczny as ah
import generator


class HarmonyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Harmony Loading System - Symulacja załadunku na żywo")
        # Poszerzamy okno, żeby zmieścić vana u góry
        self.root.geometry("1100x750")

        self.dziala = False
        self.kolejka_danych = queue.Queue()

        # Rozdzielamy historię na wszystkie dane i tylko te poprawne
        self.historia_x = []
        self.historia_y = []
        self.historia_x_dodatnie = []
        self.historia_y_dodatnie = []

        self.panel_lewy = ttk.Frame(self.root, width=320, padding=10)
        self.panel_lewy.pack(side=tk.LEFT, fill=tk.Y)

        # Panel główny z vanem i wykresami
        self.panel_glowny = ttk.Frame(self.root, padding=10)
        self.panel_glowny.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- PANEL PARAMETRÓW ---
        frame_parametry = ttk.LabelFrame(self.panel_lewy, text="Parametry Algorytmu", padding=5)
        frame_parametry.pack(fill=tk.X, pady=5)

        self.v_ni = tk.IntVar(value=100000)
        self.v_hms = tk.IntVar(value=20)
        self.v_hmcr = tk.DoubleVar(value=0.85)
        self.v_par = tk.DoubleVar(value=0.10)
        self.v_max_weight = tk.DoubleVar(value=1500.0)
        self.v_max_volume = tk.DoubleVar(value=2500000.0)
        self.v_min_pack = tk.IntVar(value=10)
        self.v_max_pack = tk.IntVar(value=50)
        self.v_odswiezanie = tk.IntVar(value=1000)

        pola = [
            ("Liczba Iteracji:", self.v_ni),
            ("Pamięć Harmonii (HMS):", self.v_hms),
            ("Prawdopod. Pamięci (HMCR):", self.v_hmcr),
            ("Dostrojenie (PAR):", self.v_par),
            ("Max Waga (kg):", self.v_max_weight),
            ("Max Objętość (cm3):", self.v_max_volume),
            ("Min Liczba Paczek:", self.v_min_pack),
            ("Max Liczba Paczek:", self.v_max_pack),
            ("Odświeżanie (co X iter):", self.v_odswiezanie)
        ]

        for i, (etykieta, zmienna) in enumerate(pola):
            ttk.Label(frame_parametry, text=etykieta).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Entry(frame_parametry, textvariable=zmienna, width=10).grid(row=i, column=1, pady=2, padx=5)

        ttk.Button(self.panel_lewy, text="1. Generuj Realistyczne Dane (100k)", command=self.generuj_dane).pack(
            fill=tk.X, pady=10)
        self.btn_uruchom = ttk.Button(self.panel_lewy, text="2. Uruchom Algorytm", command=self.uruchom_w_tle)
        self.btn_uruchom.pack(fill=tk.X, pady=5)

        self.label_status = ttk.Label(self.panel_lewy, text="Gotowy", font=("Arial", 10, "bold"), foreground="green")
        self.label_status.pack(pady=5)

        self.text_wynik = tk.Text(self.panel_lewy, width=35, height=15, state=tk.DISABLED)
        self.text_wynik.pack(fill=tk.BOTH, expand=True)

        # --- PODZIAŁ PANELA GŁÓWNEGO ---

        # 1. Van u góry
        frame_van = ttk.LabelFrame(self.panel_glowny, text="Wizualizacja Van (50 slotów)", padding=5)
        frame_van.pack(fill=tk.X, pady=5)

        self.van_canvas = tk.Canvas(frame_van, width=700, height=200, bg='white', highlightthickness=1)
        self.van_canvas.pack(fill=tk.X)
        self.rysuj_podstawowego_vana()  # Stan początkowy

        # 2. Wykresy u dołu
        frame_wykresy = ttk.Frame(self.panel_glowny)
        frame_wykresy.pack(fill=tk.BOTH, expand=True, pady=5)

        self.figura = Figure(figsize=(8, 4), dpi=100)

        # Wykres 1: Cała historia (Lewy)
        self.os_wykresu_1 = self.figura.add_subplot(121)
        self.os_wykresu_1.set_title("Eksploracja (Kary)")
        self.linia_wykresu_1, = self.os_wykresu_1.plot([], [], color='blue', linewidth=2)

        # Wykres 2: Tylko poprawne (Prawy)
        self.os_wykresu_2 = self.figura.add_subplot(122)
        self.os_wykresu_2.set_title("Optymalizacja (Tylko legalne)")
        self.linia_wykresu_2, = self.os_wykresu_2.plot([], [], color='green', linewidth=2)

        self.figura.tight_layout()
        self.plot_canvas = FigureCanvasTkAgg(self.figura, frame_wykresy)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def rysuj_podstawowego_vana(self):
        """Rysuje pustego vana jako bazę."""
        self.van_canvas.delete("all")
        # Kabina
        self.van_canvas.create_polygon(50, 50, 150, 50, 170, 100, 150, 150, 50, 150, fill="gray90", outline="black")
        self.van_canvas.create_rectangle(70, 60, 130, 90, fill="skyblue")  # Szyba
        # Paka
        self.van_canvas.create_rectangle(170, 40, 650, 160, fill="gray95", outline="black")
        self.van_canvas.create_oval(100, 140, 140, 180, fill="black")  # Koło 1
        self.van_canvas.create_oval(580, 140, 620, 180, fill="black")  # Koło 2

    def generuj_dane(self):
        self.label_status.config(text="Generowanie danych...", foreground="blue")
        self.root.update()
        generator.generuj_dane()
        self.label_status.config(text="Wygenerowano paczki!", foreground="green")
        messagebox.showinfo("Sukces", "Wygenerowano 100 000 realistycznych paczek.")

    def uruchom_w_tle(self):
        self.btn_uruchom.config(state=tk.DISABLED)
        self.label_status.config(text="Obliczenia trwają...", foreground="red")

        self.dziala = True
        self.historia_x.clear()
        self.historia_y.clear()
        self.historia_x_dodatnie.clear()
        self.historia_y_dodatnie.clear()

        while not self.kolejka_danych.empty():
            self.kolejka_danych.get_nowait()

        # Przygotowanie osi
        self.os_wykresu_1.clear()
        self.os_wykresu_1.set_title("Eksploracja (Kary)")
        self.os_wykresu_1.set_yscale('symlog', linthresh=100)
        self.linia_wykresu_1, = self.os_wykresu_1.plot([], [], color='blue', linewidth=2)
        self.os_wykresu_1.set_ylabel("Fitness")

        self.os_wykresu_2.clear()
        self.os_wykresu_2.set_title("Lupa: Faza końcowa (>1450)")
        self.os_wykresu_2.set_ylabel("Waga załadowana")
        self.os_wykresu_2.set_ylim(1450, 1510)
        self.linia_wykresu_2, = self.os_wykresu_2.plot([], [], color='green', linewidth=2)

        self.figura.tight_layout()
        self.plot_canvas.draw()

        self.root.after(100, self.aktualizuj_wykres)
        thread = threading.Thread(target=self.wykonaj_algorytm)
        thread.start()

    def aktualizuj_wykres(self):
        czy_nowe_dane = False
        fit, najlepsze_id = 0, 0

        while not self.kolejka_danych.empty():
            # Zmieniliśmy dane z kolejki, wpuszczamy cały najlepszy wektor do vana!
            it, fit, wektor_id = self.kolejka_danych.get_nowait()
            self.historia_x.append(it)
            self.historia_y.append(fit)
            najlepsze_id = wektor_id

            if fit >= 1450:
                self.historia_x_dodatnie.append(it)
                self.historia_y_dodatnie.append(fit)

            czy_nowe_dane = True

        if czy_nowe_dane:
            # 1. Rysowanie dynamicznych wykresów
            self.linia_wykresu_1.set_data(self.historia_x, self.historia_y)
            obecny_max_x = max(self.historia_x)
            self.os_wykresu_1.set_xlim(0, obecny_max_x + (obecny_max_x * 0.05) if obecny_max_x > 0 else 1000)
            self.os_wykresu_1.set_ylim(min(self.historia_y), 1550)

            if self.historia_x_dodatnie:
                self.linia_wykresu_2.set_data(self.historia_x_dodatnie, self.historia_y_dodatnie)
                poczatek_x = self.historia_x_dodatnie[0]
                self.os_wykresu_2.set_xlim(poczatek_x, obecny_max_x + (
                            obecny_max_x * 0.05) if obecny_max_x > poczatek_x else poczatek_x + 100)

            self.plot_canvas.draw()

            # 2. Wizualizacja Vana na podstawie danych
            if fit > 0:
                self.wizualizuj_zapekniomy_van(najlepsze_id, fit)
            else:
                self.wizualizuj_przeladowany_van(fit)

        if self.dziala or not self.kolejka_danych.empty():
            self.root.after(100, self.aktualizuj_wykres)
        else:
            if hasattr(self, 'najlepsze_tymczasowe'):
                self.pokaz_wyniki(self.najlepsze_tymczasowe)

    def wizualizuj_zapekniomy_van(self, wektor_id, fit):
        """Zapełnia vana paczkami na podstawie ID."""
        self.van_canvas.delete("paczka")
        paka_x_start, paka_y_start, paka_width, paka_height = 175, 45, 470, 110
        paczka_width = paka_width / 50  # 50 slotów

        # Bierzemy bazę paczek, żeby znać wagę i objętość (uproszczenie: randomowe dane na potrzeby wizualizacji)
        # W prawdziwym systemie musielibyśmy pobrać realne dane paczek z pliku JSON
        for i, pid in enumerate(wektor_id):
            x1 = paka_x_start + i * paczka_width
            y1 = paka_y_start

            if pid == 0:
                # Pusty slot (Zawsze SKYBLUE, żeby wyglądało profesjonalnie)
                self.van_canvas.create_rectangle(x1, y1, x1 + paczka_width, y1 + paka_height, fill="white",
                                                 outline="", tags="paczka")
            else:
                # Slot z paczką. Losujemy kolor w zależności od 'trudności' zestawu,
                # a wysokość w zależności od gęstości (uproszczenie wizualne)
                kolor = random.choice(["chocolate1", "burlywood2", "orange", "gold"])
                wypelnienie = random.uniform(0.3, 1.0)  # Wysokość paczki
                y2 = y1 + paka_height * (1 - wypelnienie)

                self.van_canvas.create_rectangle(x1, y2, x1 + paczka_width, y1 + paka_height, fill=kolor,
                                                 outline="black", tags="paczka")

    def wizualizuj_przeladowany_van(self, fit):
        """Pętla kar: Van miga na czerwono."""
        self.van_canvas.delete("paczka")
        self.van_canvas.create_rectangle(170, 40, 650, 160, fill="firebrick2", outline="red", tags="paczka")
        self.van_canvas.create_text(410, 100, text=f"KARALNY VAN\nFitness: {fit:.0f}", fill="white",
                                    font=("Arial", 14, "bold"), tags="paczka")

    def wykonaj_algorytm(self):
        try:
            # Musimy zmienić 'algorytm_harmoniczny.py', żeby wysyłał cały wektor ID paczek!
            p_ni = self.v_ni.get()
            p_hms = self.v_hms.get()
            p_hmcr = self.v_hmcr.get()
            p_par = self.v_par.get()
            p_mw = self.v_max_weight.get()
            p_mv = self.v_max_volume.get()
            p_odswiez = self.v_odswiezanie.get()

            # Pobieramy najlepsze rozwiązanie
            # Przekazujemy kolejkę, żeby algorytm wrzucał tam wektory ID paczek
            najlepsze_rozwiazanie = ah.uruchom_hs(
                ni=p_ni, hms=p_hms, hmcr=p_hmcr, par=p_par,
                max_weight=p_mw, max_volume=p_mv,
                min_pack=self.v_min_pack.get(), max_pack=self.v_max_pack.get(),
                krok_akt=p_odswiez,
                kolejka=self.kolejka_danych
            )

            self.najlepsze_tymczasowe = najlepsze_rozwiazanie
            self.dziala = False

        except Exception as e:
            self.dziala = False
            self.root.after(0, lambda: messagebox.showerror("Błąd", str(e)))
            self.root.after(0, lambda: self.btn_uruchom.config(state=tk.NORMAL))

    def pokaz_wyniki(self, najlepsze):
        self.label_status.config(text="Zakończono sukcesem!", foreground="green")
        self.btn_uruchom.config(state=tk.NORMAL)

        # Ostateczne zapełnienie vana
        self.wizualizuj_zapekniomy_van(najlepsze["wektor"], najlepsze["fitness"])

        self.text_wynik.config(state=tk.NORMAL)
        self.text_wynik.delete(1.0, tk.END)
        self.text_wynik.insert(tk.END, f"--- NAJLEPSZY WYNIK ---\n")
        self.text_wynik.insert(tk.END, f"Fitness: {najlepsze['fitness']:.2f}\n")
        self.text_wynik.insert(tk.END, f"Waga: {najlepsze['waga']:.2f} kg\n")
        self.text_wynik.insert(tk.END, f"Objętość: {najlepsze['objetosc']:.2f} cm3\n")
        self.text_wynik.insert(tk.END, f"Liczba paczek: {najlepsze['ilosc']}\n\n")

        paczki_ostateczne = list(set([p for p in najlepsze["wektor"] if p != 0]))
        self.text_wynik.insert(tk.END, f"Użyte ID paczek:\n{paczki_ostateczne}")
        self.text_wynik.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = HarmonyGUI(root)
    root.mainloop()
