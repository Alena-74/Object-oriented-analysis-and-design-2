import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os
import copy

class Aquarium:
    def __init__(self, update_callback=None):
        self.fishes = []
        self.food_level = 100
        self.light_on = False
        self.filter_on = False
        self.heater_on = False
        self.water_temp = 22.0
        self.water_clean = 100
        self.update_callback = update_callback

    def add_fish(self, name):
        self.fishes.append(name)
        if self.update_callback:
            self.update_callback()
        return len(self.fishes) - 1

    def remove_fish(self, index):
        if 0 <= index < len(self.fishes):
            del self.fishes[index]
            if self.update_callback:
                self.update_callback()

    def feed(self):
        self.food_level = min(100, self.food_level + 20)
        if self.update_callback:
            self.update_callback()

    def toggle_light(self):
        self.light_on = not self.light_on
        if self.update_callback:
            self.update_callback()

    def toggle_filter(self):
        self.filter_on = not self.filter_on
        if self.update_callback:
            self.update_callback()

    def toggle_heater(self):
        self.heater_on = not self.heater_on
        if self.update_callback:
            self.update_callback()

    def update(self):
        if len(self.fishes) > 0:
            self.food_level = max(0, self.food_level - 1)
        if self.heater_on:
            self.water_temp = min(28.0, self.water_temp + 0.1)
        else:
            self.water_temp = max(18.0, self.water_temp - 0.1)
        if not self.filter_on:
            self.water_clean = max(0, self.water_clean - 0.5)
        else:
            self.water_clean = min(100, self.water_clean + 0.5)
        if self.update_callback:
            self.update_callback()

    def get_state(self):
        return {
            'fishes': self.fishes.copy(),
            'food_level': self.food_level,
            'light_on': self.light_on,
            'filter_on': self.filter_on,
            'heater_on': self.heater_on,
            'water_temp': self.water_temp,
            'water_clean': self.water_clean,
        }

    def restore_state(self, state):
        self.fishes = state['fishes'].copy()
        self.food_level = state['food_level']
        self.light_on = state['light_on']
        self.filter_on = state['filter_on']
        self.heater_on = state['heater_on']
        self.water_temp = state['water_temp']
        self.water_clean = state['water_clean']
        if self.update_callback:
            self.update_callback()


class AquariumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Аквариум – без паттерна (с Undo/Redo через состояния)")
        self.root.geometry("1000x700")

        self.aquarium = Aquarium(update_callback=self.refresh_display)

        # История состояний
        self.history = []      # список состояний
        self.redo_stack = []   # список состояний для повтора
        self.save_current_state()   # сохраняем начальное состояние

        self.images = self.load_images()
        self.bubbles = []
        self.fish_positions = []
        self.fish_images = []
        self.food_particles = []

        self.setup_ui()
        self.start_animation()
        self.root.after(1000, self.update_aquarium)

    def save_current_state(self):
        """Сохраняем текущее состояние аквариума в историю (перед действием)"""
        state = self.aquarium.get_state()
        self.history.append(state)
        self.redo_stack.clear()   # новое действие очищает redo

    def undo(self):
        if len(self.history) <= 1:
            messagebox.showinfo("Инфо", "Нечего отменять")
            return
        # Последнее состояние – текущее, предпоследнее – то, к которому откатываемся
        self.redo_stack.append(self.history.pop())
        prev_state = self.history[-1]
        self.aquarium.restore_state(prev_state)
        # После отмены нужно пересинхронизировать позиции рыбок
        self.sync_fish_positions()
        self.refresh_display()

    def redo(self):
        if not self.redo_stack:
            messagebox.showinfo("Инфо", "Нечего повторять")
            return
        state = self.redo_stack.pop()
        self.history.append(state)
        self.aquarium.restore_state(state)
        self.sync_fish_positions()
        self.refresh_display()

    def do_action(self, action):
        """Обёртка для любого действия: сохраняет состояние перед действием, затем выполняет"""
        self.save_current_state()
        action()
        self.sync_fish_positions()
        self.refresh_display()

    def load_images(self):
        images = {}
        img_dir = "images"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        bg_path = os.path.join(img_dir, 'background.png')
        if os.path.exists(bg_path):
            try:
                img = Image.open(bg_path).convert('RGB')
                img = img.resize((800, 400), Image.LANCZOS)
                images['background'] = ImageTk.PhotoImage(img)
            except:
                images['background'] = None
        else:
            images['background'] = None

        fish_path = os.path.join(img_dir, 'fish.png')
        if os.path.exists(fish_path):
            try:
                img = Image.open(fish_path).resize((40,40), Image.LANCZOS)
                images['fish'] = ImageTk.PhotoImage(img)
            except:
                images['fish'] = None
        else:
            images['fish'] = None

        def load_static(name, size):
            path = os.path.join(img_dir, name)
            if os.path.exists(path):
                try:
                    img = Image.open(path).resize(size, Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except:
                    return None
            return None

        images['heater_static'] = load_static('heater.png', (60,60))
        images['filter_static'] = load_static('filter.png', (60,60))
        images['light_static'] = load_static('light_bulb.png', (50,50))

        self._image_refs = images.copy()
        return images

    def setup_ui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(control_frame, text="Добавить рыбку", command=self.add_fish).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Покормить", command=self.feed).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Свет", command=self.toggle_light).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Фильтр", command=self.toggle_filter).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Обогреватель", command=self.toggle_heater).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Отменить", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Повторить", command=self.redo).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.root, width=800, height=400, highlightthickness=0)
        self.canvas.pack(pady=10)

        info_frame = tk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.food_label = tk.Label(info_frame, text="Сытость: 100%", font=('Arial', 10))
        self.food_label.pack(side=tk.LEFT, padx=10)
        self.temp_label = tk.Label(info_frame, text="Температура: 22.0°C", font=('Arial', 10))
        self.temp_label.pack(side=tk.LEFT, padx=10)
        self.clean_label = tk.Label(info_frame, text="Чистота: 100%", font=('Arial', 10))
        self.clean_label.pack(side=tk.LEFT, padx=10)

        self.refresh_display()

    def create_food_particles(self):
        for _ in range(12):
            x = random.randint(100, 700)
            y = random.randint(20, 100)
            size = random.randint(2, 4)
            vy = random.uniform(1, 2)
            self.food_particles.append([x, y, size, vy])

    def add_fish(self):
        self.do_action(lambda: self.aquarium.add_fish(f"Рыбка {len(self.aquarium.fishes)+1}"))

    def feed(self):
        self.do_action(lambda: self.aquarium.feed())
        # Анимация корма добавляется после действия
        self.create_food_particles()

    def toggle_light(self):
        self.do_action(lambda: self.aquarium.toggle_light())

    def toggle_filter(self):
        self.do_action(lambda: self.aquarium.toggle_filter())

    def toggle_heater(self):
        self.do_action(lambda: self.aquarium.toggle_heater())

    def sync_fish_positions(self):
        while len(self.fish_positions) > len(self.aquarium.fishes):
            self.fish_positions.pop()
            if self.fish_images:
                self.fish_images.pop()
        while len(self.fish_positions) < len(self.aquarium.fishes):
            x = random.randint(120, 680)
            y = random.randint(120, 280)
            dx = random.choice([-1.5, -1, 1, 1.5])
            dy = random.choice([-1.5, -1, 1, 1.5])
            self.fish_positions.append([x, y, dx, dy])
            self.fish_images.append(None)

    def refresh_display(self):
        self.food_label.config(text=f"Сытость: {int(self.aquarium.food_level)}%")
        self.temp_label.config(text=f"Температура: {self.aquarium.water_temp:.1f}°C")
        self.clean_label.config(text=f"Чистота: {int(self.aquarium.water_clean)}%")
        self.sync_fish_positions()
        self.draw_aquarium()

    def draw_aquarium(self):
        self.canvas.delete("all")

        if self.images.get('background'):
            self.canvas.create_image(0, 0, anchor='nw', image=self.images['background'])
        else:
            self.canvas.create_rectangle(0, 0, 800, 400, fill='#87CEEB', outline='')

        if self.images.get('heater_static'):
            self.canvas.create_image(80, 200, image=self.images['heater_static'], anchor='center')
        else:
            self.canvas.create_rectangle(60, 180, 100, 220, fill='#CCCCCC', outline='black')
            self.canvas.create_text(80, 200, text="🌡️", font=('Arial', 16))

        if self.images.get('filter_static'):
            self.canvas.create_image(80, 290, image=self.images['filter_static'], anchor='center')
        else:
            self.canvas.create_rectangle(60, 270, 100, 310, fill='#CCCCCC', outline='black')
            self.canvas.create_text(80, 290, text="💧", font=('Arial', 16))

        if self.images.get('light_static'):
            self.canvas.create_image(720, 40, image=self.images['light_static'], anchor='center')
        else:
            self.canvas.create_rectangle(700, 20, 740, 60, fill='#FFFF99', outline='black')
            self.canvas.create_text(720, 40, text="💡", font=('Arial', 16))

        if not self.aquarium.light_on and not self.aquarium.heater_on:
            self.canvas.create_rectangle(0, 0, 800, 400, fill='#d9e6f2', outline='', stipple='gray50')
        else:
            if self.aquarium.light_on:
                self.canvas.create_rectangle(0, 0, 800, 400, fill='#ffffcc', outline='', stipple='gray50')
            if self.aquarium.heater_on:
                self.canvas.create_rectangle(0, 0, 800, 400, fill='#ffcccc', outline='', stipple='gray50')

        fish_img = self.images.get('fish')
        for idx, (x, y, dx, dy) in enumerate(self.fish_positions):
            if fish_img:
                self.fish_images[idx] = fish_img
                self.canvas.create_image(x, y, image=fish_img, anchor='center')
            else:
                self.canvas.create_text(x, y, text="🐟", font=('Arial', 20), fill='orange')

        new_particles = []
        for x, y, size, vy in self.food_particles:
            self.canvas.create_oval(x-size, y-size, x+size, y+size, fill='#8B4513', outline='')
            y += vy
            if y < 380:
                new_particles.append([x, y, size, vy])
        self.food_particles = new_particles

        light_color = 'yellow' if self.aquarium.light_on else 'gray'
        self.canvas.create_rectangle(20, 10, 60, 50, fill=light_color, outline='black')
        self.canvas.create_text(40, 30, text="💡", font=('Arial', 16))

        filter_color = 'lightgreen' if self.aquarium.filter_on else 'gray'
        self.canvas.create_rectangle(80, 10, 120, 50, fill=filter_color, outline='black')
        self.canvas.create_text(100, 30, text="💧", font=('Arial', 16))

        heater_color = 'salmon' if self.aquarium.heater_on else 'gray'
        self.canvas.create_rectangle(140, 10, 180, 50, fill=heater_color, outline='black')
        self.canvas.create_text(160, 30, text="🌡️", font=('Arial', 16))

        if self.aquarium.filter_on:
            if random.random() < 0.3:
                self.bubbles.append([random.randint(60, 100), random.randint(290, 310), random.randint(3,8), random.uniform(2,5)])
            new_bubbles = []
            for bx, by, r, speed in self.bubbles:
                self.canvas.create_oval(bx-r, by-r, bx+r, by+r, fill='white', outline='lightblue')
                by -= speed
                if by > 20:
                    new_bubbles.append([bx, by, r, speed])
            self.bubbles = new_bubbles

    def move_fish(self):
        for i in range(len(self.fish_positions)):
            x, y, dx, dy = self.fish_positions[i]
            if x < 120 or x > 680:
                dx = -dx
                x = max(120, min(680, x))
            if y < 120 or y > 280:
                dy = -dy
                y = max(120, min(280, y))
            x += dx
            y += dy
            dx += random.uniform(-0.2, 0.2)
            dy += random.uniform(-0.2, 0.2)
            dx = max(-2.5, min(2.5, dx))
            dy = max(-2.5, min(2.5, dy))
            self.fish_positions[i] = [x, y, dx, dy]
        self.draw_aquarium()
        self.root.after(50, self.move_fish)

    def start_animation(self):
        self.move_fish()

    def update_aquarium(self):
        self.aquarium.update()
        self.refresh_display()
        self.root.after(1000, self.update_aquarium)


if __name__ == "__main__":
    root = tk.Tk()
    app = AquariumApp(root)
    root.mainloop()
