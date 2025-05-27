# backend/ppt_utils.py
import os
import uuid
import random
import logging
from typing import List, Dict, Any, Optional

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt, Inches

from .config import ( # Import from local config
    THEME_STYLES, # Updated
    PPT_OUTPUT_DIR
)

logger = logging.getLogger(__name__)
DEFAULT_THEME_NAME = "default"


def _apply_run_style(run, font_name: str, font_size_pt: int, font_color_hex: str, is_bold: bool):
    """Internal helper to style a pptx run object based on theme."""
    run.font.name = font_name
    run.font.size = font_size_pt
    run.font.color.rgb = RGBColor.from_string(font_color_hex)
    run.font.bold = is_bold

def _style_text_shape(shape_object, current_style: Dict[str, Any], is_title_style: bool):
    """Internal helper to style text within a shape object based on theme."""
    if not hasattr(shape_object, 'has_text_frame') or not shape_object.has_text_frame:
        return
    
    text_frame = shape_object.text_frame
    font_name = current_style["font"]
    
    if is_title_style:
        font_color_hex = current_style["colors"]["primary"]
        font_size_pt = Pt(random.randint(30, 38)) # Keep random size for now
        is_bold = True # Titles are typically bold
    else:  # Body style
        font_color_hex = current_style["colors"]["text"]
        font_size_pt = Pt(random.randint(16, 20)) # Keep random size for now
        is_bold = False

    for paragraph in text_frame.paragraphs:
        if not paragraph.runs:
            run = paragraph.add_run()
            # Apply style even if run is initially empty, text might be set later or by shape's text
            _apply_run_style(run, font_name, font_size_pt, font_color_hex, is_bold)
            if hasattr(shape_object, 'text') and not shape_object.text and run.text:
                 run.text = "" # Clear default text if shape_object.text is empty
        else:
            for run in paragraph.runs:
                _apply_run_style(run, font_name, font_size_pt, font_color_hex, is_bold)
    
    # If shape has text directly (e.g. from a template or if text_frame.text was set) but no paragraphs were formatted
    if not text_frame.paragraphs and hasattr(shape_object, 'text') and shape_object.text:
        p = text_frame.add_paragraph()
        run = p.add_run()
        run.text = shape_object.text # Ensure the shape's text is set to the run
        _apply_run_style(run, font_name, font_size_pt, font_color_hex, is_bold)


def _apply_slide_background(slide, background_color_hex: str):
    """Internal helper to apply a specific background color to a slide."""
    try:
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(background_color_hex)
    except Exception as e:
        logger.warning(f"Could not set slide background with color {background_color_hex}: {e}")

def create_presentation_from_data(
    slide_data_list: List[Dict[str, Any]],
    output_filename_base: str = "presentation",
    apply_styles: bool = True,
    theme_suggestions: Optional[List[str]] = None
    # image_paths: Dict[int, Optional[str]] = None # For future image generation
) -> str:
    """
    Creates a PowerPoint presentation from structured slide data, applying thematic styling.
    Returns the full path to the saved .pptx file.
    """
    # if image_paths is None: image_paths = {}

    logger.info(f"Starting PPT creation for {len(slide_data_list)} slides. Styles enabled: {apply_styles}. Theme suggestions: {theme_suggestions}")
    
    selected_theme_name = DEFAULT_THEME_NAME
    if apply_styles and theme_suggestions:
        for theme_name in theme_suggestions:
            if theme_name in THEME_STYLES:
                selected_theme_name = theme_name
                logger.info(f"Using theme: {selected_theme_name}")
                break
        else: # No break
            logger.info(f"None of the suggested themes {theme_suggestions} found. Using default theme: {DEFAULT_THEME_NAME}")
    elif not apply_styles:
         logger.info("Styling is disabled. Presentation will have default PPTX styles.")
    else: # apply_styles is True but no theme_suggestions
        logger.info(f"No theme suggestions provided. Using default theme: {DEFAULT_THEME_NAME}")
        
    current_style = THEME_STYLES[selected_theme_name] if apply_styles else THEME_STYLES[DEFAULT_THEME_NAME] # Fallback for safety if apply_styles is false but we try to use parts of current_style
    
    prs = Presentation()
    os.makedirs(PPT_OUTPUT_DIR, exist_ok=True)
    unique_id = uuid.uuid4().hex[:8]
    output_filename = f"{output_filename_base}_{unique_id}.pptx"
    full_path = os.path.join(PPT_OUTPUT_DIR, output_filename)

    if not slide_data_list:
        logger.warning("No slide data provided. Creating empty PPT with default theme background if styles are on.")
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        if apply_styles:
            _apply_slide_background(slide, current_style["colors"]["background"])
        if slide.shapes.title: 
            slide.shapes.title.text = "Empty Presentation"
            if apply_styles: # Basic styling for empty presentation title
                 _style_text_shape(slide.shapes.title, current_style, is_title_style=True)
        prs.save(full_path)
        return full_path

    # --- Title Slide ---
    logger.debug("Processing first slide as title slide...")
    title_slide_data = slide_data_list[0]
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    if apply_styles:
        _apply_slide_background(slide, current_style["colors"]["background"])

    main_ppt_title = title_slide_data.get("title", "AI Generated Presentation")
    main_ppt_subtitle = "Content Overview"
    if isinstance(title_slide_data.get("points"), list) and title_slide_data.get("points"):
        main_ppt_subtitle = title_slide_data.get("points")[0]

    title_shape = slide.shapes.title
    subtitle_shape_obj = None
    if len(slide.placeholders) > 1:
        try: subtitle_shape_obj = slide.placeholders[1]
        except IndexError: logger.warning("Title slide layout (0) no placeholder at index 1 for subtitle.")
    
    if title_shape:
        title_shape.text = main_ppt_title
        if apply_styles: _style_text_shape(title_shape, current_style, is_title_style=True)
    
    if subtitle_shape_obj:
        subtitle_shape_obj.text = main_ppt_subtitle
        if apply_styles: _style_text_shape(subtitle_shape_obj, current_style, is_title_style=False)
    logger.debug("Title slide finished.")

    # --- Content Slides ---
    content_slide_layout = prs.slide_layouts[1] # Title and Content Layout
    for i, slide_content_dict in enumerate(slide_data_list[1:]):
        actual_index = i + 1
        logger.debug(f"Creating content slide {i+1} (original index {actual_index})...")
        if not isinstance(slide_content_dict, dict):
            logger.warning(f"Skipping invalid content slide data: {slide_content_dict}"); continue
        
        slide = prs.slides.add_slide(content_slide_layout)
        if apply_styles:
            _apply_slide_background(slide, current_style["colors"]["background"])

        slide_title_text = slide_content_dict.get("title", f"Slide {actual_index + 1}")
        points = slide_content_dict.get("points", [])
        if not isinstance(points, list):
            logger.warning(f"Points for '{slide_title_text}' not list."); points = []
        
        if slide.shapes.title:
            slide.shapes.title.text = slide_title_text
            if apply_styles: _style_text_shape(slide.shapes.title, current_style, is_title_style=True)
        
        body_shape = None
        if len(slide.placeholders) > 1:
            try: body_shape = slide.placeholders[1]
            except IndexError: logger.warning(f"No placeholder at index 1 for '{slide_title_text}'.")
        
        if body_shape:
            tf = body_shape.text_frame; tf.clear()
            # Determine body text style once
            body_font_name = current_style["font"]
            body_font_color_hex = current_style["colors"]["text"]
            body_font_size_pt = Pt(random.randint(16, 20)) # Keep random for now
            body_is_bold = False

            for point_text in points:
                if isinstance(point_text, str):
                    p = tf.add_paragraph(); p.text = point_text; p.level = 0
                    if apply_styles and p.runs:
                         # Pass specific style parameters for body points
                        _apply_run_style(p.runs[0], body_font_name, body_font_size_pt, body_font_color_hex, body_is_bold)
                else: logger.warning(f"Invalid point type: {point_text} in '{slide_title_text}'")
            # image_path = image_paths.get(actual_index)
            # if image_path and os.path.exists(image_path):
            #     try:
            #         # Example placement: Adjust as needed
            #         slide.shapes.add_picture(image_path, Inches(6), Inches(1.5), height=Inches(2.5))
            #         logger.info(f"Added image {image_path} to slide {actual_index}")
            #     except Exception as e:
            #         logger.error(f"Failed to add picture to slide {actual_index}: {e}")

        else: logger.warning(f"No body placeholder for slide: {slide_title_text}")
        logger.debug(f"Content slide {i+1} finished.")

    try:
        logger.info(f"Saving PPT file with theme '{selected_theme_name}' (if styles applied)...")
        prs.save(full_path)
        logger.info(f"PPT saved to {full_path}"); return full_path
    except Exception as e:
        logger.error(f"Failed to save PPT {full_path}: {e}", exc_info=True)
        # Re-raise or handle as appropriate for the main endpoint
        raise