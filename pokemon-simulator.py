import tkinter as tk  # Importiere das tkinter-Modul für die GUI-Erstellung
from tkinter import messagebox  # Importiere messagebox für Popup-Nachrichten
from PIL import Image, ImageTk  # Importiere PIL für Bildbearbeitung (Image und ImageTk für GUI)
import random  # Modul für Zufallszahlen
import requests  # Modul zum Senden von HTTP-Anfragen (für die PokéAPI)
from io import BytesIO  # Ermöglicht das Laden von Bilddaten aus Bytes
import os  # Modul zum Arbeiten mit dem Dateisystem

# --- Pokemon-Kategorien ---
legendary_ids = [144, 145, 146, 150, 151, 249, 250, 382, 383, 384, 385, 386, 487, 488, 491, 493, 494, 643, 644, 646, 9, 6, 25, 3, 26, 24, 34, 65, 130, 149]  # IDs legendärer Pokémon
rare_ids = [65, 94, 248, 254, 282, 448, 472, 475, 212, 230, 359, 373, 445, 461, 534, 553, 635, 2, 5, 8, 68, 59, 38, 54, 55, 64, 95, 107, 197, 143, 148]  # IDs seltener Pokémon

# --- Dropchancen pro Pack (nach Master-Rate sortiert: seltenste zuerst) ---
drop_chances = {
    # Dropchancen für bestimmte Pokémon je nach Packtyp
    "Mewtwo": {"Basic": 0.000003, "Premium": 0.000006, "Ultra": 0.00009, "Master": 0.00013},
    "Mew": {"Basic": 0.000003, "Premium": 0.000006, "Ultra": 0.00009, "Master": 0.00013},
    "Rayquaza": {"Basic": 0.000025, "Premium": 0.000005, "Ultra": 0.00008, "Master": 0.00011},
    "Blastoise": {"Basic": 0.00002, "Premium": 0.000004, "Ultra": 0.00007, "Master": 0.0001},
    "Charizard": {"Basic": 0.00002, "Premium": 0.000004, "Ultra": 0.00007, "Master": 0.0001},
    "Pikachu": {"Basic": 0.000015, "Premium": 0.000003, "Ultra": 0.00005, "Master": 0.0001},
    "Greninja": {"Basic": 0.00001, "Premium": 0.000015, "Ultra": 0.000022, "Master": 0.0003},
    "Ho-Oh": {"Basic": 0.00001, "Premium": 0.000015, "Ultra": 0.000022, "Master": 0.0003},
    "Lucario": {"Basic": 0.000008, "Premium": 0.000012, "Ultra": 0.000027, "Master": 0.00034},
    "Tyranitar": {"Basic": 0.000012, "Premium": 0.000018, "Ultra": 0.000026, "Master": 0.00035},
    "Raichu": {"Basic": 0.000012, "Premium": 0.000018, "Ultra": 0.000026, "Master": 0.00035},
    "Arbok": {"Basic": 0.000015, "Premium": 0.00022, "Ultra": 0.00003, "Master": 0.0004},
    "Dragonite": {"Basic": 0.000014, "Premium": 0.00002, "Ultra": 0.000028, "Master": 0.00038},
    "Umbreon": {"Basic": 0.000015, "Premium": 0.00022, "Ultra": 0.00003, "Master": 0.0004},
    "Salamence": {"Basic": 0.000016, "Premium": 0.00023, "Ultra": 0.000031, "Master": 0.00041},
    "Metagross": {"Basic": 0.000017, "Premium": 0.00025, "Ultra": 0.000034, "Master": 0.00045},
    "Snorlax": {"Basic": 0.000018, "Premium": 0.000027, "Ultra": 0.000037, "Master": 0.00048},
    "Sylveon": {"Basic": 0.00002, "Premium": 0.00003, "Ultra": 0.000042, "Master": 0.00055},
    "Espeon": {"Basic": 0.00002, "Premium": 0.00003, "Ultra": 0.000042, "Master": 0.00055},
    "Gardevoir": {"Basic": 0.00002, "Premium": 0.00003, "Ultra": 0.000042, "Master": 0.00055},
    "Gengar": {"Basic": 0.000022, "Premium": 0.000033, "Ultra": 0.000045, "Master": 0.0006},
    "Charmeleon": {"Basic": 0.000022, "Premium": 0.000033, "Ultra": 0.000045, "Master": 0.0006},
    "Eevee": {"Basic": 0.00004, "Premium": 0.00005, "Ultra": 0.00006, "Master": 0.00085}
}

# --- Werte ---
value_overrides = {
    # Feste Werte in Euro für bestimmte Pokémon
    "Charizard": 100,
    "Rayquaza": 75,
    "Mewtwo": 60,
    "Raichu": 50,
    "Arbok": 40,
    "Mew": 55,
    "Greninja": 50,
    "Tyranitar": 45,
    "Dragonite": 42,
    "Umbreon": 40,
    "Salamence": 40,
    "Metagross": 38,
    "Lucario": 20,
    "Snorlax": 32,
    "Sylveon": 30,
    "Espeon": 30,
    "Charmeleon": 40,
    "Gengar": 30,
    "Gardevoir": 28,
    "Pikachu": 80,
    "Eevee": 20,
    "Squirtle": 15,
    "Blastoise": 80  
}

# --- Farben ---
color_overrides = {
    # Farben zur Darstellung bestimmter Pokémon im UI
    "Charizard": "red",
    "Mew": "pink",
    "Rayquaza": "green",
    "Umbreon": "purple",
    "Greninja": "blue",
    "Mewtwo": "violet",
    "Pikachu": "orange",
    "Blastoise": "teal" 
}

# --- Packs ---
packs = {
    # Preis und Wahrscheinlichkeiten für legendäre/spezielle Pokémon je Pack
    "Basic": {"price": 10, "legendary": 0.025, "rare": 0.0075},
    "Premium": {"price": 20, "legendary": 0.033, "rare": 0.01},
    "Ultra": {"price": 35, "legendary": 0.05, "rare": 0.15},
    "Master": {"price": 50, "legendary": 0.0833, "rare": 0.25}
}

# --- Highscore-Datei ---
HIGHSCORE_FILE = "highscore.txt"  # Name der Datei zum Speichern des Highscores

# --- Highscore laden ---
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):  # Falls Datei existiert
        with open(HIGHSCORE_FILE, "r") as file:  # Datei öffnen
            return int(file.read().strip())  # Inhalt lesen und in Integer umwandeln
    return 0  # Wenn Datei nicht existiert, Highscore = 0

# Highscore speichern
def save_highscore():
    with open(HIGHSCORE_FILE, "w") as file:  # Datei zum Schreiben öffnen
        file.write(str(player.highscore))  # Aktuellen Highscore reinschreiben

# --- Spielerklasse ---
class Player:
    def __init__(self):
        self.money = 50  # Startgeld
        self.collection = []  # Gesammelte Pokémon
        self.highscore = load_highscore()  # Highscore laden

    def update_highscore(self):
        if self.money > self.highscore:  # Wenn aktuelles Geld > Highscore
            self.highscore = self.money  # Neuen Highscore setzen
            save_highscore()  # Highscore speichern
            highscore_label.config(text=f"🏆 Highscore: {self.highscore} €")  # Label aktualisieren

player = Player()  # Spieler-Instanz erstellen

# --- GUI Setup ---
root = tk.Tk()  # Hauptfenster erstellen
root.title("Pokémon Pack Simulator")  # Fenstertitel setzen
root.geometry("950x700")  # Fenstergröße setzen

pack_frame = tk.Frame(root)  # Frame für Pack-Buttons
pack_frame.pack(pady=10)  # Abstand oben/unten

card_frame = tk.Frame(root)  # Frame für Kartenanzeige
card_frame.pack(pady=10)  # Abstand

info_label = tk.Label(root, text=f"💰 Guthaben: {player.money} €", font=("Arial", 14))  # Label für Geld
info_label.pack(pady=5)  # Abstand

highscore_label = tk.Label(root, text=f"🏆 Highscore: {player.highscore} €", font=("Arial", 14), fg="blue")  # Label für Highscore
highscore_label.pack(pady=5)  # Abstand

# --- Hilfsfunktionen ---
def fetch_pokemon_data(poke_id_or_name):
    # Holt Daten von der PokéAPI für ein Pokémon (nach ID oder Name)
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id_or_name}"  # API-URL
    response = requests.get(url)  # HTTP-Request senden
    if response.status_code != 200:  # Wenn Fehler beim Abrufen
        return None
    return response.json()  # JSON-Antwort zurückgeben


def get_pokemon_image(url):
    try:
        img_data = requests.get(url).content
        img = Image.open(BytesIO(img_data))  
        img = img.resize((96, 96))  
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error fetching or processing image from {url}: {e}")
        
        placeholder = Image.new('RGB', (96, 96), color='gray')  
        return ImageTk.PhotoImage(placeholder) 


def get_price(name, rarity):
    return value_overrides.get(name, 30 if rarity == "🌟 Legendary" else 10 if rarity == "✨ Rare" else 1)

def reveal_card(index, pack_name):
    if index >= 5:
        return

   
    for special_name, pack_chances in drop_chances.items():
        chance = pack_chances.get(pack_name, 0)
        if random.random() < chance:
            data = fetch_pokemon_data(special_name.lower())
            if data:
                name = data["name"].title()
                img_url = data["sprites"]["front_default"]
                
                if data["id"] in legendary_ids:
                    rarity = "🌟 Legendary"
                elif data["id"] in rare_ids:
                    rarity = "✨ Rare"
                else:
                    rarity = "Common"
                show_card(name, rarity, img_url)
                root.after(700, lambda: reveal_card(index + 1, pack_name))
            return

    
    roll = random.random()
    rarity = "Common"
    
    if roll < packs[pack_name]["legendary"]:
        poke_id = random.choice(legendary_ids)
        rarity = "🌟 Legendary"
    elif roll < packs[pack_name]["legendary"] + packs[pack_name]["rare"]:
        poke_id = random.choice(rare_ids)
        rarity = "✨ Rare"
    else:
        poke_id = random.randint(1, 898)

    
    data = fetch_pokemon_data(poke_id)
    if data:
        name = data["name"].title()
        img_url = data["sprites"]["front_default"]
        if data["id"] in legendary_ids:
            rarity = "🌟 Legendary"
        elif data["id"] in rare_ids:
            rarity = "✨ Rare"
        show_card(name, rarity, img_url)

    root.after(700, lambda: reveal_card(index + 1, pack_name))


def show_card(name, rarity, img_url):
    img = get_pokemon_image(img_url)
    price = get_price(name, rarity)

   
    if rarity == "🌟 Legendary":
        fg_color = "gold"
    elif rarity == "✨ Rare":
        fg_color = "blueviolet" 
    else:
        fg_color = color_overrides.get(name, "black")  

    frame = tk.Frame(card_frame)
    frame.pack(side="left", padx=10)

    img_label = tk.Label(frame, image=img)
    img_label.image = img
    img_label.pack()

    text = f"{name}\n{rarity}\n💵 {price} €"
    label = tk.Label(frame, text=text, font=("Arial", 10), fg=fg_color)
    label.pack()

    player.collection.append((name, rarity, price))


def open_pack(pack_name):
    pack = packs[pack_name]
    if player.money < pack["price"]:
        messagebox.showwarning("Nicht genug Geld", "Du hast nicht genug Geld für dieses Pack!")
        return

    player.money -= pack["price"]
    info_label.config(text=f"💰 Guthaben: {player.money} €")

    for widget in card_frame.winfo_children():
        widget.destroy()

    reveal_card(0, pack_name)
    player.update_highscore()

def open_shop():
    if not player.collection:
        messagebox.showinfo("Shop", "Du hast keine Karten zum Verkaufen!")
        return

    total_value = sum(price for _, _, price in player.collection)
    player.money += total_value
    player.collection.clear()
    messagebox.showinfo("Shop", f"Du hast alle Karten verkauft und {total_value} € verdient!")
    info_label.config(text=f"💰 Guthaben: {player.money} €")

    player.update_highscore()

def reset_game():
    player.money = 50
    player.collection.clear()
    info_label.config(text=f"💰 Guthaben: {player.money} €")
    for widget in card_frame.winfo_children():
        widget.destroy()
    messagebox.showinfo("Reset", "Das Spiel wurde zurückgesetzt!")

# --- Buttons ---
for pack_name in packs:
    btn = tk.Button(pack_frame, text=f"{pack_name} Pack ({packs[pack_name]['price']} €)",
                    command=lambda name=pack_name: open_pack(name), width=20)
    btn.pack(side="left", padx=10)

shop_btn = tk.Button(root, text="🛒 Karten im Shop verkaufen", command=open_shop, bg="lightgreen")
shop_btn.pack(pady=5)

reset_btn = tk.Button(root, text="🔄 Reset", command=reset_game, bg="lightcoral")
reset_btn.pack(pady=5)

# --- Start ---
root.mainloop()