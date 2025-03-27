import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import requests
from io import BytesIO
import os

# --- Pokémon-Kategorien ---
legendary_ids = [144, 145, 146, 150, 151, 249, 250, 382, 383, 384, 385, 386, 487, 488, 491, 493, 494, 643, 644, 646]
rare_ids = [6, 9, 65, 94, 149, 248, 254, 282, 448, 472, 475, 212, 230, 359, 373, 445, 461, 534, 553, 635]

# --- Dropchancen pro Pack ---
drop_chances = {
    "Charizard": {"Basic": 0.0002, "Premium": 0.00004, "Ultra": 0.00007, "Master": 0.0001},
    "Rayquaza": {"Basic": 0.00025, "Premium": 0.00005, "Ultra": 0.00008, "Master": 0.00012},
    "Mewtwo": {"Basic": 0.0003, "Premium": 0.00006, "Ultra": 0.00009, "Master": 0.00013},
}

# --- Werte ---
value_overrides = {
    "Charizard": 80, "Rayquaza": 75, "Mewtwo": 60
}

# --- Farben ---
color_overrides = {
    "Charizard": "red", "Rayquaza": "green", "Mewtwo": "violet"
}

# --- Packs ---
packs = {
    "Basic": {"price": 10, "legendary": 0.0025, "rare": 0.05},
    "Premium": {"price": 20, "legendary": 0.0057, "rare": 0.15},
    "Ultra": {"price": 35, "legendary": 0.0085, "rare": 0.3},
    "Master": {"price": 50, "legendary": 0.010, "rare": 0.4}
}

# --- Highscore-Datei ---
HIGHSCORE_FILE = "highscore.txt"

# --- Highscore laden ---
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as file:
            return int(file.read().strip())
    return 0

def save_highscore():
    with open(HIGHSCORE_FILE, "w") as file:
        file.write(str(player.highscore))

# --- Spielerklasse ---
class Player:
    def __init__(self):
        self.money = 50
        self.collection = []
        self.highscore = load_highscore()

    def update_highscore(self):
        if self.money > self.highscore:
            self.highscore = self.money
            save_highscore()
            highscore_label.config(text=f"🏆 Highscore: {self.highscore} €")

player = Player()

# --- GUI Setup ---
root = tk.Tk()
root.title("Pokémon Pack Simulator")
root.geometry("950x700")

pack_frame = tk.Frame(root)
pack_frame.pack(pady=10)

card_frame = tk.Frame(root)
card_frame.pack(pady=10)

info_label = tk.Label(root, text=f"💰 Guthaben: {player.money} €", font=("Arial", 14))
info_label.pack(pady=5)

highscore_label = tk.Label(root, text=f"🏆 Highscore: {player.highscore} €", font=("Arial", 14), fg="blue")
highscore_label.pack(pady=5)

# --- Hilfsfunktionen ---
def fetch_pokemon_data(poke_id_or_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id_or_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def get_pokemon_image(url):
    img_data = requests.get(url).content
    img = Image.open(BytesIO(img_data)).resize((96, 96))
    return ImageTk.PhotoImage(img)

def get_price(name, rarity):
    return value_overrides.get(name, 30 if rarity == "🌟 Legendary" else 10 if rarity == "✨ Rare" else 1)

def reveal_card(index, pack_name):
    if index >= 5:
        return

    # Spezieller Pokémon-Drop
    for special_name, pack_chances in drop_chances.items():
        chance = pack_chances.get(pack_name, 0)
        if random.random() < chance:
            data = fetch_pokemon_data(special_name.lower())
            if data:
                name = data["name"].title()
                img_url = data["sprites"]["front_default"]
                rarity = "🌟 Legendary" if data["id"] in legendary_ids else "✨ Rare"
                show_card(name, rarity, img_url)
                root.after(700, lambda: reveal_card(index + 1, pack_name))
            return

    # Regulärer Drop
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
        show_card(name, rarity, img_url)

    root.after(700, lambda: reveal_card(index + 1, pack_name))

def show_card(name, rarity, img_url):
    img = get_pokemon_image(img_url)
    price = get_price(name, rarity)

    frame = tk.Frame(card_frame)
    frame.pack(side="left", padx=10)

    img_label = tk.Label(frame, image=img)
    img_label.image = img
    img_label.pack()

    fg_color = color_overrides.get(name, "black")
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

# --- Buttons ---
for pack_name in packs:
    btn = tk.Button(pack_frame, text=f"{pack_name} Pack ({packs[pack_name]['price']} €)",
                    command=lambda name=pack_name: open_pack(name), width=20)
    btn.pack(side="left", padx=10)

shop_btn = tk.Button(root, text="🛒 Karten im Shop verkaufen", command=open_shop, bg="lightgreen")
shop_btn.pack(pady=20)

# --- Start ---
root.mainloop()