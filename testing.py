from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

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

# Get the format instructions
output_parser_1 = PydanticOutputParser(pydantic_object=UpdatedComponent)
output_parser_2 = PydanticOutputParser(pydantic_object=UpdatedPage)

format_instructions_1 = output_parser_1.get_format_instructions()
format_instructions_2 = output_parser_2.get_format_instructions()

def update_angular_component(html_path, css_path, image_path, lexicon_components, page_name, page_image_path, page_angular_code, page_angular_components, page_angular_components_code, usr_inst):
    
    new_html = read_file(html_path)
    new_css = read_file(css_path)
    new_image = encode_image(image_path)
    page_image = encode_image(page_image_path)

    prompt_step1 = f"""
        As an experienced Angular 18+ developer, your task is to update an **existing Angular component** in a page based on Figma design changes.

        Analyze the **new page design** and compare it with the **existing page** to determine which **component** needs to be updated 
        and create the updated component with the same name.

        <<INPUTS>>

        - new page HTML: {new_html}
        - new page CSS: {new_css}
        - new page Image: {new_image}
        - Lexicon Components: {lexicon_components}

        # EXISTING PAGE
        - Page Name: {page_name}
        - Page Angular Code: {page_angular_code}
        - Page Image: {page_image}
        - List of Components used in the Page: {page_angular_components}
        - Angular code for each component: {page_angular_components_code}

        <<INPUTS>>

        <<INSTRUCTIONS>>

        # ANALYZE AND PLAN
        - Thoroughly analyze the new page’s HTML, CSS, and image.
        - Compare the new design with the existing page’s Angular code and its components.
        - Identify the **single component** that has changed.
        - Focus on maintaining accessibility, responsiveness, and consistency with the Figma design.
        - **Review the available Lexicon components** and plan to integrate them where applicable.

        # COMPONENT GENERATION
        - Update the `.ts`, `.html`, `.css`, and `.spec.ts` files for the identified component to match the new structure.
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
        {usr_inst}

        <<INSTRUCTIONS>>


        <<OUTPUT>>

        Provide the updated component in the following JSON format:
        {format_instructions_1}
        ONLY return the JSON object. Do not include any additional text.
        
        <<OUTPUT>>
"""
## need to get output from model and parse it to json format so send to next invocation of model as input

def update_angular_page(updated_component_name, updated_component_code, page_image_path, page_name, page_code, page_angular_components, page_angular_components_code, usr_inst):
    
    page_image = encode_image(page_image_path)
    
    prompt_step2 = f"""
        You are an expert Angular developer. Follow the instructions below to **update an existing Angular page** by integrating the updated component provided. The target framework is Angular 18+.

        <<INPUTS>>

        - Updated Component:
        - Name: {updated_component_name}
        - Angular Code: {updated_component_code}

        # EXISTING PAGE
        - Page Name: {page_name}
        - Page Angular Code: {page_code}
        - Page Image: {page_image}
        - List of Components used in the Page: {page_angular_components}
        - Angular code for each component: {page_angular_components_code}

        <<INPUTS>>

        <<INSTRUCTIONS>>

        ## ANALYZE AND PLAN
        - Carefully review the existing Angular page and its components.
        - Analyze the **updated component** provided.
        - Determine the necessary changes to integrate the updated component into the existing page.
        - Maintain the page's overall design, accessibility, and responsiveness.
        - Ensure the page continues to follow Angular best practices after the update.

        ## PAGE UPDATING
         Update the `.ts`, `.html`, `.css`, and `.spec.ts` files for the page.
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
        {usr_inst}

        <<INSTRUCTIONS>>

        <<OUTPUT>>

        Answer only in the below format. Do not add any trailing or leading text in your answer. **PROVIDE JSON ONLY**.
        {format_instructions_2}

        <<OUTPUT>>
        """