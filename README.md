# GNOME Pywalfox Theme

**Make firefox-gnome-theme follow your wallpaper colors.**

`gnome-pywalfox-theme` is a tiny patcher for the rice goblins who want Firefox to actually match the rest of their desktop.

You already have:

* **Firefox GNOME Theme** for that clean GNOME-style Firefox layout
* **Pywalfox** for wallpaper-based browser colors

This project glues them together.

Firefox keeps the GNOME layout.
Pywalfox brings the colors.
Your browser stops looking like it missed the memo.

## Requirements

You need to have:

* `firefox-gnome-theme` or `firefox-gnome-theme-git`
* Pywalfox
* The Pywalfox browser extension

This does **not** set up firefox-gnome-theme for you.
This does **not** configure pywalfox for you.
This is the dumb little bridge that makes them kiss.

## Install

### AUR

Install using your favorite AUR helper.

```sh
yay -S gnome-pywalfox-theme
```
The pacman hook automatically reapplies the patch whenever `firefox-gnome-theme` or `firefox-gnome-theme-git` gets installed or upgraded.

Then fully restart Firefox, LibreWolf, or whatever Firefox-based browser you are using.

### Git / makepkg

```sh
git clone https://github.com/JamesFromFL/gnome-pywalfox-theme.git
cd gnome-pywalfox-theme
makepkg -si
```

This installs the patcher, the color bridge, and the pacman hook like the AUR. Still need to fully restart your browser.

### Manual patch only

```sh
git clone https://github.com/JamesFromFL/gnome-pywalfox-theme.git
cd gnome-pywalfox-theme
sudo ./patch-gnome-firefox-theme
```

This patches the installed `firefox-gnome-theme` tree directly, but does not install the pacman hook.

## Uninstall

If installed as a package, remove it with your package manager.

```sh
yay -R gnome-pywalfox-theme
```

If you used the manual patch-only method:

```sh
cd gnome-pywalfox-theme
sudo ./patch-gnome-firefox-theme --remove
```

The uninstall removes:

- the Pywalfox color file
- the imports added to Firefox GNOME Theme
- the pacman hook, if installed as a package

Restart your browser after uninstall is done.

## What It Actually Patches

The patcher changes the installed Firefox GNOME Theme tree.

It copies:

```sh
pywalfox-colors.css
```

to:

```sh
theme/colors/pywalfox.css
```

Then it imports that file through firefox-gnome-theme’s update-safe custom import points when available:

```sh
customChrome.css
customContent.css
```

For older firefox-gnome-theme installs, it falls back to patching:

```sh
theme/gnome-theme.css
userContent.css
```

Your Firefox profile files are not touched.

## The Vibe

I just wanted to make these two projects work together so this is my Frankenstein.
I will try to keep up on maintaining this if something breaks from an update.
If you notice a bug or anything leave an issue!

## License

Licensed under **MPL-2.0**.
