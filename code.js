"use strict";
// code.ts
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
// -----------------------
// Utility Functions
// -----------------------
// Convert a Figma RGB color (0-1 values) to an rgba() string.
// The Figma RGB type only has r, g, and b. Use the optional opacity parameter.
function rgbaToString(color, opacity) {
    const r = Math.round(color.r * 255);
    const g = Math.round(color.g * 255);
    const b = Math.round(color.b * 255);
    const a = opacity !== undefined ? opacity.toFixed(2) : "1";
    return `rgba(${r}, ${g}, ${b}, ${a})`;
}
// -----------------------
// Extraction Functions
// -----------------------
// Extract typography information from a TextNode.
function extractTypography(node) {
    return __awaiter(this, void 0, void 0, function* () {
        yield figma.loadFontAsync(node.fontName);
        const font = node.fontName;
        // Use valueOf() for non-number lineHeight.
        let lineHeightStr;
        if (typeof node.lineHeight === "number") {
            lineHeightStr = `${node.lineHeight}px`;
        }
        else {
            const lh = node.lineHeight.valueOf();
            lineHeightStr = `${lh.value}${lh.unit.toLowerCase()}`;
        }
        // Use valueOf() for non-number letterSpacing.
        let letterSpacingStr;
        if (typeof node.letterSpacing === "number") {
            letterSpacingStr = `${node.letterSpacing}px`;
        }
        else {
            const ls = node.letterSpacing.valueOf();
            letterSpacingStr = `${ls.value}${ls.unit.toLowerCase()}`;
        }
        return {
            fontFamily: font.family,
            fontWeight: font.style.toLowerCase().includes("bold") ? 700 : 400,
            fontSize: `${String(node.fontSize)}px`,
            lineHeight: lineHeightStr,
            letterSpacing: letterSpacingStr,
            textAlign: node.textAlignHorizontal.toLowerCase()
        };
    });
}
// Extract layout details for nodes that support auto-layout.
function extractLayout(node) {
    if ("layoutMode" in node && node.layoutMode !== "NONE") {
        let padding;
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
// Extract style properties like fills, strokes, shadows, and opacity.
function extractStyles(node) {
    const styles = {};
    // Background / fills extraction
    if ("fills" in node && Array.isArray(node.fills) && node.fills.length > 0) {
        const fill = node.fills[0];
        if (fill.type === "SOLID") {
            styles.background = rgbaToString(fill.color, fill.opacity);
        }
    }
    // Border extraction
    if ("strokes" in node && Array.isArray(node.strokes) && node.strokes.length > 0) {
        const stroke = node.strokes[0];
        if (stroke.type === "SOLID") {
            let radius = "";
            // Use a type guard for nodes that support corner radius.
            if ("cornerRadius" in node && typeof node.cornerRadius === "number") {
                radius = `${node.cornerRadius}px`;
            }
            else if ("topLeftRadius" in node) {
                const { topLeftRadius, topRightRadius, bottomRightRadius, bottomLeftRadius } = node;
                radius = `${topLeftRadius}px ${topRightRadius}px ${bottomRightRadius}px ${bottomLeftRadius}px`;
            }
            styles.border = {
                width: typeof node.strokeWeight === "number" ? node.strokeWeight : Number(node.strokeWeight),
                color: rgbaToString(stroke.color),
                radius: radius
            };
        }
    }
    // Shadow extraction: look for DROP_SHADOW effect
    if ("effects" in node && Array.isArray(node.effects)) {
        const dropShadow = node.effects.find(e => e.type === "DROP_SHADOW" && e.visible);
        if (dropShadow &&
            "offset" in dropShadow &&
            "color" in dropShadow &&
            "radius" in dropShadow) {
            const ds = dropShadow;
            styles.shadow = {
                x: ds.offset.x,
                y: ds.offset.y,
                blur: ds.radius,
                color: rgbaToString(ds.color)
            };
        }
    }
    // Opacity extraction
    if ("opacity" in node) {
        styles.opacity = node.opacity;
    }
    return styles;
}
// Recursively extract an AltNode from any SceneNode.
function createAltNode(node) {
    return __awaiter(this, void 0, void 0, function* () {
        const altNode = {
            id: node.id,
            type: node.type,
            name: node.name,
            position: {
                x: node.x,
                y: node.y
            },
            dimensions: {
                width: node.width,
                height: node.height
            },
            layout: extractLayout(node),
            styles: extractStyles(node),
            children: []
        };
        // If the node is a TextNode, extract its text content and typography details.
        if (node.type === "TEXT") {
            altNode.text = node.characters;
            altNode.typography = yield extractTypography(node);
        }
        // Recursively process children if they exist.
        if ("children" in node && node.children) {
            for (const child of node.children) {
                altNode.children.push(yield createAltNode(child));
            }
        }
        return altNode;
    });
}
// -----------------------
// UI Message Handling
// -----------------------
figma.ui.onmessage = (msg) => __awaiter(void 0, void 0, void 0, function* () {
    if (msg.type === "export-alt-node") {
        try {
            const selection = figma.currentPage.selection;
            if (selection.length === 0) {
                figma.notify("Please select at least one node.");
                return;
            }
            // Build AltNodes from each selected node.
            const altNodes = [];
            for (const node of selection) {
                altNodes.push(yield createAltNode(node));
            }
            // Send the AltNode JSON back to the UI with a distinct message type.
            figma.ui.postMessage({ type: "display-alt-nodes", altNodes });
            // Optional user feedback.
            figma.notify("AltNode generated! Check the UI panel for JSON.");
        }
        catch (error) {
            figma.notify("Error: " + JSON.stringify(error, null, 2));
        }
    }
});
figma.showUI(__html__, { width: 400, height: 600 });
