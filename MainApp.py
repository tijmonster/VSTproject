from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, Scrollbar, Label, messagebox, Frame
import csv
import os

# CSV file paths
USER_FILE = "users.csv"
PLUGIN_FILE = "plugins.csv"
USER_PLUGINS_FILE = "user_plugins.csv"  # New file to store user-specific plugin ownership

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
        username = self.entry_username.get()
        password = self.entry_password.get()
        users = self.read_csv(USER_FILE)

        for user in users:
            if user["username"] == username and user["password"] == password:
                messagebox.showinfo("Ingelogd", f"Welkom, {username}!")
                self.window.destroy()  # Close login window
                MainApp(user=username).run()  # Open main application
                return

        messagebox.showerror("Fout", "Ongeldige gebruikersnaam of wachtwoord.")

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
        self.show_available_plugins()  # Initialize with available plugins

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
        for widget in self.plugins_frame.winfo_children():
            widget.destroy()

        # Create plugin elements dynamically
        for idx, plugin in enumerate(plugins):
            frame = Frame(self.plugins_frame, bd=1, relief="solid", padx=10, pady=5, bg="#f5f5f5")
            frame.grid(row=idx, column=0, pady=5, padx=5, sticky="w")

            # Plugin details
            plugin_text = (f'{plugin["plugin_name"]} - {plugin["manufacturer"]} - '
                           f'Licentie: {plugin["license_type"]}')
            label = Label(frame, text=plugin_text, font=("Arial", 12), bg="#f5f5f5")
            label.pack(side="left")

            # Buttons
            if owned:
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
                    text="Koop",
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
        """Handles downloading a selected plugin."""
        plugin_name = plugin["plugin_name"]
        messagebox.showinfo("Download", f"Je hebt {plugin_name} gedownload!")

    def logout(self):
        """Logs the user out and returns to the login screen."""
        self.window.destroy()
        Login().run()

    def setup_ui(self):
        """Sets up the user interface."""
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
        self.plugins_frame.place(x=500, y=100)

        scrollbar = Scrollbar(self.window, command=self.plugins_frame.yview)
        scrollbar.place(x=1350, y=100, height=500)

    def run(self):
        self.window.resizable(False, False)
        self.window.mainloop()


# Start the application
if __name__ == "__main__":
    Login().run()
