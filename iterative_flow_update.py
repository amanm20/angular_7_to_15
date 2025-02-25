from typing import List
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

# Updated Pydantic models
class ComponentUpdateList(BaseModel):
    """List of components needing updates"""
    components: List[str] = Field(..., description="Names of components requiring updates in order")

class UpdatedComponent(BaseModel):
    """Represents the updated component."""
    name: str = Field(..., description="The name of the updated component.")
    html: str = Field(..., description="The updated HTML code.")
    css: str = Field(..., description="The updated CSS code.")
    spec_ts: str = Field(..., description="The updated spec.ts file.")
    ts: str = Field(..., description="The updated TypeScript (.ts) code.")

class UpdatedPage(BaseModel):
    """Represents the updated page."""
    name: str = Field(..., description="The name of the updated page.")
    html: str = Field(..., description="The updated HTML code for the page.")
    css: str = Field(..., description="The updated CSS code for the page.")
    spec_ts: str = Field(..., description="The updated spec.ts file for the page.")
    ts: str = Field(..., description="The updated TypeScript (.ts) code for the page.")

# Create parsers
list_parser = PydanticOutputParser(pydantic_object=ComponentUpdateList).get_format_instructions()
component_parser = PydanticOutputParser(pydantic_object=UpdatedComponent).get_format_instructions()
page_parser = PydanticOutputParser(pydantic_object=UpdatedPage).get_format_instructions()

##Method for analyzing and updating page for changes
def analyze_and_update(html_path, css_path, image_path, lexicon_components, page_name, page_angular_code, components_json, user_inst):
    
    html = read_file(html_path)
    css = read_file(css_path)
    base64_image = encode_image(image_path)

    # Step 1: Identify components needing updates
    analysis_prompt = f"""
        As an experienced Angular 18+ developer, your task is to analyze design changes in a page and identify which
        components need updating based on figma design changes.

        Analyze the **new page design** and compare it with the **existing page** to determine which **component(s)**
        need(s) to be updated.

        Return an ordered list of names of components needing updates, starting with foundational components first.

        <<INPUTS>>

        - new page HTML: {html}
        - new page CSS: {css}
        - new page Image: {base64_image}
        - Lexicon Components: {lexicon_components}

        # EXISTING PAGE
        - Page Name: {page_name}
        - Page Angular Code: {page_angular_code}
        - Angular code for each component: {components_json}

        <<INPUTS>>

        <<INSTRUCTIONS>>

        # ANALYZE AND PLAN
        - Thoroughly analyze the new page's HTML, CSS and image.
        - Compare the new desing with the existing page's Angular code and its components.
        - Identify which Angular components are impacted by the design changes and need to be updated.
        - Review the available lexicon components to analyze changes as well.

        # Additional User Instructions that should be given the highest priority:
        {user_inst}

        <INSTRUCTIONS>>

        <<OUTPUT>>

        Provide the names of the component(s) that need(s) to be updated in the following JSON format:
        {list_parser}
        ONLY return the JSON object. Do not include any additional text.

        <<OUTPUT>>
    """
    
    # Call model and parse - to be replaced with existing code 
    component_list_obj = list_parser.parse(model.invoke(analysis_prompt))
    components_to_update = component_list_obj.components
    
    # Step 2: Update components with chained context
    updated_components = []
    for component_name in enumerate(components_to_update):
        # Get current component state (including any previous updates)
        current_component = components_json.get(component_name, {})
        
        component_prompt = f"""
        As an experienced Angular 18+ developer, your task is to update an **existing Angular component** in a page based on Figma design changes.

        Analyze the **new page design** and compare it with the **existing page** and generate the updated component with the same name.

        <<INPUTS>>

        - new page HTML: {html}
        - new page CSS: {css}
        - new page Image: {base64_image}
        - Lexicon Components: {lexicon_components}

        # EXISTING PAGE
        - Page Name: {page_name}
        - Page Angular Code: {page_angular_code}
        - Angular Component to be updated: {component_name}
        - Angular Code for component to be updated: {current_component}
        - Angular Code for all components: {components_json}

        <<INPUTS>>

        <<INSTRUCTIONS>>

        # ANALYZE AND PLAN
        - Thoroughly analyze the new page’s HTML, CSS, and image.
        - Compare the new design with the existing page’s Angular code and its components code.
        - Update the **component**: {component_name} to incorporate the design changes.
        - Focus on maintaining accessibility, responsiveness, and consistency with the Figma design.
        - **Review the available Lexicon components** and plan to integrate them where applicable.

        # COMPONENT GENERATION
        - Update the `.ts`, `.html`, `.css`, and `.spec.ts` files for the component to match the new structure.
        - **If any file does not require changes**, provide the existing content as-is.

        1. **TypeScript File (.ts)**  
        - Define the component class, decorators, and metadata.  
        - Implement core logic, methods, and properties.  
        - Maintain Angular best practices, including dependency injection and proper event handling.

        2. **HTML File (.html)**  
        - Recreate the structure and layout from the Figma design.  
        - Use Angular directives (`*ngIf`, `*ngFor`) and property binding (`[property]`, `{{variable}}`).  
        - Ensure accessibility with proper ARIA roles and semantic tags.  
        - Optimize for responsiveness using flex/grid layouts as needed.
        - Integrate **Lexicon components** where applicable.

        3. **CSS File (.css)**  
        - Implement styles matching the Figma design.  
        - Use BEM naming conventions for classes.  
        - Ensure responsive styling (media queries, flexbox, grid).  
        - Maintain consistency with global styles and themes.

        4. **Unit Test File (.spec.ts)**  
        - Write or update unit tests to ensure coverage of:
        - Component logic and methods.
        - Input and output properties.
        - Event handling and interactions.
        - Use Jasmine/Karma for testing.
        - Ensure **minimum 80% coverage**.

        # ACCESSIBILITY & BEST PRACTICES
        - Ensure all interactive elements are keyboard accessible.  
        - Use semantic HTML and ARIA attributes for screen readers.  
        - Validate color contrast ratios for WCAG compliance.  
        - Optimize performance by minimizing unnecessary re-renders.

        # Additional User Instructions that should be given the highest priority:
        {user_inst}

        <<INSTRUCTIONS>>
        
        <<OUTPUT>>

        Provide the updated component in the following JSON format:
        {component_parser}
        ONLY return the JSON object. Do not include any additional text.
        
        <<OUTPUT>>
        """

        # Get and parse updated component - to be replaced with existing code 
        updated_comp_obj = component_parser.parse(model.invoke(component_prompt))
        updated_components.append(updated_comp_obj)
    
    # Create a summary: list of names and associated updated code
    updated_component_names = [comp.name for comp in updated_components]
    updated_component_codes = {
        comp.name: {
            "html": comp.html,
            "css": comp.css,
            "ts": comp.ts,
            "spec_ts": comp.spec_ts
        }
        for comp in updated_components
    }

    # Step 3: Update page with all new components
    page_prompt = f"""
        You are an expert Angular developer. Follow the instructions below to **update an existing Angular page** by integrating the updated component(s) provided. The target framework is Angular 18+.
    
        <<INPUTS>>

        # UPDATED ANGULAR COMPONENT(s):
        - Name: {updated_component_names}
        - Angular Code: {updated_component_codes}

        # EXISTING PAGE
        - Page Name: {page_name}
        - Page Angular Code: {page_angular_code}
        - Page Angular Components: {components_json}

        <<INPUTS>>

        <<INSTRUCTIONS>>

        ## ANALYZE AND PLAN
        - Carefully review the existing Angular page and its components.
        - Analyze the **updated component(s)** provided.
        - Determine the necessary changes to integrate the updated component(s) into the existing page.
        - Maintain the page's overall design, accessibility, and responsiveness.
        - Ensure the page continues to follow Angular best practices after the update.

        ## PAGE UPDATING
        - Update the `.ts`, `.html`, `.css`, and `.spec.ts` files for the page.
        - **If any file does not require changes**, provide the existing content as-is.

        ### 1. TYPESCRIPT (.ts) FILE
        - Update the page's class and metadata to reference the updated component.
        - Ensure all imports are correct and that the updated component is integrated seamlessly.
        - Maintain existing logic and functionality while incorporating the changes.
        - Follow Angular best practices (e.g., dependency injection, routing if applicable).

        ### 2. HTML TEMPLATE (.html)
        - Update the page layout to incorporate the updated component.
        - Use Angular directives (`*ngIf`, `*ngFor`) and property bindings (`[property]`, `{{variable}}`) as needed.
        - Ensure the page's structure remains semantically correct and accessible.
        - Verify that the updated component renders correctly within the page.

        ### 3. CSS (.css)
        - Apply or update styles to maintain consistency with the existing design.
        - Ensure the updated component integrates smoothly with the page's existing layout.
        - Maintain responsive design principles using flexbox/grid and media queries.

        ### 4. UNIT TEST (.spec.ts)
        - Write or update unit tests to ensure:
        - The page renders correctly with the updated component.
        - Existing page logic remains functional.
        - The updated component interacts correctly within the page.
        - Use Jasmine/Karma for testing.
        - Ensure **minimum 80% coverage**.

        ## ACCESSIBILITY AND BEST PRACTICES
        - Ensure all interactive elements remain keyboard accessible.
        - Use semantic HTML and ARIA attributes for screen readers.
        - Validate color contrast for WCAG compliance.
        - Optimize page performance and minimize unnecessary re-renders.

        # Additional User Instructions that should be given highest priority
        {user_inst}

        <<INSTRUCTIONS>>

        <<OUTPUT>>

        Answer only in the below format. Do not add any trailing or leading text in your answer. **PROVIDE JSON ONLY**.
        {page_parser}

        <<OUTPUT>>
        """

    #to be replaced with existing code
    final_page = page_parser.parse(model.invoke(page_prompt))
    
    
    # return {
    #     "updated_components": [c.dict() for c in updated_components],
    #     "updated_page": final_page.dict()
    # }