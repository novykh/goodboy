# goodboy for OpenCode

## Prerequisites

- Git
- Node.js (for plugin loader)

## Installation

1. Clone goodboy:

   ```bash
   git clone https://github.com/novykh/goodboy.git ~/.config/opencode/goodboy
   ```

2. Register the plugin:

   ```bash
   mkdir -p ~/.config/opencode/plugins
   ln -sf ~/.config/opencode/goodboy/.opencode/plugins/goodboy.js ~/.config/opencode/plugins/goodboy.js
   ```

3. Symlink skills for discovery:

   ```bash
   mkdir -p ~/.config/opencode/skills
   ln -sf ~/.config/opencode/goodboy/skills ~/.config/opencode/skills/goodboy
   ```

## Usage

Once installed, goodboy skills are available in OpenCode sessions. Activate behavior-first mode by saying:
- "goodboy mode" or "I don't know code"

### Tool Mapping

Skills reference Claude Code tool names. OpenCode equivalents:

| Skill References | OpenCode Equivalent |
|-----------------|---------------------|
| `TodoWrite` | `todowrite` |
| `Skill` | skill tool |
| `Read` | `read` |
| `Write` | `write` |
| `Edit` | `edit` |
| `Bash` | `bash` |
| `Glob` | `glob` |
| `Grep` | `grep` |

## Updating

```bash
cd ~/.config/opencode/goodboy && git pull
```

## Uninstalling

```bash
rm ~/.config/opencode/plugins/goodboy.js
rm ~/.config/opencode/skills/goodboy
rm -rf ~/.config/opencode/goodboy
```
