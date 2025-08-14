import os
import requests
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIG ---
GITHUB_USER = "ThunderEmm"
REPO_NAME = "Create-SMP-Mods"
BRANCH = "main"  # Change if your default branch is not main
MODS_DIR = os.path.abspath(os.path.dirname(__file__))  # Current folder
# ----------------

def get_local_mods():
    return {f for f in os.listdir(MODS_DIR) if f.endswith(".jar")}

def get_remote_mods():
    """Fetch list of .jar files from GitHub repository without downloading."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        remote_mods = {item["name"] for item in data if item["name"].endswith(".jar")}
        return remote_mods
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch remote mods:\n{e}")
        return set()

def pull_selected_mods(selected_mods):
    """Pull only selected mods using git."""
    if not selected_mods:
        return
    try:
        # Use 'git fetch' to update remote info without touching files
        subprocess.run(["git", "fetch"], cwd=MODS_DIR, check=True)
        for mod in selected_mods:
            # Checkout the individual file from remote
            subprocess.run(
                ["git", "checkout", f"origin/{BRANCH}", "--", mod],
                cwd=MODS_DIR,
                check=True
            )
        messagebox.showinfo("Success", "Mods downloaded successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Git Error", f"Error installing mods:\n{e}")

def main():
    local_mods = get_local_mods()
    remote_mods = get_remote_mods()
    missing_mods = sorted(remote_mods - local_mods)

    root = tk.Tk()
    root.title("Install Mods")
    root.geometry("400x400")
    root.configure(bg="white")

    title_label = tk.Label(root, text="Install Mods", font=("Arial", 16, "bold"), bg="white")
    title_label.pack(pady=10)

    # Scrollable frame
    container = ttk.Frame(root)
    canvas = tk.Canvas(container, height=250)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0,0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    container.pack(fill="both", expand=True, padx=10)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    check_vars = {}
    if missing_mods:
        for mod in missing_mods:
            var = tk.BooleanVar(value=True)
            check = tk.Checkbutton(scroll_frame, text=mod, variable=var, bg="white")
            check.pack(anchor="w")
            check_vars[mod] = var
    else:
        no_mods_label = tk.Label(scroll_frame, text="Your Mods Directory is Up To Date!", bg="white")
        no_mods_label.pack()

    def update_install_button():
        if any(var.get() for var in check_vars.values()):
            install_btn.config(state="normal")
        else:
            install_btn.config(state="disabled")

    # Monitor checkbox changes
    for var in check_vars.values():
        var.trace_add("write", lambda *args: update_install_button())

    # Buttons
    button_frame = tk.Frame(root, bg="white")
    button_frame.pack(pady=10, anchor="e")

    def on_install():
        selected = [mod for mod, var in check_vars.items() if var.get()]
        pull_selected_mods(selected)
        root.destroy()

    def on_cancel():
        root.destroy()

    cancel_btn = tk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_btn.pack(side="left", padx=5)
    install_btn = tk.Button(button_frame, text="Install", command=on_install)
    install_btn.pack(side="right", padx=5)

    # Disable install if no mods missing
    if not missing_mods:
        install_btn.config(state="disabled")

    root.mainloop()

if __name__ == "__main__":
    main()
