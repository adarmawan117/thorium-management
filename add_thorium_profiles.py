import json
import psutil
import shutil
import os


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


def get_latest_index(json_object) -> int:
    profile_orders = json_object["profile"]['profiles_order']

    index_terakhir = 0
    for index in profile_orders:
        index_split = index.split(" ")
        if len(index_split) == 2:
            index_terakhir = int(index_split[1])

    return index_terakhir


def set_new_profile(json_object, new_index, profile_name):
    json_object['profile']['info_cache']['Profile ' + str(new_index)] = {
        "active_time": 0,
        "avatar_icon": "chrome://theme/IDR_PROFILE_AVATAR_30",
        "background_apps": False,
        "default_avatar_fill_color": -14737376,
        "default_avatar_stroke_color": -1,
        "force_signin_profile_locked": False,
        "gaia_given_name": "",
        "gaia_id": "",
        "gaia_name": "",
        "hosted_domain": "",
        "is_consented_primary_account": False,
        "is_ephemeral": False,
        "is_using_default_avatar": True,
        "is_using_default_name": False,
        "managed_user_id": "",
        "metrics_bucket_index": new_index + 1,
        "name": profile_name,
        "profile_color_seed": -5715974,
        "profile_highlight_color": -14737376,
        "signin.with_credential_provider": False,
        "user_name": ""
    }


def set_tab_stats(json_object, new_index):
    json_object['tab_stats'] = {
        "discards_external": 0,
        "discards_proactive": 0,
        "discards_suggested": 0,
        "discards_urgent": 0,
        "last_daily_sample": "13387010952306459",
        "max_tabs_per_window": new_index + 2,
        "reloads_external": 0,
        "reloads_proactive": 0,
        "reloads_suggested": 0,
        "reloads_urgent": 0,
        "total_tab_count_max": new_index + 2,
        "window_count_max": new_index + 1
    }


def rewrite_config(json_object, path):
    with open(path, 'w') as file_baru:
        json.dump(json_object, file_baru, indent=2)


def set_local_state(profile_name, local_state_path) -> int:
    with open(local_state_path, 'r') as file:
        json_object = json.load(file)

    latest_index = get_latest_index(json_object)
    new_index = latest_index + 1

    set_new_profile(json_object, new_index, profile_name)
    json_object['profile']['metrics']['next_bucket_index'] = new_index + 2
    json_object['profile']['profiles_created'] = new_index + 1
    json_object['profile']['profiles_order'].append(f"Profile {new_index}")
    set_tab_stats(json_object, new_index)
    json_object['variations_google_groups'][f'Profile {new_index}'] = []

    # log(json.dumps(json_object, indent=4))
    log("Menulis ulang file Local State")
    rewrite_config(json_object, local_state_path)
    log("Selesai menulis ulang file Local State\n\n")

    return new_index


def change_bookmarks(profile_name, source_path_profile):
    path = f'{source_path_profile}/Bookmarks'
    with open(path, 'r') as file:
        json_object = json.load(file)

    json_object["roots"]["bookmark_bar"]["children"][0]["name"] = profile_name
    # log(json.dumps(json_object, indent=4))
    log("Menulis ulang Bookmark")
    rewrite_config(json_object, path)
    log("Selesai menulis ulang Bookmark\n\n")


def duplicate_profile(
        profile_name: str,
        new_index: int,
        source_path_profile: str,
        destination_path_profile: str
):
    log(f"Menduplikasi {profile_name} ke Profile {new_index}")
    shutil.copytree(source_path_profile, destination_path_profile)
    log("Selesai menduplikasi profile")


def run(profile_names: list[str], thorium_installation_path):
    close_all_thorium_instances()
    for profile_name in profile_names:
        local_state_path = os.path.join(thorium_installation_path, 'USER_DATA', 'Local State')
        new_index = set_local_state(profile_name, local_state_path)

        source_path_profile = "thorium/Profile 2"
        destination_path_profile = os.path.join(thorium_installation_path, 'USER_DATA', f'Profile {new_index}')

        change_bookmarks(profile_name, source_path_profile)
        duplicate_profile(
            profile_name,
            new_index,
            source_path_profile,
            destination_path_profile
        )
        log("=================================\n")


def main():
    profile_names = ["6. Testing"]
    thorium_installation_path = "D:\\Thorium_AVX2_130.0.6723.174"
    run(profile_names)


if __name__ == "__main__":
    main()
