# backend/ppt_utils.py
import os
import uuid
import random
import logging
from typing import List, Dict, Any, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt, Inches
from pptx.enum.text import MSO_AUTO_SIZE, MSO_ANCHOR # Import necessary enums

from .config import ( # Import from local config
    PROFESSIONAL_COLORS_HEX,
    PROFESSIONAL_FONT_NAMES,
    SUBTLE_BACKGROUND_COLORS_HEX,
    PPT_OUTPUT_DIR
)

logger = logging.getLogger(__name__)

def _apply_run_style(run, is_title_style=False, is_description_style=False):
    """Internal helper to style a pptx run object with professional, consistent styles."""
    if is_title_style:
        # Consistent professional title styling
        run.font.color.rgb = RGBColor.from_string(PROFESSIONAL_COLORS_HEX["dark_blue"]) # Consistent dark blue title color
        run.font.name = PROFESSIONAL_FONT_NAMES[0] # Use the first professional font (e.g., Calibri)
        run.font.size = Pt(36) # Consistent title size
        run.font.bold = True # Titles should always be bold for professionalism
    elif is_description_style:
        # Consistent professional description text styling
        run.font.name = PROFESSIONAL_FONT_NAMES[0]
        run.font.size = Pt(16) # Smaller size for descriptions
        run.font.color.rgb = RGBColor.from_string("555555") # Slightly lighter grey for descriptions
        run.font.bold = False
    else:  # Body style (for main bullet points)
        # Consistent professional body text styling
        run.font.name = PROFESSIONAL_FONT_NAMES[0] # Use the same professional font as titles
        run.font.size = Pt(20) # Consistent body text size for main points
        run.font.color.rgb = RGBColor.from_string(PROFESSIONAL_COLORS_HEX["dark_grey"]) # Consistent dark grey for body text
        run.font.bold = False # Body text usually not bold

def _style_text_shape(shape_object, is_title_style=False, is_description_style=False):
    """Internal helper to style a pptx text shape object."""
    text_frame = shape_object.text_frame
    text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT # Allows text to fit the shape
    text_frame.vertical_anchor = MSO_ANCHOR.TOP # Align text to the top of the shape

    # Apply consistent styling to all paragraphs within the text frame
    for p in text_frame.paragraphs:
        if p.runs:
            # Apply run style based on whether it's a title, description, or regular body text
            _apply_run_style(p.runs[0], is_title_style=is_title_style, is_description_style=is_description_style)

# MODIFIED FUNCTION SIGNATURE AND USAGE
def create_presentation_from_data(slide_data: List[Dict[str, Any]], full_output_path: str) -> str:
    """
    Creates a PowerPoint presentation from structured slide data and saves it to the specified path.
    Applies professional and consistent styling.
    :param slide_data: A list of dictionaries, each representing a slide.
    :param full_output_path: The complete file path (including directory and filename.pptx) to save the presentation.
    :return: The full path to the generated PPTX file.
    """
    prs = Presentation()
    # No need to os.makedirs here, it's done in main.py
    # No need to construct full_path here, it's passed directly as full_output_path

    # Define a default layout for content slides (e.g., Title and Content)
    title_and_content_layout = None
    for i, layout in enumerate(prs.slide_layouts):
        if "TITLE AND CONTENT" in layout.name.upper() or "TITLE AND BULLETS" in layout.name.upper():
            title_and_content_layout = layout
            break
    if title_and_content_layout is None:
        logger.warning("Specific 'Title and Content' layout not found, defaulting to layout index 1.")
        title_and_content_layout = prs.slide_layouts[1]

    # Use a title slide for the first slide (if available, typically layout 0)
    title_slide_layout = prs.slide_layouts[0]
    
    if not slide_data:
        logger.warning("No slide data provided. Creating a default empty presentation.")
        slide = prs.slides.add_slide(title_slide_layout)
        if slide.shapes.title:
            slide.shapes.title.text = "Empty Presentation"
            _style_text_shape(slide.shapes.title, is_title_style=True)
        prs.save(full_output_path) # Use the passed path
        return full_output_path

    # Process the first slide as the Title Slide
    first_slide_data = slide_data[0]
    slide = prs.slides.add_slide(title_slide_layout)
    _apply_random_slide_background(slide) # Apply a subtle background

    title_shape = slide.shapes.title
    if title_shape:
        title_shape.text = first_slide_data.get("title", "AI Generated Presentation")
        _style_text_shape(title_shape, is_title_style=True)
    else:
        logger.warning("No title placeholder found for the first slide. Adding manually.")
        left, top, width, height = Inches(0.5), Inches(1), Inches(9), Inches(1.5)
        title_shape = slide.shapes.add_textbox(left, top, width, height)
        title_shape.text_frame.text = first_slide_data.get("title", "AI Generated Presentation")
        _style_text_shape(title_shape, is_title_style=True)

    # For the subtitle on the title slide
    subtitle_shape = None
    for ph in slide.placeholders:
        if ph.is_placeholder and ph.placeholder_format.idx == 1: # Subtitle placeholder index
            subtitle_shape = ph
            break
    
    if subtitle_shape:
        subtitle_text = first_slide_data.get("description", "A Comprehensive Overview")
        if isinstance(first_slide_data.get("points"), list) and first_slide_data.get("points"):
            subtitle_text = first_slide_data.get("points")[0] # Use first point as subtitle if available
        subtitle_shape.text = subtitle_text
        _style_text_shape(subtitle_shape, is_title_style=False) # Use body style for subtitle
    else:
        logger.warning("No subtitle placeholder found for the first slide. Adding manually.")
        left, top, width, height = Inches(0.5), Inches(3), Inches(9), Inches(1)
        subtitle_shape = slide.shapes.add_textbox(left, top, width, height)
        subtitle_shape.text_frame.text = first_slide_data.get("description", "A Comprehensive Overview")
        _style_text_shape(subtitle_shape, is_title_style=False)


    logger.info("Title slide created.")

    # Add content slides
    for i, slide_info in enumerate(slide_data[1:]): # Start from the second slide for content
        slide_title_text = slide_info.get("title", f"Slide {i+2}")
        points = slide_info.get("points", [])
        description = slide_info.get("description", "")

        logger.info(f"Adding content slide: {slide_title_text}")

        slide = prs.slides.add_slide(title_and_content_layout)
        _apply_random_slide_background(slide) # Apply a subtle background

        # --- Set Slide Title ---
        title_shape = slide.shapes.title
        if title_shape:
            title_shape.text = slide_title_text
            _style_text_shape(title_shape, is_title_style=True)
        else:
            logger.warning(f"No title placeholder found for slide {i+2}. Adding manually.")
            left, top, width, height = Inches(0.5), Inches(0.2), Inches(9), Inches(1)
            title_shape = slide.shapes.add_textbox(left, top, width, height)
            title_shape.text_frame.text = slide_title_text
            _style_text_shape(title_shape, is_title_style=True)


        # --- Set Slide Body (Bullet Points) ---
        body_shape = None
        for shape in slide.placeholders:
            if shape.is_placeholder and (
                "body" in shape.name.lower() or
                "content" in shape.name.lower() or
                "text" in shape.name.lower() # Generic text placeholder
            ):
                body_shape = shape
                break
        if body_shape is None:
            # Fallback: add a new textbox if no suitable placeholder found
            logger.warning(f"No suitable body placeholder found for slide {i+2}. Adding body textbox manually.")
            left, top, width, height = Inches(0.5), Inches(1.5), Inches(9), Inches(4) # Adjusted height
            body_shape = slide.shapes.add_textbox(left, top, width, height)

        if body_shape:
            tf = body_shape.text_frame
            tf.clear() # Clear existing text
            tf.word_wrap = True

            # Add bullet points
            for point_text in points:
                if isinstance(point_text, str):
                    p = tf.add_paragraph()
                    p.text = point_text
                    p.level = 0 # Main bullet point level
                    _apply_run_style(p.runs[0], is_title_style=False, is_description_style=False)
                else:
                    logger.warning(f"Invalid point type: {point_text} in '{slide_title_text}'")
        else:
            logger.warning(f"No body placeholder for slide: {slide_title_text}. Bullet points might not be fully added.")


        # --- Add Description (separate text box for clear separation) ---
        if description.strip():
            # Position description below bullet points, ensuring clear separation
            # Calculate top position based on approximate height of bullet points
            # This is a heuristic and might need fine-tuning based on actual content length
            desc_left = Inches(0.5)
            desc_top = Inches(5.5) # Start lower to ensure space for points
            desc_width = Inches(9)
            desc_height = Inches(1.5) # Ample height for description

            description_shape = slide.shapes.add_textbox(desc_left, desc_top, desc_width, desc_height)
            tf_desc = description_shape.text_frame
            tf_desc.clear()
            tf_desc.word_wrap = True
            
            p_desc = tf_desc.add_paragraph()
            p_desc.text = description
            p_desc.level = 0 # Description as a main paragraph
            _apply_run_style(p_desc.runs[0], is_title_style=False, is_description_style=True)
            logger.debug(f"Added description to slide {i+2}.")
        
        logger.debug(f"Content slide {i+2} finished.")

    try:
        logger.info(f"Saving PPT file to {full_output_path}...") # Use the passed path
        prs.save(full_output_path)
        logger.info("PPT file saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save PPT file {full_output_path}: {e}", exc_info=True)
        raise # Re-raise the exception for FastAPI to catch and return 500

    return full_output_path

def _apply_random_slide_background(slide):
    """Internal helper to apply a random subtle background to a slide."""
    if SUBTLE_BACKGROUND_COLORS_HEX:
        try:
            fill = slide.background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor.from_string(random.choice(SUBTLE_BACKGROUND_COLORS_HEX))
        except Exception as e:
            logger.warning(f"Could not set slide background: {e}")