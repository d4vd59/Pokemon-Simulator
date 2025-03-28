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
    "Rayquaza": {"Basic": 0.00025, "Premium": 0.00005, "Ultra": 0.00008, "Master": 0.00011},
    "Mewtwo": {"Basic": 0.0003, "Premium": 0.00006, "Ultra": 0.00009, "Master": 0.00013},
    "Mew": {"Basic": 0.0003, "Premium": 0.00006, "Ultra": 0.00009, "Master": 0.00013},
    "Greninja": {"Basic": 0.001, "Premium": 0.00015, "Ultra": 0.00022, "Master": 0.0003},
    "Tyranitar": {"Basic": 0.0012, "Premium": 0.00018, "Ultra": 0.00026, "Master": 0.00035},
    "Dragonite": {"Basic": 0.0014, "Premium": 0.0002, "Ultra": 0.00028, "Master": 0.00038},
    "Umbreon": {"Basic": 0.0015, "Premium": 0.00022, "Ultra": 0.0003, "Master": 0.0004},
    "Salamence": {"Basic": 0.0016, "Premium": 0.00023, "Ultra": 0.00031, "Master": 0.00041},
    "Metagross": {"Basic": 0.0017, "Premium": 0.00025, "Ultra": 0.00034, "Master": 0.00045},
    "Lucario": {"Basic": 0.0008, "Premium": 0.00012, "Ultra": 0.00017, "Master": 0.00024},
    "Snorlax": {"Basic": 0.0018, "Premium": 0.00027, "Ultra": 0.00037, "Master": 0.00048},
    "Sylveon": {"Basic": 0.002, "Premium": 0.0003, "Ultra": 0.00042, "Master": 0.00055},
    "Espeon": {"Basic": 0.002, "Premium": 0.0003, "Ultra": 0.00042, "Master": 0.00055},
    "Gengar": {"Basic": 0.0022, "Premium": 0.00033, "Ultra": 0.00045, "Master": 0.0006},
    "Gardevoir": {"Basic": 0.002, "Premium": 0.0003, "Ultra": 0.00042, "Master": 0.00055},
    "Pikachu": {"Basic": 0.003, "Premium": 0.00045, "Ultra": 0.0006, "Master": 0.00075},
    "Eevee": {"Basic": 0.004, "Premium": 0.0006, "Ultra": 0.00085, "Master": 0.001}
}

# --- Werte ---
value_overrides = {name: value for name, value in zip(drop_chances.keys(),
    [80, 75, 60, 55, 50, 45, 42, 40, 40, 38, 35, 32, 30, 30, 30, 28, 25, 20])}

# --- Farben ---
color_overrides = {
    "Charizard": "red", "Mew": "pink", "Rayquaza": "green",
    "Umbreon": "purple", "Greninja": "blue", "Mewtwo": "violet", "Pikachu": "orange"
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