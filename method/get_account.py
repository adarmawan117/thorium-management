import os
import sqlite3
import method.directory as mydir

from entity.facebook import AkunFacebook


def get_account_facebook(nama) -> AkunFacebook:
    result = None
    try:
        file_path = os.path.join(mydir.database_dir, 'db_facebook.db')
        with sqlite3.connect(file_path) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM akun WHERE nama = ?', (nama,))

            rows = cursor.fetchall()

            for row in rows:
                result = AkunFacebook(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4]
                )

            cursor.close()

    except sqlite3.Error as e:
        print(f"Error: {e}")

    return result


def get_facebook_accounts() -> (list[str], list[int]):
    names = []
    codes = []
    try:
        file_path = os.path.join(mydir.database_dir, 'db_facebook.db')
        with sqlite3.connect(file_path) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM akun ORDER BY kode_profile')

            rows = cursor.fetchall()
            for row in rows:
                '''
                0 -> name
                1 -> email
                2 -> password
                3 -> tanggal_dibuat
                4 -> kode_profile   -> int
                5 -> type
                '''
                names.append(row[0])
                codes.append(int(row[4]))

            cursor.close()

    except sqlite3.Error as e:
        print(f"Error: {e}")

    return names, codes
