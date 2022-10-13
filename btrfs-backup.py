#!/usr/bin/env python3

import os
import socket
import subprocess
import sys
import time

from datetime import datetime


KEEP_NUM = 30
THIS_HOSTNAME = socket.gethostname()
REMOTE_HOST = 'btrfs-backup'
REMOTE_DIR = os.path.join('/btrfs-snapshots', THIS_HOSTNAME)
MAX_RETRY_DELAY = 60


def await_network():
    print('Checking network connectivity...')
    delay_s = 5
    while True:
        check_connection = subprocess.run(
            ['ssh', REMOTE_HOST, 'date', '-Is'],
            timeout=10,
        )
        if check_connection.returncode == 0:
            break
        else:
            print(f'Failed to connect to server; retrying in {delay_s}s...')
            time.sleep(delay_s)
            delay_s = min(delay_s * 2, MAX_RETRY_DELAY)
    print()


def drop_last(lst, ndrop):
    return [i for i in lst[0:(len(lst) - ndrop)]]


def exit_unless(proc, desc):
    if proc.returncode != 0:
        print(f'{desc} failed with status: {proc.returncode}')
        sys.exit(1)


def take_snapshot(volume, snapshots_dir, snapshot_prefix):
    print(f'Taking snapshot of {volume}')
    timestamp = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    snapshot_path = os.path.join(snapshots_dir, snapshot_prefix + timestamp)
    exit_unless(
        subprocess.run([
            'sudo', 'btrfs', 'subvolume',
            'snapshot', '-r', volume, snapshot_path,
        ]),
        'btrfs subvolume snapshot',
    )
    print(f'Created snapshot: {snapshot_path}')

    print('Removing old snapshots...')
    local_snaps = sorted(
        fn for fn in os.listdir(snapshots_dir)
        if fn.startswith(snapshot_prefix)
    )
    delete_local_subvols([
        os.path.join(snapshots_dir, fn)
        for fn in drop_last(local_snaps, KEEP_NUM)
    ])


def delete_local_subvols(subvol_paths):
    print()
    print(f'Deleting {len(subvol_paths)} local snapshots:')
    for d in subvol_paths:
        print(d)

    exit_unless(
        subprocess.run([
            'sudo', 'btrfs', 'subvolume', 'delete', *subvol_paths]),
        'btrfs subvolume delete',
    )


def delete_remote_subvols(subvol_paths):
    print()
    print(f'Deleting {len(subvol_paths)} remote snapshots:')
    for d in subvol_paths:
        print(d)

    exit_unless(
        subprocess.run([
            'ssh', REMOTE_HOST,
            'sudo', 'btrfs', 'subvolume', 'delete', *subvol_paths,
        ]),
        'ssh btrfs subvolume delete',
    )


def send(snapshots_dir, snapshot_prefix):
    print()
    print(f'Snapshot directory: {snapshots_dir} prefix: {snapshot_prefix}')
    print()
    remote_incomplete = [
        fn for fn in subprocess.run(
            ['ssh', REMOTE_HOST, 'ls', '-1', REMOTE_DIR],
            stdout=subprocess.PIPE,
            encoding='utf-8').stdout.split()
        if fn.startswith(snapshot_prefix) and fn.endswith('.incomplete')
    ]
    if len(remote_incomplete) > 0:
        print('Incomplete shapshots:')
        for s in remote_incomplete:
            print(s)
        incomplete_snapshots = [
            os.path.join(REMOTE_DIR, fn.removesuffix('.incomplete'))
            for fn in remote_incomplete
        ]
        delete_remote_subvols(incomplete_snapshots)
        exit_unless(
            subprocess.run([
                'ssh', REMOTE_HOST,
                'sudo', 'rm', *[
                    os.path.join(REMOTE_DIR, fn)
                    for fn in remote_incomplete
                ],
            ]),
            'ssh rm incomplete',
        )
    else:
        print('No incomplete snapshots.')

    remote_snaps = set(subprocess.run(
        ['ssh', REMOTE_HOST, 'ls', '-1', REMOTE_DIR],
        stdout=subprocess.PIPE,
        encoding='utf-8').stdout.split())
    local_snaps = set(os.listdir(snapshots_dir))

    shared_snaps = sorted(local_snaps.intersection(remote_snaps))
    new_snaps = sorted(local_snaps.difference(remote_snaps))

    print()
    if len(new_snaps) > 0:
        print('New shapshots:')
        for s in new_snaps:
            print(s)
    else:
        print('No new snapshots.')

    for fn in new_snaps:
        print()
        print(f'Sending {fn}')

        full_filename = os.path.join(snapshots_dir, fn)
        incomplete_filename = os.path.join(REMOTE_DIR, f'{fn}.incomplete')
        clone_srcs = [
            ['-c', os.path.join(snapshots_dir, sfn)]
            for sfn in shared_snaps
        ]
        clone_srcs = [arg for pair in clone_srcs for arg in pair]

        exit_unless(
            subprocess.run([
                'ssh', REMOTE_HOST,
                'sudo', 'touch', f"'{incomplete_filename}'",
            ]),
            'ssh touch incomplete',
        )

        btrfs_send = subprocess.Popen(
            ['sudo', 'btrfs', 'send', *clone_srcs, full_filename],
            stdout=subprocess.PIPE)
        btrfs_receive = subprocess.Popen([
            'ssh', REMOTE_HOST,
            'sudo', 'btrfs', 'receive', os.path.join(REMOTE_DIR, '')
        ], stdin=btrfs_send.stdout)

        btrfs_send.wait()
        btrfs_receive.wait()

        exit_unless(btrfs_send, 'btrfs send')
        exit_unless(btrfs_receive, 'ssh btrfs receive')

        exit_unless(
            subprocess.run([
                'ssh', REMOTE_HOST,
                'sudo', 'rm', f"'{incomplete_filename}'",
            ]),
            'ssh rm incomplete',
        )

        shared_snaps.append(fn)

        print(f'Finished sending {fn}')

    print()
    print('Cleaning up remote snapshots...')
    remote_snaps = sorted([
        fn for fn in
        subprocess.run(
            ['ssh', REMOTE_HOST, 'ls', '-1', REMOTE_DIR],
            stdout=subprocess.PIPE,
            encoding='utf-8').stdout.split()
        if fn.startswith(snapshot_prefix)
    ])
    if len(remote_snaps) > KEEP_NUM:
        delete_remote_subvols([
            os.path.join(REMOTE_DIR, fn)
            for fn in drop_last(remote_snaps, KEEP_NUM)
        ])
    else:
        print('Nothing to delete!')


def main():
    take_snapshot('/', '/snapshots', 'root-')
    take_snapshot('/home', '/home/snapshots', 'home-')

    await_network()
    send('/snapshots', 'root-')
    send('/home/snapshots', 'home-')


if __name__ == '__main__':
    main()
