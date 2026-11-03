class SvgGeometryProbe:
    def script(self) -> str:
        return r"""
({ expected, kind }) => {
  const failures = [];
  const svg = document.documentElement;
  svg.style.maxWidth = "none";
  svg.style.width = `${svg.viewBox.baseVal.width}px`;
  svg.style.height = `${svg.viewBox.baseVal.height}px`;
  const viewport = svg.getBoundingClientRect();
  const normalize = (value) => value.replace(/\s+/g, " ").trim();
  const labels = [...document.querySelectorAll("foreignObject, text")];
  const text = normalize(labels.map((label) => label.textContent).join(" "));
  for (const value of expected) {
    if (!text.includes(value)) failures.push(`Missing text: ${value}`);
  }
  const overflow = (rect, box) => Math.max(
    box.left - rect.left, rect.right - box.right, box.top - rect.top, rect.bottom - box.bottom, 0,
  );
  const rows = [];
  for (const label of labels) {
    const box = label.getBoundingClientRect();
    const walker = document.createTreeWalker(label, NodeFilter.SHOW_TEXT);
    const lines = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const rect of range.getClientRects()) {
        if (rect.width === 0 || rect.height === 0) continue;
        lines.push(rect);
        const clipping = Math.max(overflow(rect, box), overflow(rect, viewport));
        if (clipping > 0.5) failures.push(`Clipped by ${clipping.toFixed(3)}px: ${node.textContent}`);
      }
    }
    if (lines.length === 0) failures.push(`Label has no visible text: ${label.textContent}`);
    rows.push({ label, lines, top: Math.min(...lines.map((line) => line.top)),
      bottom: Math.max(...lines.map((line) => line.bottom)) });
  }
  const groups = kind === "class" ? [...document.querySelectorAll("g.node")] : [svg];
  for (const group of groups) {
    const groupRows = rows.filter((row) => group.contains(row.label)).sort((a, b) => a.top - b.top);
    for (let index = 1; index < groupRows.length; index++) {
      if (groupRows[index - 1].bottom - groupRows[index].top > 0.5) {
        failures.push(`Overlapping rows: ${groupRows[index - 1].label.textContent}`
          + ` / ${groupRows[index].label.textContent}`);
      }
    }
  }
  if (kind === "class") {
    if (labels.length !== 6) failures.push(`Expected six class labels, found ${labels.length}`);
    const styles = [...document.querySelectorAll("g.label")];
    if (!styles.some((label) => label.textContent.includes("count_example")
      && getComputedStyle(label).textDecorationLine.includes("underline"))) failures.push("Static style lost");
    if (!styles.some((label) => label.textContent.includes("refresh_example")
      && getComputedStyle(label).fontStyle === "italic")) failures.push("Abstract style lost");
    const paths = [...document.querySelectorAll("path.relation")];
    if (paths.length !== 1 || !paths[0].getAttribute("marker-end")?.includes("extensionEnd")
      || paths[0].hasAttribute("marker-start") || !Number.isFinite(paths[0].getTotalLength())
      || paths[0].getTotalLength() <= 0) failures.push("Inheritance connector lost");
  } else {
    if (labels.length !== 3) failures.push(`Expected three TreeView labels, found ${labels.length}`);

  }
  if (document.fonts.status !== "loaded") failures.push("Fonts have not loaded");
  return { failures, label_count: labels.length,
    wrapped_rows: rows.filter((row) => new Set(row.lines.map((line) => line.top)).size > 1).length };
}
"""
