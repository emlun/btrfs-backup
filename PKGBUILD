# Maintainer: Emil Lundberg <emil@emlun.se> (emlun)

pkgname='btrfs-backup'
pkgver='0.3.0'
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
  'btrfs-backup.timer'
  'btrfs-backup.target'
  'btrfs-send.service'
  'btrfs-snapshot.service'
  '90-btrfs-backup.sudoers.conf'
)
sha1sums=('ff007ce11f3ff7964f1a5b04202c4e95b5c82c85'
          '923bb88866551b2a6ef8e117504e882f9ca902f1'
          '36561704fa5090643fcc0d47ca1509456e68e01f'
          'a7b28d983f95a14e4bbab37c02b960b16493637f'
          'f9db89b94e2ed40ff424c253cb403d7de4634ddb'
          '2b1a196ec2b13f5dbdc4482d04a0087ab2fdf175'
          'c8f662899c1dbc54a5df8ac281040131838a6fca')

package() {
  install -d -m 755 "${pkgdir}/usr/lib/systemd/system/timers.target.wants"
  install -d -m 750 "${pkgdir}/etc/sudoers.d"
  install -D -m 444 "${srcdir}/LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
  install -D -m 444 "${srcdir}"/*.service "${srcdir}"/*.target "${srcdir}"/*.timer "${pkgdir}/usr/lib/systemd/system"
  ln -s ../btrfs-backup.timer "${pkgdir}/usr/lib/systemd/system/timers.target.wants/btrfs-backup.timer"
  install -D -m 440 "${srcdir}"/90-btrfs-backup.sudoers.conf "${pkgdir}/etc/sudoers.d/90-btrfs-backup"
}
