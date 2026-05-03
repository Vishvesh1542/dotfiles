import os
import random
import subprocess
import sys
import time


# Check if we have installer dependencies
def bootstrap():
    VENV_DIR = "/tmp/myinstaller"
    if sys.prefix == VENV_DIR:
        return

    if not os.path.exists(VENV_DIR):
        print("--- Creating installer environment ---")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

        print("--- Installing UI libraries ---")
        pip_path = os.path.join(VENV_DIR, "bin", "pip")
        subprocess.run([pip_path, "install", "questionary", "rich"], check=True)

    python_executable = os.path.join(VENV_DIR, "bin", "python")
    os.execv(python_executable, [python_executable] + sys.argv)


def check_distribution():
    result = run_void("pacman --help")
    if result.returncode == 0:
        return True
    else:
        return False


def print_info(text):
    console.log(f"[bold green][ Info ]    [white]{text}")


def print_warning(text):
    console.log(f"[bold yellow][ Warning ] [white]{text}")


def print_error(text):
    console.log(f"[bold red][ Error ]  [white] {text}")


def run_void(cmd):
    return subprocess.run(
        cmd,
        capture_output=False,
        text=True,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def random_wait(s=0.1, e=0.5):
    time.sleep(random.uniform(s, e))


def check_github_repo():
    if os.path.isdir(f"{os.path.expanduser('~')}/.files"):
        print_info("Repo found at ~/.files")
        random_wait(0.3, 0.6)
        os.chdir(f"{os.path.expanduser('~')}/.files")

        local_hash = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        )

        remote_hash = (
            subprocess.check_output(["git", "rev-parse", "@{u}"]).decode().strip()
        )

        if local_hash == remote_hash:
            random_wait()
            print_info("Repo up to date with remote")
        else:
            print_warning("Updates available at remote\n")
            random_wait()

            do_update = questionary.confirm(
                message="Update local repo?",
                qmark="",
            ).ask()

            if do_update:
                print_info("Updating repo.")
                with console.status("[bold yellow] Updating repo"):
                    run_void("git pull")
                    random_wait()

        return True

    else:
        print_warning("Repo not found at ~/.files.")

        do_clone = questionary.confirm(
            message="Confirm clone to ~/.files",
            qmark="",
        ).ask()

        if not do_clone:
            raise Exception("Cannot continue without cloning repo.")

        else:
            with console.status("[bold yellow] Cloning repo..."):
                run_void(
                    f"git clone https://github.com/Vishvesh1542/dotfiles {os.path.expanduser('~')}/.files"
                )
                random_wait(0.05, 0.2)
            return True


def link_dotfiles():
    check_github_repo()
    all_folders = os.listdir(f"{os.path.expanduser('~')}/.files/")

    with console.status("Linking apps") as status:
        for t in all_folders:
            src_path = f"{os.path.expanduser('~')}/.files/" + t
            dest_path = f"{os.path.expanduser('~')}/.config/" + t
            if os.path.isdir(src_path) and t not in [
                "screenshots",
                ".git",
            ]:
                status.update(f"Linking {t}")
                random_wait()

                if os.path.islink(dest_path):
                    if os.path.realpath(dest_path) == os.path.realpath(src_path):
                        continue

                does_config_exist = os.path.isdir(
                    f"{os.path.expanduser('~')}/.config/" + t
                )

                confirmed = True
                if does_config_exist:
                    status.stop()
                    confirmed = questionary.confirm(
                        f"{t} config already exists. Continue?",
                        qmark="",
                    ).ask()
                    status.start()

                    if confirmed:
                        if not os.path.isdir(
                            os.path.expanduser("~") + "/.files.backups/"
                        ):
                            os.mkdir(os.path.expanduser("~") + "/.files.backups/")

                        run_void(
                            f"mv {os.path.expanduser('~') + '/.config/' + t} {os.path.expanduser('~') + '/.files.backups/' + t}"
                        )

                if confirmed:
                    run_void(
                        f"ln -snf {os.path.expanduser('~') + '/.files/' + t} {os.path.expanduser('~') + '/.config/' + t}"
                    )


def unlink_dotfiles():
    all_folders = os.listdir(f"{os.path.expanduser('~')}/.files/")

    with console.status("Unlinking apps") as status:
        for t in all_folders:
            src_path = f"{os.path.expanduser('~')}/.files/" + t
            dest_path = f"{os.path.expanduser('~')}/.config/" + t

            if os.path.isdir(src_path) and t not in [
                "screenshots",
                ".git",
            ]:
                if os.path.islink(dest_path):
                    if os.path.realpath(dest_path) == os.path.realpath(src_path):
                        status.update(f"Unlinking {t}")
                        random_wait()
                        run_void(f"rm {os.path.expanduser('~') + '/.config/' + t}")

    if os.path.isdir(f"{os.path.expanduser('~')}/.files.backups/"):
        replace_dotfiles = questionary.confirm(
            "Backups found at .files.backups/. Replace them?",
            qmark="",
        ).ask()

        if replace_dotfiles:
            with console.status("Replacing backups") as status:
                for file in os.listdir(f"{os.path.expanduser('~')}/.files.backups/"):
                    try:
                        status.update(f"Replacing {file}")
                        random_wait()
                        run_void(
                            f"mv {os.path.expanduser('~') + '/.files.backups/' + file} {os.path.expanduser('~') + '/.config/' + file}"
                        )
                    except Exception:
                        print_warning(f"Something went wrong when moving {file}")

    remove_folder = questionary.confirm(
        "Remove ~/.files/ ?", qmark="", default=False
    ).ask()

    if remove_folder:
        if os.path.isdir(f"{os.path.expanduser('~')}/.files/"):
            try:
                run_void(f"rm  -r {os.path.expanduser('~') + '/.files/'}")
            except Exception:
                print_warning(
                    "Something went wrong when deleting folder. Please remove it manually"
                )


def install_tools():
    apps_needed = ["git", "base-devel"]

    with console.status("Installing basic apps...") as status:
        for app in apps_needed:
            status.update(f"Installing {app}")
            run_void(f"sudo pacman -S {app} --needed --noconfirm")

    result = run_void("pacman -Qq yay")
    if result.returncode != 0:
        print_info("Installing yay")
        os.chdir("/tmp")
        run_void("git clone https://aur.archlinux.org/yay-bin.git")
        os.chdir("/tmp/yay-bin")
        run_void("makepkg -si")


def set_tweaks():
    with console.status("Adding personal tweaks") as status:
        if not os.path.isdir(
            f"{os.path.expanduser('~')}/.local/share/icons/Adwaita-blue"
        ):
            try:
                os.chdir("/tmp/")
                if os.path.isdir("/tmp/Adwaita-colors"):
                    print_info("/tmp/Adwaita-colors found. Deleting in 5 seconds")
                    status.update("Waiting...")
                    random_wait(4.5, 5.5)
                    run_void("sudo rm -r /tmp/Adwaita-colors")

                status.update("Cloning Adwaita-colors")
                run_void("git clone https://github.com/dpejoh/Adwaita-colors")

                os.chdir("/tmp/Adwaita-colors")

                status.update("Running setup script for Adwaita-colors")
                run_void("./setup -i")

                status.update("Setup morewaita")
                run_void("./morewaita.sh")
            except Exception as e:
                print_error(f"Something went wrong cloning Adwaita-colors. {e}")

        status.update("Hiding useless icons")
        random_wait()
        if not os.path.isdir(f"{os.path.expanduser('~')}/.local/share/applications"):
            os.mkdir(f"{os.path.expanduser('~')}/.local/share/applications")

        run_void("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")

        apps = [
            "avahi-discover",
            "bssh",
            "bvnc",
            "qv4l2",
            "qvidcap",
            "nvim",
            "org.freedesktop.IBus.Setup",
        ]
        base_path = "/usr/share/applications/"

        for app in apps:
            file_path = base_path + app + ".desktop"
            status.update(f"Deleting {app}")
            run_void(f"sudo rm {file_path}")


def install_apps():
    # Checking yay
    de_tools = [
        "brightnessctl",
        # "swaync",
        # "swayidle",
        "playerctl",
        "wlsunset",
        "niri",
        "xwayland-satellite",
        "bluetui",
        "polkit-gnome",
        "xdg-desktop-portal-gnome",
        "gdm",
        "zed",
        "fish",
        "imagemagick",
    ]

    common_apps = [
        "fastfetch",
        "nvim",
        "adw-gtk-theme",
        "loupe",
        "papers",
        "fzf",
        "resources",
        "showtime",
        # GST needed for showtime
        "gst-plugins-base",
        "gst-plugins-good",
        "gst-plugins-bad",
        "gst-plugins-ugly",
        "gst-libav",
        # "openrgb",
        "nautilus",
        "ghostty",
    ]

    yay_apps = [
        # "swaylock-effects-improved-git",
        # "vicinae-bin",
        "morewaita-icon-theme",
        # "awww-bin",
        "envycontrol",
        # "opentabletdriver",
        "walker-bin",
        "elephant-desktopapplications",
        "zen-browser-bin",
    ]

    with console.status("Installing apps") as status:
        for app in de_tools + common_apps:
            status.update(f"Installing {app}")
            run_void(f"sudo pacman -S --needed --noconfirm {app}")

        for app in yay_apps:
            status.update(f"Installing {app} (AUR)")
            run_void(f"yay -S --needed --noconfirm {app}")

    print_info("Please change your shell by running 'chsh'")


def install():
    # Start of empty
    print("\033[2J\033[H", end="", flush=True)
    subprocess.run(["sudo", "-v"], check=True)

    install_tools()

    if not check_distribution():
        return print_error("Only Arch linux is supported")

    choice = questionary.select(
        "Do what?",
        choices=[
            "Setup computer",
            "Set tweaks",
            "Install apps",
            "Install dotfiles",
            "Uninstall dotfiles",
        ],
        style=questionary.Style(
            [
                ("pointer", "fg:red bold"),
                ("highlighted", "fg:red bold"),
                ("selected", "fg:green"),
            ]
        ),
        instruction=" ",
        qmark="",
        show_selected=False,
    ).ask()

    if not choice:
        return print_info("No choice provided. Exitting..")

    if choice == "Setup computer":
        print_info("Setting up this new installtion")
        random_wait(0.5, 1)
        install_apps()
        link_dotfiles()
        set_tweaks()

    if choice == "Install apps":
        print_info("Installing useful apps")
        random_wait(0.4, 0.8)
        install_apps()

    elif choice == "Install dotfiles":
        print_info("Setting up dotfiles")
        random_wait(0.4, 0.8)
        link_dotfiles()

    elif choice == "Uninstall dotfiles":
        print_info("Removing dotfiles")
        random_wait(0.4, 0.8)
        unlink_dotfiles()

    elif choice == "Set tweaks":
        print_info("Setting up personal tweaks")
        random_wait(0.4, 0.8)
        set_tweaks()


if __name__ == "__main__":
    bootstrap()

    import questionary
    from rich.console import Console

    global console
    console = Console()

    try:
        install()
    except Exception as e:
        with open("/tmp/archinstaller_error_logs.txt", "w") as f:
            f.write(str(e))
        print_error(f"{e}. Logs written to /tmp/archinstaller_error_logs.txt")
