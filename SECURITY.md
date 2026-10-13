# Security and API keys

- Never commit `.env`, API keys, access tokens, chat data, logs, or personal attachments.
- Use your own NVIDIA API key and your own Tavily API key. Do not expect the project author to provide credentials.
- If a key is exposed, revoke it with its provider and create a replacement.
- Publicly distributed client applications cannot keep user-provided API keys secret from the person using that device. EldhoAi loads keys from local configuration instead of embedding the author's keys in the app.
- Report security concerns privately to the project maintainer through a contact method published on the maintainer's GitHub profile. Do not post secrets or personal chat data in issues.
