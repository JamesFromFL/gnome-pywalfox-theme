# Maintainer: James

pkgname=gnome-pywalfox-theme
pkgver=0.1.5
pkgrel=1
pkgdesc='Pywalfox color patcher for firefox-gnome-theme'
arch=('any')
url='https://github.com/JamesFromFL/gnome-pywalfox-theme'
license=('MPL-2.0')
optdepends=(
	'firefox-gnome-theme: base theme to patch'
	'firefox-gnome-theme-git: development version of the base theme to patch'
)
install='gnome-pywalfox-theme.install'
source=(
	'patch-gnome-firefox-theme'
	'pywalfox-colors.css'
	'90-gnome-pywalfox-theme.hook'
	'LICENSE'
)
sha256sums=(
	'3a0196d939310a05fd74df3f6382f7f789b9d750db4e5423ccd7a5e54783344f'
	'5528389fb966493ec44bd8b28f102bce97c76b3725d0fd0029cf0a51e3901aac'
	'1b79206a28ee5f1648d63ac8ca215009c637d2a741dad402c30d5d1e6275cb9c'
	'1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5'
)

package() {
	install -Dm755 "$srcdir/patch-gnome-firefox-theme" "$pkgdir/usr/bin/gnome-pywalfox-theme-patch"
	install -Dm644 "$srcdir/pywalfox-colors.css" "$pkgdir/usr/share/gnome-pywalfox-theme/pywalfox-colors.css"
	install -Dm644 "$srcdir/90-gnome-pywalfox-theme.hook" "$pkgdir/usr/share/libalpm/hooks/90-gnome-pywalfox-theme.hook"
	install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
