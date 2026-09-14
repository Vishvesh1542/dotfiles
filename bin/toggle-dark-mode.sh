current=$(gsettings get org.gnome.desktop.interface color-scheme)

if [[ "$current" == "'prefer-dark'" ]]; then
    niri msg action do-screen-transition
    gsettings set org.gnome.desktop.interface color-scheme 'default'

else
    niri msg action do-screen-transition
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
fi
