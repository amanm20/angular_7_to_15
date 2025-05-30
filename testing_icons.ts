// code.ts

// -----------------------
// Interfaces & Type Definitions
// -----------------------

interface Position {
  x: number;
  y: number;
}

interface Dimensions {
  width: number;
  height: number;
}

interface Layout {
  display: "block" | "flex";
  padding?: string;
  gap?: string;
}

interface Typography {
  fontFamily: string;
  fontWeight: number;
  fontSize: string;
  lineHeight: string;
  letterSpacing: string;
  textAlign?: "left" | "center" | "right";
}

interface Border {
  width: number;
  color: string;
  radius: string;
}

interface Shadow {
  x: number;
  y: number;
  blur: number;
  color: string;
}

interface Styles {
  background?: string;
  border?: Border;
  shadow?: Shadow;
  opacity?: number;
}

interface AltNode {
  id: string;
  type: string;
  name: string;
  position: Position;
  dimensions: Dimensions;
  layout?: Layout;
  typography?: Typography;
  styles?: Styles;
  text?: string;
  svgData?: string;
  children: AltNode[];
}

// -----------------------
// UTF-8 Decoding Helper
// -----------------------
function decodeUTF8(uint8Array: Uint8Array): string {
  let rawString = "";
  for (let i = 0; i < uint8Array.length; i++) {
    rawString += String.fromCharCode(uint8Array[i]);
  }
  try {
    return decodeURIComponent(escape(rawString));
  } catch (err) {
    console.error("UTF-8 decoding error:", err);
    return rawString;
  }
}

// -----------------------
// Utility Functions
// -----------------------
function rgbaToString(color: RGB, opacity?: number): string {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  const a = opacity !== undefined ? opacity.toFixed(2) : "1";
  return `rgba(${r}, ${g}, ${b}, ${a})`;
}

// -----------------------
// Extraction Functions
// -----------------------

async function extractTypography(node: TextNode): Promise<Typography> {
  await figma.loadFontAsync(node.fontName as FontName);
  const font = node.fontName as FontName;

  let lineHeightStr: string;
  if (typeof node.lineHeight === "number") {
    lineHeightStr = `${node.lineHeight}px`;
  } else {
    const lh = node.lineHeight.valueOf() as { value: number; unit: string };
    lineHeightStr = `${lh.value}${lh.unit.toLowerCase()}`;
  }

  let letterSpacingStr: string;
  if (typeof node.letterSpacing === "number") {
    letterSpacingStr = `${node.letterSpacing}px`;
  } else {
    const ls = node.letterSpacing.valueOf() as { value: number; unit: string };
    letterSpacingStr = `${ls.value}${ls.unit.toLowerCase()}`;
  }
  
  return {
    fontFamily: font.family,
    fontWeight: font.style.toLowerCase().includes("bold") ? 700 : 400,
    fontSize: `${String(node.fontSize)}px`,
    lineHeight: lineHeightStr,
    letterSpacing: letterSpacingStr,
    textAlign: node.textAlignHorizontal.toLowerCase() as "left" | "center" | "right"
  };
}

function extractLayout(node: SceneNode): Layout | undefined {
  if ("layoutMode" in node && node.layoutMode !== "NONE") {
    let padding: string | undefined;
    if ("paddingTop" in node && "paddingRight" in node && "paddingBottom" in node && "paddingLeft" in node) {
      padding = `${node.paddingTop}px ${node.paddingRight}px ${node.paddingBottom}px ${node.paddingLeft}px`;
    }
    return {
      display: "flex",
      padding,
      gap: node.itemSpacing ? `${node.itemSpacing}px` : undefined
    };
  }
  return { display: "block" };
}

function extractStyles(node: SceneNode): Styles | undefined {
  const styles: Styles = {};
  
  if ("fills" in node && Array.isArray(node.fills) && node.fills.length > 0) {
    const fill = node.fills[0] as Paint;
    if (fill.type === "SOLID") {
      styles.background = rgbaToString(fill.color, fill.opacity);
    }
  }
  
  if ("strokes" in node && Array.isArray(node.strokes) && node.strokes.length > 0) {
    const stroke = node.strokes[0] as Paint;
    if (stroke.type === "SOLID") {
      let radius = "";
      if ("cornerRadius" in node && typeof (node as any).cornerRadius === "number") {
        radius = `${(node as any).cornerRadius}px`;
      } else if ("topLeftRadius" in node) {
        const { topLeftRadius, topRightRadius, bottomRightRadius, bottomLeftRadius } = node as any;
        radius = `${topLeftRadius}px ${topRightRadius}px ${bottomRightRadius}px ${bottomLeftRadius}px`;
      }
      styles.border = {
        width: typeof node.strokeWeight === "number" ? node.strokeWeight : Number(node.strokeWeight),
        color: rgbaToString(stroke.color),
        radius: radius
      };
    }
  }
  
  if ("effects" in node && Array.isArray(node.effects)) {
    const dropShadow = node.effects.find(e => e.type === "DROP_SHADOW" && e.visible);
    if (dropShadow && "offset" in dropShadow && "color" in dropShadow && "radius" in dropShadow) {
      const ds = dropShadow as {
        offset: { x: number; y: number };
        color: RGB;
        radius: number;
      };
      styles.shadow = {
        x: ds.offset.x,
        y: ds.offset.y,
        blur: ds.radius,
        color: rgbaToString(ds.color)
      };
    }
  }
  
  if ("opacity" in node) {
    styles.opacity = node.opacity;
  }
  
  return styles;
}

async function createAltNode(node: SceneNode): Promise<AltNode> {
  const altNode: AltNode = {
    id: node.id,
    type: node.type,
    name: node.name,
    position: { x: node.x, y: node.y },
    dimensions: { width: node.width, height: node.height },
    layout: extractLayout(node),
    styles: extractStyles(node),
    children: []
  };

  if (node.type === "TEXT") {
    altNode.text = (node as TextNode).characters;
    altNode.typography = await extractTypography(node as TextNode);
  }
  
  // For VECTOR nodes, try exporting as SVG.
  if (node.type === "VECTOR") {
    try {
      const svgBytes = await node.exportAsync({ format: "SVG" });
      const svgString = decodeUTF8(svgBytes);
      if (svgString.trim().length > 0) {
        altNode.svgData = svgString;
        console.log("SVG exported for node", node.id, svgString);
      } else {
        console.warn("SVG export returned empty for node", node.id);
      }
    } catch (error) {
      console.error("Error exporting SVG for node", node.id, error);
    }
  }

  if ("children" in node && node.children) {
    for (const child of node.children) {
      altNode.children.push(await createAltNode(child));
    }
  }
  
  return altNode;
}

// -----------------------
// UI Message Handling
// -----------------------
figma.ui.onmessage = async (msg) => {
  if (msg.type === "export-alt-node") {
    try {
      const selection = figma.currentPage.selection;
      if (selection.length === 0) {
        figma.notify("Please select at least one node.");
        return;
      }
      
      const altNodes: AltNode[] = [];
      for (const node of selection) {
        altNodes.push(await createAltNode(node));
      }
      
      figma.ui.postMessage({ type: "display-alt-nodes", altNodes });
      figma.notify("AltNode generated! Check the UI panel for JSON.");
    } catch (error) {
      figma.notify("Error: " + JSON.stringify(error, null, 2));
    }
  }
};

figma.showUI(__html__, { width: 400, height: 600 });
