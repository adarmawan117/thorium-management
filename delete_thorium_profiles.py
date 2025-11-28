import json
import psutil
import shutil
import os
import time
import stat


def log(message):
    print(f"[INFO] {message}")


def close_all_thorium_instances():
    # Mendapatkan semua proses yang berjalan
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Memeriksa apakah proses adalah Chrome
            if proc.info['name'] == 'thorium.exe':
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def rewrite_config(json_object, path):
    with open(path, 'w') as file_baru:
        json.dump(json_object, file_baru, indent=2)


def get_profile_names(json_object):
    profile_names = [json_object['profile']['info_cache'][p]['name'] for p in get_profile_lists(json_object)]
    return profile_names


def get_profile_lists(json_object):
    profile_lists = [p for p in json_object['profile']['info_cache']]

    # Jika cuma ada satu profile, maka biarkan
    if len(profile_lists) == 1:
        return []

    profile_lists = profile_lists[1:]  # sisakan satu profile, jangan dihapus
    return profile_lists


def change_local_state(deleted_account, local_state_path) -> str:
    with open(local_state_path, 'r') as file:
        json_object = json.load(file)

    profile_lists = get_profile_lists(json_object)
    for p in profile_lists:
        if json_object['profile']['info_cache'][p]['name'] == deleted_account:
            print("Profile ditemukan")

            print(f"Menghapus profile '{deleted_account}'")
            del json_object['profile']['info_cache'][p]
            print("Profile berhasil dihapus\n")

            print("Mengurangi nilai 'profiles_created'")
            json_object['profile']['profiles_created'] -= 1

            print("Menghapus profile di 'profiles_order'")
            json_object['profile']['profiles_order'].remove(p)

            print("Merubah nilai di 'tab_stats'")
            json_object['tab_stats']['max_tabs_per_window'] -= 1
            json_object['tab_stats']['total_tab_count_max'] -= 1
            json_object['tab_stats']['window_count_max'] -= 1

            print("Merubah nilai di 'variations_google_groups'")
            del json_object['variations_google_groups'][p]

            log("Menulis ulang file Local State")
            rewrite_config(json_object, local_state_path)
            log("Selesai menulis ulang file Local State\n\n")

            return p

    else:
        print("Profile tidak ditemukan")

    return None


def unlock_folder(folder):
    for root, dirs, files in os.walk(folder):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IRWXU)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IWRITE)


def run(deleted_accounts: list[str], thorium_installation_path):
    close_all_thorium_instances()
    for deleted_account in deleted_accounts:
        local_state_path = os.path.join(thorium_installation_path, 'USER_DATA', 'Local State')

        profile_name = change_local_state(deleted_account, local_state_path)
        if profile_name is not None:
            print(profile_name)

            print(f"Menghapus folder '{profile_name}'")
            removed_path_profile = os.path.join(thorium_installation_path, 'USER_DATA', profile_name)
            unlock_folder(removed_path_profile)  # Pastikan semua file dalam folder bisa dihapus
            os.chmod(removed_path_profile, stat.S_IRWXU)  # Ubah izin folder
            shutil.rmtree(removed_path_profile)  # Hapus folder
            print(f"Berhasil menghapus folder '{profile_name}'\n\n")

        # log(json.dumps(json_object, indent=4))
        log("=================================\n")


def main():
    deleted_accounts = ["Indro Warkop"]
    thorium_installation_path = "D:\\Thorium_AVX2_130.0.6723.174"
    run(deleted_accounts, thorium_installation_path)


if __name__ == "__main__":
    main()
