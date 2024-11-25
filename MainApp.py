from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, Scrollbar, Label, messagebox, Frame, Text, VERTICAL, RIGHT, Y
import csv


USER_FILE = "users.csv"
PLUGIN_FILE = "plugins.csv"
USER_PLUGINS_FILE = "user_plugins.csv"

class Login:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("662x393")
        self.window.configure(bg="#FFFFFF")
        self.assets_path = Path(r"build/assets/frame0")
        self.setup_ui()

    def relative_to_assets(self, path: str) -> Path:
        return self.assets_path / Path(path)

    def read_csv(self, file):
        with open(file, mode="r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def login(self):
        while True:
            username = self.entry_username.get()
            password = self.entry_password.get()
            users = self.read_csv(USER_FILE)

            # Check if the credentials are correct
            for user in users:
                if user["username"] == username and user["password"] == password:
                    messagebox.showinfo("Ingelogd", f"Welkom, {username}!")
                    self.window.destroy()
                    if user.get("role") == "admin":
                        AdminApp(user=username).run()  # Open admin application if user is admin
                    else:
                        MainApp(user=username).run()  # Open main application for regular users
                    return

            messagebox.showerror("Fout", "Ongeldige gebruikersnaam of wachtwoord.")
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
            break

    def setup_ui(self):
        canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=393,
            width=662,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)

        button_image_1 = PhotoImage(file=self.relative_to_assets("button_0.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.login,
            relief="flat"
        )
        button_1.image = button_image_1
        button_1.place(x=212.0, y=273.0, width=211.0, height=51.0)

        canvas.create_text(279.0, 156.0, anchor="nw", text="Wachtwoord", fill="#000000", font=("Inter", 12 * -1))
        canvas.create_text(269.0, 81.0, anchor="nw", text="Gebruikersnaam", fill="#000000", font=("Inter", 12 * -1))

        entry_image_1 = PhotoImage(file=self.relative_to_assets("entry_1.png"))
        canvas.create_image(317.0, 126.0, image=entry_image_1)
        self.entry_username = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_username.place(x=221.0, y=110.0, width=192.0, height=30.0)

        entry_image_2 = PhotoImage(file=self.relative_to_assets("entry_2.png"))
        canvas.create_image(317.0, 197.0, image=entry_image_2)
        self.entry_password = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, show="*")
        self.entry_password.place(x=221.0, y=181.0, width=192.0, height=30.0)

    def run(self):
        self.window.resizable(False, False)
        self.window.mainloop()

class MainApp:
    def __init__(self, user):
        self.current_user = user
        self.plugin_file = PLUGIN_FILE
        self.user_plugins_file = USER_PLUGINS_FILE
        self.window = Tk()
        self.window.geometry("1440x1024")
        self.window.configure(bg="#FFFFFF")
        self.assets_path = Path(r"build/assets/frame0")
        self.setup_ui()
        self.show_available_plugins()

    def relative_to_assets(self, path: str) -> Path:
        return self.assets_path / Path(path)

    def read_csv(self, file):
        try:
            with open(file, mode="r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            messagebox.showerror("Fout", f"Het bestand {file} ontbreekt.")
            return []

    def write_csv(self, file, data, fieldnames):
        with open(file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def show_plugins(self, plugins, owned=False):
        # Clear previous plugin frames
        for widget in self.plugins_frame_inner.winfo_children():
            widget.destroy()

        # Create plugin elements dynamically
        for idx, plugin in enumerate(plugins):
            frame = Frame(self.plugins_frame_inner, bd=1, relief="solid", padx=10, pady=5, bg="#f5f5f5")
            frame.grid(row=idx, column=0, pady=5, padx=5, sticky="w")

            # Plugin details
            plugin_text = (f'{plugin["plugin_name"]} - {plugin["manufacturer"]} - '
                           f'Licentie: {plugin["license_type"]} - Prijs: {plugin["price"]}')
            label = Label(frame, text=plugin_text, font=("Arial", 12), bg="#f5f5f5")
            label.pack(side="left")

            # Buttons
            if owned:
                if plugin["license_type"] != "One Time Payment":
                    cancel_button = Button(
                        frame,
                        text="Annuleer Licentie",
                        command=lambda p=plugin: self.cancel_license(p),
                        font=("Arial", 10),
                        bg="#F44336",
                        fg="white"
                    )
                    cancel_button.pack(side="right", padx=5)
                download_button = Button(
                    frame,
                    text="Download",
                    command=lambda p=plugin: self.download_plugin(p),
                    font=("Arial", 10),
                    bg="#4CAF50",
                    fg="white"
                )
                download_button.pack(side="right", padx=5)
            else:
                buy_button = Button(
                    frame,
                    text=f"Koop ({plugin['price']})",
                    command=lambda p=plugin: self.buy_plugin(p),
                    font=("Arial", 10),
                    bg="#4CAF50",
                    fg="white"
                )
                buy_button.pack(side="right", padx=5)

    def show_available_plugins(self):
        """Displays all available plugins (not owned by the user)."""
        plugins = self.read_csv(self.plugin_file)
        user_plugins = self.read_csv(self.user_plugins_file)
        owned_plugin_names = {p['plugin_name'] for p in user_plugins if p['username'] == self.current_user}
        available_plugins = [p for p in plugins if p['plugin_name'] not in owned_plugin_names]
        self.listbox_label.config(text="Beschikbare Plug-ins")
        self.show_plugins(available_plugins, owned=False)

    def show_owned_plugins(self):
        """Displays all plugins owned by the current user."""
        plugins = self.read_csv(self.plugin_file)
        user_plugins = self.read_csv(self.user_plugins_file)
        owned_plugin_names = {p['plugin_name'] for p in user_plugins if p['username'] == self.current_user}
        owned_plugins = [p for p in plugins if p['plugin_name'] in owned_plugin_names]
        self.listbox_label.config(text="Huidige Plug-ins")
        self.show_plugins(owned_plugins, owned=True)

    def buy_plugin(self, plugin):
        """Handles buying a selected plugin."""
        plugin_name = plugin["plugin_name"]
        user_plugins = self.read_csv(self.user_plugins_file)
        user_plugins.append({"username": self.current_user, "plugin_name": plugin_name})

        self.write_csv(self.user_plugins_file, user_plugins, fieldnames=["username", "plugin_name"])
        messagebox.showinfo("Succes", f"Je hebt {plugin_name} gekocht!")
        self.show_available_plugins()

    def cancel_license(self, plugin):
        """Handles license cancellation for a selected plugin."""
        plugin_name = plugin["plugin_name"]
        user_plugins = self.read_csv(self.user_plugins_file)
        user_plugins = [p for p in user_plugins if not (p["username"] == self.current_user and p["plugin_name"] == plugin_name)]

        self.write_csv(self.user_plugins_file, user_plugins, fieldnames=["username", "plugin_name"])
        messagebox.showinfo("Succes", f"Je hebt de licentie voor {plugin_name} geannuleerd!")
        self.show_owned_plugins()

    def download_plugin(self, plugin):
        plugin_name = plugin["plugin_name"]
        messagebox.showinfo("Download", f"Je hebt {plugin_name} gedownload!")

    def logout(self):
        self.window.destroy()
        Login().run()

    def setup_ui(self):
        canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=1024,
            width=1440,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        canvas.create_rectangle(0.0, 0.0, 437.0, 1024.0, fill="#D9D9D9", outline="")

        # Sidebar buttons
        button_image_1 = PhotoImage(file=self.relative_to_assets("button_2.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.show_available_plugins,
            relief="flat"
        )
        button_1.image = button_image_1
        button_1.place(x=90.0, y=53.0, width=230.0, height=75.0)

        button_image_2 = PhotoImage(file=self.relative_to_assets("button_1.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.show_owned_plugins,
            relief="flat"
        )
        button_2.image = button_image_2
        button_2.place(x=90.0, y=209.0, width=230.0, height=75.0)

        button_image_3 = PhotoImage(file=self.relative_to_assets("button_3.png"))
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.logout,
            relief="flat"
        )
        button_3.image = button_image_3
        button_3.place(x=94.0, y=650.0, width=230.0, height=75.0)

        # Main area for listing plugins
        self.listbox_label = Label(self.window, text="Beschikbare Plug-ins", font=("Arial", 16), bg="#FFFFFF")
        self.listbox_label.place(x=500, y=50)

        self.plugins_frame = Frame(self.window, bg="#FFFFFF")
        self.plugins_frame.place(x=500, y=100, width=800, height=800)

        # Add a canvas and scrollbar for the plugins frame
        self.plugins_canvas = Canvas(self.plugins_frame, bg="#FFFFFF")
        self.scrollbar = Scrollbar(self.plugins_frame, orient=VERTICAL, command=self.plugins_canvas.yview)
        self.plugins_frame_inner = Frame(self.plugins_canvas, bg="#FFFFFF")

        self.plugins_canvas.create_window((0, 0), window=self.plugins_frame_inner, anchor="nw")
        self.plugins_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.plugins_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill=Y)

        self.plugins_frame_inner.bind(
            "<Configure>", lambda e: self.plugins_canvas.configure(scrollregion=self.plugins_canvas.bbox("all"))
        )

    def run(self):
        self.window.resizable(False, False)
        self.window.mainloop()

class AdminApp:
    def __init__(self, user):
        self.current_user = user
        self.plugin_file = PLUGIN_FILE
        self.window = Tk()
        self.window.geometry("662x393")
        self.window.configure(bg="#FFFFFF")
        self.assets_path = Path(r"build/assets/frame0")
        self.setup_ui()

    def relative_to_assets(self, path: str) -> Path:
        return self.assets_path / Path(path)

    def read_csv(self, file):
        try:
            with open(file, mode="r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            messagebox.showerror("Fout", f"Het bestand {file} ontbreekt.")
            return []

    def write_csv(self, file, data, fieldnames):
        with open(file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def add_plugin(self):
        plugin_name = self.entry_name.get()
        license_type = self.entry_license.get()
        price = self.entry_price.get()
        manufacturer = self.current_user

        if not plugin_name or not license_type or not price:
            messagebox.showerror("Fout", "Vul alle velden in.")
            return

        plugins = self.read_csv(self.plugin_file)
        plugins.append({"plugin_name": plugin_name, "manufacturer": manufacturer, "license_type": license_type, "price": price})
        self.write_csv(self.plugin_file, plugins, fieldnames=["plugin_name", "manufacturer", "license_type", "price"])

        messagebox.showinfo("Succes", f"Plug-in '{plugin_name}' is toegevoegd aan beschikbare plug-ins!")

    def setup_ui(self):
        canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=393,
            width=662,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)

        button_4 = Button(
            self.window,
            text="Toevoegen",
            borderwidth=0,
            highlightthickness=0,
            command=self.add_plugin,
            relief="flat"
        )
        button_4.place(
            x=212.0,
            y=273.0,
            width=211.0,
            height=51.0
        )

        canvas.create_text(
            202.0,
            109.99999946355638,
            anchor="nw",
            text="Licentie type (One Time Payment, Subscription, etc.)",
            fill="#000000",
            font=("Inter", 12 * -1)
        )

        canvas.create_text(
            279.00001525878906,
            52.99999946355638,
            anchor="nw",
            text="Plug-in naam",
            fill="#000000",
            font=("Inter", 12 * -1)
        )

        entry_image_1 = PhotoImage(file=self.relative_to_assets("entry_1.png"))
        canvas.create_image(316.99999237060547, 88.99999850988206, image=entry_image_1)
        self.entry_name = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_name.place(x=221.0, y=72.99999946355638, width=191.99998474121094, height=29.999998092651367)

        entry_image_2 = PhotoImage(file=self.relative_to_assets("entry_2.png"))
        canvas.create_image(317.99999237060547, 155.99999850988206, image=entry_image_2)
        self.entry_license = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_license.place(x=222.0, y=139.99999946355638, width=191.99998474121094, height=29.999998092651367)

        canvas.create_text(
            304.00001525878906,
            179.0000070929509,
            anchor="nw",
            text="Prijs",
            fill="#000000",
            font=("Inter", 12 * -1)
        )

        entry_image_3 = PhotoImage(file=self.relative_to_assets("entry_3.png"))
        canvas.create_image(317.99999237060547, 215.0000061392766, image=entry_image_3)
        self.entry_price = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_price.place(x=222.0, y=199.0000070929509, width=191.99998474121094, height=29.999998092651367)

    def run(self):
        self.window.resizable(False, False)
        self.window.mainloop()


# Start the application
if __name__ == "__main__":
    Login().run()
