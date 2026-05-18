# GNOME Pywalfox Theme

`gnome-pywalfox-theme` is a small patcher for systems that already have:

1. `firefox-gnome-theme`
2. Pywalfox and its browser extension

It keeps Firefox GNOME Theme's layout, but changes its color layer so GNOME theme variables follow the live browser-theme variables that Pywalfox updates. When Pywalfox refreshes after a wallpaper/color change, the GNOME-styled browser follows the new colors without regenerating this patch.

## What Gets Patched

The patcher changes the installed Firefox GNOME Theme at `/usr/lib/firefox-gnome-theme`:

- copies `pywalfox-colors.css` to `theme/colors/pywalfox.css`
- imports that file from `theme/gnome-theme.css` after Firefox GNOME Theme's adaptive-color extension layer
- imports that same color layer from `userContent.css` after the internal page styles so Pywalfox's new-tab colors remain authoritative there too

No profile files are changed. The browser profile must already be set up for Firefox GNOME Theme in the normal way.

## Why This Works

Pywalfox updates Firefox browser-theme fields such as:

- frame/background
- toolbar
- toolbar field
- popup
- sidebar
- selected tab
- accent/highlight

Firefox exposes those as live CSS variables in browser chrome. The patch maps those variables onto Firefox GNOME Theme's `--gnome-*` color variables while leaving its layout CSS alone.

## Manual Use

Patch a disposable copy:

```sh
cp -a /usr/lib/firefox-gnome-theme /tmp/firefox-gnome-theme
./patch-gnome-firefox-theme /tmp/firefox-gnome-theme
```

Patch the installed theme:

```sh
sudo ./patch-gnome-firefox-theme
```

Remove the patch from an installed or disposable theme tree:

```sh
sudo ./patch-gnome-firefox-theme --remove
```

Restart the full browser process after installing, upgrading, or removing the patch. Future Pywalfox color updates are live browser-theme updates and do not require rerunning the patcher.

## Package Flow

The package installs:

- `/usr/bin/gnome-pywalfox-theme-patch`
- `/usr/share/gnome-pywalfox-theme/pywalfox-colors.css`
- `/usr/share/libalpm/hooks/90-gnome-pywalfox-theme.hook`

The pacman hook reapplies the patch whenever `firefox-gnome-theme` or `firefox-gnome-theme-git` is installed or upgraded.

Removing `gnome-pywalfox-theme` removes its imports and copied color file from the installed Firefox GNOME Theme.

## License

`gnome-pywalfox-theme` is licensed under MPL-2.0.
