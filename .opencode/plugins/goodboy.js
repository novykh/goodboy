import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function stripFrontmatter(content) {
  const match = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
  return match ? match[1].trim() : content;
}

function findPluginRoot() {
  let dir = __dirname;
  while (dir !== dirname(dir)) {
    try {
      const manifest = join(dir, ".claude-plugin", "plugin.json");
      readFileSync(manifest, "utf-8");
      return dir;
    } catch {
      dir = dirname(dir);
    }
  }
  return join(__dirname, "..", "..");
}

export default async function GoodboyPlugin() {
  const pluginRoot = findPluginRoot();
  const skillPath = join(pluginRoot, "skills", "being-a-goodboy", "SKILL.md");

  let bootstrapContent;
  try {
    const raw = readFileSync(skillPath, "utf-8");
    bootstrapContent = stripFrontmatter(raw);
  } catch {
    bootstrapContent =
      "goodboy plugin loaded but could not read being-a-goodboy skill.";
  }

  const context = [
    "<EXTREMELY_IMPORTANT>",
    "You have goodboy.",
    "",
    "**Below is the full content of your 'goodboy:being-a-goodboy' skill:**",
    "",
    bootstrapContent,
    "</EXTREMELY_IMPORTANT>",
  ].join("\n");

  return {
    name: "goodboy",
    version: "0.1.0",
    experimental: {
      chat: {
        system: {
          transform: (system) => `${system}\n\n${context}`,
        },
      },
    },
  };
}
