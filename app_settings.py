import json
import os


# ============================================================
# ELDHOAI SETTINGS STORAGE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

SETTINGS_FILE = os.path.join(
    DATA_DIR,
    "settings.json"
)


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_SETTINGS = {

    # AI configuration

    "model": "z-ai/glm-5.3-flash",

    "reasoning_effort": "low",

    "temperature": 0.5,

    "max_tokens": 1024,


    # Appearance

    "appearance": "dark",

    "ui_scale": 1.0,


    # Chat behavior

    "enter_to_send": True,

    "auto_scroll": True,

    "render_markdown": True,

}


# ============================================================
# CREATE STORAGE DIRECTORY
# ============================================================

def ensure_settings_directory():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )


# ============================================================
# VALIDATE SETTINGS
# ============================================================

def validate_settings(settings):

    validated = DEFAULT_SETTINGS.copy()


    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = settings.get(
        "model",
        DEFAULT_SETTINGS["model"]
    )

    if isinstance(model, str) and model.strip():

        validated["model"] = model.strip()


    # --------------------------------------------------------
    # Reasoning effort
    # --------------------------------------------------------

    reasoning = settings.get(
        "reasoning_effort",
        DEFAULT_SETTINGS["reasoning_effort"]
    )

    if reasoning in (
        "low",
        "high",
        "max"
    ):

        validated["reasoning_effort"] = reasoning


    # --------------------------------------------------------
    # Temperature
    # --------------------------------------------------------

    try:

        temperature = float(
            settings.get(
                "temperature",
                DEFAULT_SETTINGS["temperature"]
            )
        )

        if 0.0 <= temperature <= 1.0:

            validated["temperature"] = temperature

    except (
        TypeError,
        ValueError
    ):

        pass


    # --------------------------------------------------------
    # Maximum response tokens
    # --------------------------------------------------------

    try:

        max_tokens = int(
            settings.get(
                "max_tokens",
                DEFAULT_SETTINGS["max_tokens"]
            )
        )

        if max_tokens in (
            512,
            1024,
            2048,
            4096
        ):

            validated["max_tokens"] = max_tokens

    except (
        TypeError,
        ValueError
    ):

        pass


    # --------------------------------------------------------
    # Appearance
    # --------------------------------------------------------

    appearance = settings.get(
        "appearance",
        DEFAULT_SETTINGS["appearance"]
    )

    if appearance in (
        "dark",
        "light",
        "system"
    ):

        validated["appearance"] = appearance


    # --------------------------------------------------------
    # UI scaling
    # --------------------------------------------------------

    try:

        ui_scale = float(
            settings.get(
                "ui_scale",
                DEFAULT_SETTINGS["ui_scale"]
            )
        )

        if ui_scale in (
            0.8,
            0.9,
            1.0,
            1.1,
            1.2
        ):

            validated["ui_scale"] = ui_scale

    except (
        TypeError,
        ValueError
    ):

        pass


    # --------------------------------------------------------
    # Boolean options
    # --------------------------------------------------------

    for key in (
        "enter_to_send",
        "auto_scroll",
        "render_markdown"
    ):

        value = settings.get(
            key,
            DEFAULT_SETTINGS[key]
        )

        if isinstance(value, bool):

            validated[key] = value


    return validated


# ============================================================
# LOAD SETTINGS
# ============================================================

def load_settings():

    ensure_settings_directory()

    if not os.path.exists(
        SETTINGS_FILE
    ):

        return DEFAULT_SETTINGS.copy()


    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            stored_settings = json.load(
                file
            )


        if not isinstance(
            stored_settings,
            dict
        ):

            return DEFAULT_SETTINGS.copy()


        return validate_settings(
            stored_settings
        )


    except (
        json.JSONDecodeError,
        OSError
    ):

        return DEFAULT_SETTINGS.copy()


# ============================================================
# SAVE SETTINGS
# ============================================================

def save_settings(settings):

    ensure_settings_directory()

    validated = validate_settings(
        settings
    )

    temporary_file = SETTINGS_FILE + ".tmp"


    try:

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                validated,
                file,
                indent=4,
                ensure_ascii=False
            )


        # Replace the existing file safely.

        os.replace(
            temporary_file,
            SETTINGS_FILE
        )

        return True


    except OSError as error:

        print(
            f"Could not save EldhoAi settings: {error}"
        )


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
# UPDATE INDIVIDUAL SETTINGS
# ============================================================

def update_settings(**changes):

    settings = load_settings()

    settings.update(
        changes
    )

    return save_settings(
        settings
    )


# ============================================================
# RESET SETTINGS
# ============================================================

def reset_settings():

    return save_settings(
        DEFAULT_SETTINGS.copy()
    )


# ============================================================
# TEST SETTINGS
# ============================================================

if __name__ == "__main__":

    print("=" * 50)

    print("       EldhoAi Settings Test")

    print("=" * 50)

    print()


    # Load current settings.

    settings = load_settings()


    print("Current settings:")

    print(
        json.dumps(
            settings,
            indent=4
        )
    )


    print()


    # Save settings.

    success = save_settings(
        settings
    )


    if success:

        print(
            "Settings saved successfully!"
        )

        print()

        print(
            f"Settings file: {SETTINGS_FILE}"
        )

    else:

        print(
            "Failed to save settings."
        )

    print()

    print("=" * 50)