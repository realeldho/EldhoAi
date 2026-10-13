# Publish EldhoAi to GitHub (Windows)

This folder is a GitHub-ready source repository. It intentionally does **not** include `.env`, personal chats/attachments, `.venv`, `build/`, `dist/`, or a compiled installer.

## 1. Extract the repository bundle

Extract `EldhoAi_GitHub_Release.zip` to a folder you can find, for example `Desktop\EldhoAi_GitHub_Release`.

## 2. Install GitHub Desktop and sign in

Download GitHub Desktop from its official site: https://desktop.github.com/ and sign in to your GitHub account.

## 3. Create the local repository

In GitHub Desktop, select **File → New repository**. Use the extracted source folder as the repository location if the dialog allows selecting it, name it `EldhoAi`, and do not overwrite its existing `README.md`, `.gitignore`, or `LICENSE.txt`. If Desktop requires a new folder, create the repository first and copy the bundle's files into that new repository folder, allowing the existing files to replace only matching starter files.

Alternatively, from a terminal opened in the extracted folder, run:

```powershell
git init -b main
git add .
git status --short
git commit -m "Publish EldhoAi v1.0.0 source"
```

Review `git status --short` before committing. **Never commit `.env`, `data/`, `dist/`, `build/`, or personal attachments.** Then create a new **Public** repository named `EldhoAi` on GitHub, without adding a second README, .gitignore, or license, and follow GitHub's “push an existing repository” instructions to connect and push this local repository.

## 4. Publish the installer for everyone to download

The source repository by itself isn't the Windows installer. After the repository is public, open its **Releases** page and draft a release named `v1.0.0`. Upload your locally built `dist\EldhoAi_Setup_1.0.0.exe` as a release asset. If you have changed source files since your last successful build, rebuild the portable folder and recompile the installer first so the installer corresponds to the source release.

## 5. Secrets checklist before publishing

- `.env` is not part of this bundle.
- User data and build output are excluded through `.gitignore`.
- Each user must provide their own NVIDIA and Tavily API keys.
- If an API key has ever been committed to Git history, deleting the file in a later commit is not sufficient: revoke/rotate the key and clean the history before making the repo public.
