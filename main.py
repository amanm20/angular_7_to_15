import json
import re
from typing import List, Dict

def safe_css_identifier(value: str) -> str:
    """
    Convert a Figma node ID or name into a safe CSS selector (e.g. #_7_737).
    """
    # Replace invalid characters with underscores
    return "_" + re.sub(r'[^a-zA-Z0-9_\-]', '_', value)

def px(value) -> str:
    """Convert a numeric or string to a 'px' string (if numeric)."""
    if isinstance(value, (int, float)):
        return f"{value}px"
    return str(value)

def generate_node_html_css(node: Dict, css_rules: Dict[str, Dict[str, str]]) -> str:
    """
    Recursively generate HTML for a single AltNode, collecting CSS rules in `css_rules`.
    Returns the HTML snippet for the node (including children).
    """
    node_id = safe_css_identifier(node["id"])
    node_type = node["type"]
    
    # Decide what HTML tag to use
    if node_type == "TEXT":
        tag = "span"
    elif node_type == "VECTOR":
        tag = "div"  # Could be <svg>, but that requires vector path data
    else:
        tag = "div"
    
    # Build CSS for this node
    styles = {}

    # Position & size (absolute positioning to match Figma’s x, y)
    x = node["position"]["x"]
    y = node["position"]["y"]
    w = node["dimensions"]["width"]
    h = node["dimensions"]["height"]
    
    # Use absolute positioning to replicate Figma’s coordinates
    styles["position"] = "absolute"
    styles["left"] = px(x)
    styles["top"] = px(y)
    styles["width"] = px(w)
    styles["height"] = px(h)
    
    # Layout (display: flex or block), plus padding, gap
    if "layout" in node and node["layout"]:
        layout = node["layout"]
        if layout.get("display") == "flex":
            styles["display"] = "flex"
            if layout.get("gap"):
                styles["gap"] = layout["gap"]
            if layout.get("padding"):
                styles["padding"] = layout["padding"]
        else:
            styles["display"] = "block"
    
    # Styles (background, border, shadow, opacity)
    if "styles" in node and node["styles"]:
        node_styles = node["styles"]
        
        # If it's a TEXT node, interpret fill as text color
        bg_color = node_styles.get("background")
        if bg_color:
            if node_type == "TEXT":
                styles["color"] = bg_color
            else:
                styles["background-color"] = bg_color
        
        # Border
        if "border" in node_styles and node_styles["border"]:
            border = node_styles["border"]
            styles["border"] = f"{border['width']}px solid {border['color']}"
            if border["radius"]:
                styles["border-radius"] = border["radius"]
        
        # Shadow
        if "shadow" in node_styles and node_styles["shadow"]:
            shadow = node_styles["shadow"]
            styles["box-shadow"] = (
                f"{px(shadow['x'])} {px(shadow['y'])} {px(shadow['blur'])} {shadow['color']}"
            )
        
        # Opacity
        if "opacity" in node_styles:
            styles["opacity"] = str(node_styles["opacity"])
    
    # Typography (for TEXT nodes)
    if node_type == "TEXT" and "typography" in node and node["typography"]:
        typo = node["typography"]
        styles["font-family"] = typo["fontFamily"]
        styles["font-weight"] = str(typo["fontWeight"])
        styles["font-size"] = typo["fontSize"]
        
        # Convert lineHeight like "122.00000286102295percent" => "122%"
        line_height = typo["lineHeight"]
        if line_height.endswith("percent"):
            numeric_part = re.sub(r'[^0-9.]+', '', line_height)
            styles["line-height"] = f"{numeric_part}%"
        else:
            styles["line-height"] = line_height
        
        # letterSpacing like "0percent" => "0%"
        letter_spacing = typo["letterSpacing"]
        if letter_spacing.endswith("percent"):
            numeric_part = re.sub(r'[^0-9.]+', '', letter_spacing)
            styles["letter-spacing"] = f"{numeric_part}%"
        else:
            styles["letter-spacing"] = letter_spacing
        
        # textAlign
        if "textAlign" in typo:
            styles["text-align"] = typo["textAlign"]
    
    # Accumulate these styles into the css_rules dictionary
    css_rules[node_id] = styles
    
    # Generate HTML for children
    children_html = ""
    if "children" in node and node["children"]:
        for child in node["children"]:
            children_html += generate_node_html_css(child, css_rules)
    
    # If this is a TEXT node, include the text in the HTML
    if node_type == "TEXT" and "text" in node:
        inner_text = node["text"]
        # Escape special chars
        inner_text = (inner_text
                      .replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;"))
        return f'<{tag} id="{node_id}">{inner_text}{children_html}</{tag}>'
    else:
        return f'<{tag} id="{node_id}">{children_html}</{tag}>'

def build_html_document(alt_nodes: List[Dict]) -> str:
    """
    Given a list of top-level AltNodes, generate a complete HTML document
    with embedded CSS in a <style> block.
    """
    css_rules = {}
    
    # Generate HTML for each top-level node
    body_content = ""
    for node in alt_nodes:
        body_content += generate_node_html_css(node, css_rules)
    
    # Build the CSS text from the css_rules dictionary
    css_text = ""
    for node_id, style_dict in css_rules.items():
        style_str = "".join(f"{prop}: {val};" for prop, val in style_dict.items())
        css_text += f"#{node_id} {{{style_str}}}\n"
    
    # Final HTML with embedded <style>
    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>AltNode Output</title>
  <style>
    /* Basic reset / defaults */
    html, body {{
      margin: 0;
      padding: 0;
      position: relative;
      width: 100%;
      height: 100%;
    }}
    body {{
      /* You can change this color to match your Figma canvas if desired */
      background-color: #fff;
    }}
    {css_text}
  </style>
</head>
<body>
{body_content}
</body>
</html>"""
    return html_document

# -------------------------------------------------------------
# The script flow: prompt user for JSON file path, generate HTML
# -------------------------------------------------------------

input_path = input("Enter the path to your AltNode JSON file: ").strip()
with open(input_path, "r", encoding="utf-8") as f:
    alt_nodes = json.load(f)

html_output = build_html_document(alt_nodes)

with open("output.html", "w", encoding="utf-8") as out:
    out.write(html_output)

print("HTML + CSS generated in 'output.html'")
