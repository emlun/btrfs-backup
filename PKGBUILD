# Maintainer: Emil Lundberg <emil@emlun.se> (emlun)

pkgname='btrfs-backup'
pkgver='0.1.0'
pkgrel=1
pkgdesc="emlun's BTRFS backup system"
license=('custom:unlicense')
arch=('any')
#url='https://github.com/emlun/systemlund'
depends=(
  'btrfs-progs'
  'openssh'
  'python'
  'sudo'
)
source=(
  'LICENSE'
  'btrfs-backup.py'
  'btrfs-send.service'
  'btrfs-send.timer'
  'btrfs-snapshot.service'
  'btrfs-snapshot.timer'
  '90-btrfs-backup.sudoers.conf'
)
sha1sums=('ff007ce11f3ff7964f1a5b04202c4e95b5c82c85'
          '923bb88866551b2a6ef8e117504e882f9ca902f1'
          '7f3a92f70178ba1864f6a388d191585db15c4e7a'
          '0591f7b857650d2f553aa2a392325ba301613cc2'
          '37781bbbecee789be48ff8cdfd566d6d580c4953'
          '4d27a8ae80c62e1f78dfff8afa09046ed98bf03e'
          'c8f662899c1dbc54a5df8ac281040131838a6fca')

package() {
  install -d -m 755 "${pkgdir}/usr/lib/systemd/system" "${pkgdir}/etc/systemd/system"
  install -d -m 750 "${pkgdir}/etc/sudoers.d"
  install -D -m 444 "${srcdir}"/*.service "${srcdir}"/*.timer "${pkgdir}/usr/lib/systemd/system"
  install -D -m 440 "${srcdir}"/90-btrfs-backup.sudoers.conf "${pkgdir}/etc/sudoers.d/90-btrfs-backup"
  install -D -m 444 "${srcdir}/LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
