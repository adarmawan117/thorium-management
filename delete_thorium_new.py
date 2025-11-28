import traceback

import psutil
import os
import sys
import method.directory as mydir

from method.get_account import get_facebook_accounts, get_account_facebook


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

def extract_sub_folders(thorium_base_path) -> list[str]:
    sub_folders = os.listdir(thorium_base_path)
    # print(thorium_base_path)

    sub_folder_results = []
    # Filter hanya folder yang mempunya nama "USER_DATA_"
    for sub_folder in sub_folders:
        full_path = os.path.join(thorium_base_path, sub_folder)

        if os.path.isdir(full_path) and "USER_DATA_" in full_path:
            sub_folder_results.append(full_path)

    return sub_folder_results

def get_fb_accounts(name: str) -> (list[str], list[int]):
    """
    Mengambil akun facebook<br>
    Jika name = None artinya ambil semua<br>
    Jika name tidak None, maka cari berdasarkan nama tersebut
    :param name: Boleh None atau str
    :return:
    """

    if name is None or name == "":
        names, codes = get_facebook_accounts()
    else:
        akun = get_account_facebook(name)
        names = [akun.nama]
        codes = [akun.kode_profile]

    return names, codes

def get_complete_profiles(name: str) -> list[dict]:
    thorium_base_path = os.getenv("THORIUM_PATH", mydir.thorium_dir)
    sub_folder_results = extract_sub_folders(thorium_base_path)

    # DATA AKUN FACEBOOK (nama -> kode_profile)
    names, codes = get_fb_accounts(name)
    complete_profiles = []

    # Ambil name dan kode_profile berdasarkan folder yang ditemukan
    for sub_folder in sub_folder_results:
        try:
            code_from_folder = int(sub_folder.replace(f"{thorium_base_path}\\USER_DATA_", ""))
        except ValueError as e:
            continue

        # cek apakah kodenya ditemukan didalam database
        if code_from_folder in codes:
            index = codes.index(code_from_folder)

            complete_profiles.append({
                "name": names[index],
                "kode_profile": codes[index],
                "full_path": sub_folder
            })

    return complete_profiles

def main():
    try:
        complete_profiles = get_complete_profiles()

        for profile in complete_profiles:
            print(profile)

    except:
        traceback.print_exc()
        sys.exit(-1)

def test():
    names, codes = get_facebook_accounts()
    for name, code in zip(names, codes):
        print(f"{name} -->> {code}")

if __name__ == "__main__":
    main()