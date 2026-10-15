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

The bridge maps colors by element: popovers use Pywalfox's popup colors,
entries use its field colors, and cards use its new-tab card color. GNOME
Theme supplies the Adwaita borders, shadows, and control states.

Pywalfox remains the color source. This package does not read your GTK
stylesheet. To match a customized GNOME Web palette exactly, configure
Pywalfox with the same surface, text, and accent colors as your GTK theme.

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

## Color compatibility

Version 0.1.5 supports the current Firefox color variable names and keeps
fallbacks for older names. The bridge only overrides browser colors while
a browser theme is active. With no browser theme, GNOME Theme supplies the colors.
New-tab overrides apply only when Firefox exposes themed new-tab colors.

| GNOME element | Pywalfox / Firefox color source |
| --- | --- |
| Window, header, tab strip | Frame background and frame text |
| Address and search entries | Toolbar field background and text |
| Menus, popovers, address suggestions | Popup background and text |
| Cards | New-tab card background, with toolbar background as fallback |
| Sidebars | Sidebar background |
| Selected tab | Tab-line color (also Pywalfox's selected-tab color by default) |
| Accent, focus, loading indicator | Tab-loading color (Pywalfox's primary accent by default) |

GNOME Theme reuses Firefox's native selection and selected-tab variables for
its own output. The bridge reads independent inputs for those colors to
avoid circular CSS variables and empty colors. Palette changes continue to
apply live without regenerating the bridge.

## Development checks

Run the offline patcher tests and shell checks:

```sh
python tests/test_patcher.py
shellcheck patch-gnome-firefox-theme
bash -n PKGBUILD gnome-pywalfox-theme.install
```

To check resolved colors in an isolated headless Firefox profile, pass a
complete Firefox GNOME Theme checkout or installed tree:

```sh
python tests/test_colors.py --theme-dir /usr/lib/firefox-gnome-theme
```

The browser tests require Python 3 and Firefox with Marionette support. They
create and remove a temporary profile; they do not use your personal profile.
An optional `--firefox librewolf` checks LibreWolf, and `--screenshot PATH`
saves a screenshot of the test profile.

## The Vibe

I just wanted to make these two projects work together so this is my Frankenstein.
I will try to keep up on maintaining this if something breaks from an update.
If you notice a bug or anything leave an issue!

## License

Licensed under **MPL-2.0**.
