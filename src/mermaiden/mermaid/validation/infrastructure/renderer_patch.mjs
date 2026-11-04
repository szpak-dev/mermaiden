import { createHash } from "node:crypto";
import { readFile, rename, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";

class RendererPatchInstaller {
  digest(content) {
    return createHash("sha256").update(content).digest("hex");
  }

  async run(arguments_) {
    const check = arguments_[0] === "--check";
    if ((!check && arguments_.length !== 0) || (check && arguments_.length !== 2)) {
      throw new Error("Usage: renderer_patch.mjs [--check MERMAID_PACKAGE_ROOT]");
    }
    const recipe = JSON.parse(await readFile(new URL("renderer_patch.json", import.meta.url), "utf8"));
    const require = createRequire(resolve("package.json"));
    const root = check ? resolve(arguments_[1]) : dirname(require.resolve("mermaid/package.json"));
    const metadata = JSON.parse(await readFile(join(root, "package.json"), "utf8"));
    if (metadata.name !== "mermaid" || metadata.version !== recipe.mermaid_version) {
      throw new Error(`Renderer patch requires mermaid@${recipe.mermaid_version}.`);
    }
    const pending = [];
    for (const file of recipe.files) {
      const path = join(root, file.path);
      const original = await readFile(path, "utf8");
      const digest = this.digest(original);
      if (digest === file.patched_sha256) continue;
      if (check) {
        throw new Error(`Required renderer patch ${recipe.id} is absent or changed. Run python -m mermaiden.cli renderer-setup --prefix ${dirname(dirname(root))}.`);
      }
      if (digest !== file.original_sha256) {
        throw new Error(`Refusing to patch unexpected Mermaid content: ${file.path}`);
      }
      let patched = original;
      for (const replacement of file.replacement_groups.flatMap((group) => recipe.replacements[group])) {
        if (patched.split(replacement.before).length - 1 !== replacement.count) {
          throw new Error(`Renderer patch does not match ${file.path}.`);
        }
        patched = patched.replaceAll(replacement.before, replacement.after);
      }
      if (this.digest(patched) !== file.patched_sha256) {
        throw new Error(`Renderer patch checksum does not match ${file.path}.`);
      }
      pending.push({ path, patched });
    }
    for (const { path, patched } of pending) {
      const temporary = `${path}.mermaiden-${process.pid}`;
      await writeFile(temporary, patched, { flag: "wx" });
      await rename(temporary, path);
    }
    console.log(`Mermaid ${recipe.mermaid_version}: ${recipe.id} verified.`);
  }
}

await new RendererPatchInstaller().run(process.argv.slice(2)).catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
