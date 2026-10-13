import json
import os


# ============================================================
# STORAGE LOCATION
# ============================================================

DATA_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data"
)

CHATS_FILE = os.path.join(
    DATA_FOLDER,
    "chats.json"
)


# ============================================================
# MAKE SURE STORAGE EXISTS
# ============================================================

def ensure_storage():

    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )


# ============================================================
# LOAD CHATS
# ============================================================

def load_chats():

    ensure_storage()

    if not os.path.exists(CHATS_FILE):
        return []

    try:

        with open(
            CHATS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ============================================================
# SAVE CHATS
# ============================================================

def save_chats(chats):

    ensure_storage()

    temporary_file = CHATS_FILE + ".tmp"

    try:

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                chats,
                file,
                indent=4,
                ensure_ascii=False
            )

        os.replace(
            temporary_file,
            CHATS_FILE
        )

        return True

    except OSError:

        try:

            if os.path.exists(
                temporary_file
            ):
                os.remove(
                    temporary_file
                )

        except OSError:
            pass

        return False


# ============================================================
# CREATE CHAT
# ============================================================

def create_chat():

    return {
        "id": None,
        "title": "New Chat",
        "messages": []
    }


# ============================================================
# UPDATE CHAT TITLE
# ============================================================

def update_chat_title(
    chats,
    chat_id,
    new_title
):

    for chat in chats:

        if chat.get("id") == chat_id:

            clean_title = " ".join(
                new_title.strip().split()
            )

            if not clean_title:

                clean_title = "New Chat"

            chat["title"] = clean_title

            return True

    return False


# ============================================================
# DELETE CHAT
# ============================================================

def delete_chat(
    chats,
    chat_id
):

    for index, chat in enumerate(chats):

        if chat.get("id") == chat_id:

            chats.pop(index)

            return True

    return False