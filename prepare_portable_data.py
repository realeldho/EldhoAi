"""Rebase saved EldhoAi image attachment paths in a copied data directory."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: prepare_portable_data.py SOURCE_DATA DESTINATION_DATA")
        return 2

    source_data = Path(sys.argv[1]).resolve()
    destination_data = Path(sys.argv[2]).resolve()
    chats_file = destination_data / "chats.json"
    destination_attachments = destination_data / "attachments"

    if not chats_file.is_file():
        print("No copied chats.json found; nothing to migrate.")
        return 0

    try:
        with chats_file.open("r", encoding="utf-8") as handle:
            chats = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not read copied chat history: {error}")
        return 1

    if not isinstance(chats, list):
        print("Copied chat history is not a list; image paths were not modified.")
        return 0

    updates = 0
    source_attachments = (source_data / "attachments").resolve()

    for chat in chats:
        if not isinstance(chat, dict):
            continue
        messages = chat.get("messages", [])
        if not isinstance(messages, list):
            continue
        for message in messages:
            if not isinstance(message, dict):
                continue
            images = message.get("image_paths", [])
            if not isinstance(images, list):
                continue
            for image in images:
                if not isinstance(image, dict):
                    continue
                old_value = image.get("path")
                if not isinstance(old_value, str) or not old_value:
                    continue
                try:
                    old_path = Path(old_value).resolve()
                    old_path.relative_to(source_attachments)
                except (OSError, ValueError):
                    # Don't rewrite files that are outside the project's managed attachments folder.
                    continue

                new_path = destination_attachments / old_path.name
                if new_path.is_file() and str(new_path) != old_value:
                    image["path"] = str(new_path)
                    updates += 1

    if updates:
        temporary = chats_file.with_suffix(".json.tmp")
        try:
            with temporary.open("w", encoding="utf-8") as handle:
                json.dump(chats, handle, indent=4, ensure_ascii=False)
            os.replace(temporary, chats_file)
        except OSError as error:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            print(f"Could not update image attachment paths: {error}")
            return 1

    print(f"Portable data prepared. Updated {updates} saved image path(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
