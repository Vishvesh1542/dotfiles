dir := invocation_directory()

list:
    @just --choose

install-dotfiles:
    mkdir -p "$HOME/.config"
    @just link-app "fastfetch"
    @just link-app "niri"
    @just link-app "fish"
    @just link-app "ghostty"
    @just link-app "nvim"
    @just link-app "swayidle"
    @just link-app "swaylock"
    @just link-app "swaync"
    @just link-app "zed"

    @just link-app "scripts"
    @just link-app "zenith"

uninstall-dotfiles:
    @just unlink-app "fastfetch"
    @just unlink-app "niri"
    @just unlink-app "fish"
    @just unlink-app "ghostty"
    @just unlink-app "nvim"
    @just unlink-app "swayidle"
    @just unlink-app "swaylock"
    @just unlink-app "swaync"
    @just unlink-app "zed"

    @just unlink-app "scripts"
    @just unlink-app "zenith"

setup-computer: install-dotfiles install-apps install-venv-for-bar hide-bloat-apps set-tweaks

install-apps: install-tools
    #!/bin/env python3
    import subprocess
    import shutil

    subprocess.run(["sudo", "-v"], check=True)

    def is_installed(app):
        try:
            result = subprocess.run(["pacman", "-Qq", app], text=True, capture_output=True)
            return result.returncode == 0
        except Exception:
            return False

    de_tools = ["brightnessctl", "swaync",
        "swayidle", "playerctl",
        "wlsunset", "niri", "xwayland-satellite", "bluetui",
        "polkit-gnome", "xdg-desktop-portal-gnome", "gdm", "zed"]

    common_apps = ["fastfetch", "nvim",
        "adw-gtk-theme", "flatpak", "openrgb", "nautilus", "ghostty"]

    yay_apps = ["swaylock-effects-improved-git", "vicinae-bin",
        "awww-bin", "envycontrol", "opentabletdriver", "zen-browser-bin"]

    for app in de_tools + common_apps:
        if not is_installed(app):
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", app] , check=True)

    for app in yay_apps:
        if not is_installed(app):
            subprocess.run(["yay", "-S", "--noconfirm", app], check=True)

    subprocess.run(["systemctl", "enable", "gdm"])

set-tweaks:
    sudo -v
    sudo flatpak override --filesystem=xdg-data/themes
    sudo flatpak mask org.gtk.Gtk3theme.adw-gtk3
    sudo flatpak mask org.gtk.Gtk3theme.adw-gtk3-dark
    gsettings set org.gnome.desktop.interface gtk-theme 'adw-gtk3-dark'
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'

install-tools:
    @sudo pacman -S --noconfirm --needed python
    @sudo pacman -S --noconfirm --needed base-devel
    @sudo pacman -S --noconfirm --needed git
    @sudo pacman -S --noconfirm --needed fish

    chsh -s /bin/fish

    @command -v yay >/dev/null 2>&1 || ( \
            git clone https://aur.archlinux.org/yay.git /tmp/yay && \
            cd /tmp/yay && makepkg -si --noconfirm && \
            rm -rf /tmp/yay \
        )

install-venv-for-bar:
    #!/usr/bin/env python3
    import os
    import subprocess
    import sys
    from pathlib import Path

    zenith_path = Path("~/.config/zenith").expanduser()
    venv_path = zenith_path / ".venv"
    req_file = zenith_path / "requirements.txt"
    pip_path = venv_path / "bin" / "pip"

    zenith_path.mkdir(parents=True, exist_ok=True)

    if not venv_path.exists():
        print(f"--- Creating venv in {venv_path} ---")
        subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", str(venv_path)], check=True)

    if req_file.exists():
        print(f"--- Installing requirements from {req_file} ---")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_path), "install", "-r", str(req_file)], check=True)
    else:
        print(f"Error: {req_file} not found!")
        sys.exit(1)

link-app app:
    #!/bin/bash
    TARGET="$HOME/.config/{{ app }}"
    BACKUP="$HOME/.config/backup/{{ app }}"

    if [ -d "$TARGET" ] && [ ! -L "$TARGET" ]; then
        echo "Folder exists, backing up: {{ app }}"
        mkdir -p "$HOME/.config/backup/"
        mv "$TARGET" "$BACKUP"
    fi

    ln -snf {{ dir }}/{{ app }} "$TARGET"
    echo "Linked {{ app }}"

unlink-app app:
    rm -f "$HOME/.config/{{ app }}"

hide-bloat-apps:
    #!/usr/bin/env bash
    mkdir -p ~/.local/share/applications
    apps=(avahi-discover bssh bvnc qv4l2 qvidcap nvim)

    for app in "${apps[@]}"; do
        file="$HOME/.local/share/applications/$app.desktop"
        echo "[Desktop Entry]" > "$file"
        echo "Type=Application" >> "$file"
        echo "Name=$app (Hidden)" >> "$file"
        echo "NoDisplay=true" >> "$file"
        echo "Exec=/usr/bin/false" >> "$file"
        echo "Hiding $app..."
    done
