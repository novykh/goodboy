# goodboy for Codex

## Prerequisites

- Git

## Installation

1. Clone goodboy:

   ```bash
   git clone https://github.com/novykh/goodboy.git ~/.config/goodboy
   ```

2. Symlink the skills directory so Codex can discover them:

   ```bash
   mkdir -p ~/.agents/skills
   ln -sf ~/.config/goodboy/skills ~/.agents/skills/goodboy
   ```

   **Windows (PowerShell as Administrator):**
   ```powershell
   New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills\goodboy" -Target "$env:USERPROFILE\.config\goodboy\skills"
   ```

## Verification

In a Codex session, you should see goodboy skills available. Try saying:
- "goodboy mode" or "I don't know code" to activate behavior-first mode

## Updating

```bash
cd ~/.config/goodboy && git pull
```

## Uninstalling

```bash
rm ~/.agents/skills/goodboy
rm -rf ~/.config/goodboy
```
