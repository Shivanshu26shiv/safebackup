"""
- This script takes cyclic backups based on MAX_NO_OF_BACKUPS
- Checks latest backup repo before taking backup, if identical, it skips
- Ideally scheduled via task scheduler at every logon
- To see the latest backup, refresh windows explorer
- Ideally, only need to change variables in CAPS
"""


def are_dir_same(comparison):

    if comparison.diff_files or comparison.left_only or comparison.right_only:
        return False
    for sub_comparison in comparison.subdirs.values():
        if not are_dir_same(sub_comparison):
            return False
        
    return True


def take_local_backup():

    import fnmatch
    import distutils.dir_util
    from datetime import datetime

    creation_date_dict = {}
    for repo in os.listdir(BACKUP_TO_PARENT_REPO):
        path = BACKUP_TO_PARENT_REPO + r"\/"+repo
        if os.path.isdir(path) and fnmatch.fnmatch(repo, BACKUP_DRIVE_PREFIX+'*'):
            creation_date_dict[path] = datetime.fromtimestamp(os.stat(path).st_ctime)

    print('\ncreation_date_dict: {}'.format(creation_date_dict))

    if len(creation_date_dict) == MAX_NO_OF_BACKUPS:
        oldest_backup_repo = min(creation_date_dict, key=creation_date_dict.get)
        print('\nDeleting: {}'.format(oldest_backup_repo), '\n')
        os.system('rmdir /S /Q "{}"'.format(oldest_backup_repo))
        from time import sleep
        sleep(2)

    trial = 1
    latest_backup_repo = max(creation_date_dict, key=creation_date_dict.get, default=[])

    import filecmp

    while trial <= MAX_NO_OF_BACKUPS:

        print('trial: {}'.format(trial))
        new_repo_path = BACKUP_TO + str(trial)

        if not os.path.isdir(new_repo_path):
            if latest_backup_repo and are_dir_same(filecmp.dircmp(BACKUP_FROM, latest_backup_repo)):
                print('\nBackup FROM and TO are identical!, exiting\n')
                return
            else:
                print('\nCreating: {}'.format(new_repo_path))
                distutils.dir_util.copy_tree(BACKUP_FROM, new_repo_path)

            break

        trial += 1

    print('\nBackup completed!')

    return


if __name__ == '__main__':

    import os
    if os.name != 'nt':
        print('This is a Windows based script!')
        exit()

    import sys
    MAX_NO_OF_BACKUPS = 10
    BACKUP_FROM = sys.exec_prefix + r'\shiv'
    BACKUP_DRIVE_PREFIX = 'safebackup'
    BACKUP_TO_PARENT_REPO = r'E:\backups'
    BACKUP_TO = BACKUP_TO_PARENT_REPO + '/' + BACKUP_DRIVE_PREFIX + '1'

    take_local_backup()
