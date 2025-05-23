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
    PROFESSIONAL_COLORS_HEX,
    PROFESSIONAL_FONT_NAMES,
    SUBTLE_BACKGROUND_COLORS_HEX,
    PPT_OUTPUT_DIR
)

logger = logging.getLogger(__name__)

def _apply_run_style(run, is_title_style=False):
    """Internal helper to style a pptx run object."""
    if is_title_style:
        run.font.color.rgb = RGBColor.from_string(random.choice(list(PROFESSIONAL_COLORS_HEX.values())))
        run.font.name = random.choice(PROFESSIONAL_FONT_NAMES)
        run.font.size = Pt(random.randint(30, 38))
        run.font.bold = random.choice([True, False])
    else:  # Body style
        run.font.name = random.choice(PROFESSIONAL_FONT_NAMES[:2])
        run.font.size = Pt(random.randint(16, 20))
        run.font.color.rgb = RGBColor.from_string("333333")

def _style_text_shape(shape_object, is_title_style=False):
    """Internal helper to style text within a shape object."""
    if not hasattr(shape_object, 'has_text_frame') or not shape_object.has_text_frame:
        return
    text_frame = shape_object.text_frame
    for paragraph in text_frame.paragraphs:
        if not paragraph.runs:
            run = paragraph.add_run()
            _apply_run_style(run, is_title_style=is_title_style)
            if hasattr(shape_object, 'text') and not shape_object.text and run.text:
                 run.text = "" 
        else:
            for run in paragraph.runs:
                _apply_run_style(run, is_title_style=is_title_style)
    if not text_frame.paragraphs and hasattr(shape_object, 'text') and shape_object.text: # If shape has text but no paras
        p = text_frame.add_paragraph()
        run = p.add_run()
        run.text = shape_object.text 
        _apply_run_style(run, is_title_style=is_title_style)


def _apply_random_slide_background(slide):
    """Internal helper to apply random background to a slide."""
    if SUBTLE_BACKGROUND_COLORS_HEX:
        try:
            fill = slide.background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor.from_string(random.choice(SUBTLE_BACKGROUND_COLORS_HEX))
        except Exception as e:
            logger.warning(f"Could not set slide background: {e}")

def create_presentation_from_data(
    slide_data_list: List[Dict[str, Any]],
    output_filename_base: str = "presentation",
    apply_styles: bool = True
    # image_paths: Dict[int, Optional[str]] = None # For future image generation
) -> str:
    """
    Creates a PowerPoint presentation from structured slide data.
    Returns the full path to the saved .pptx file.
    """
    # if image_paths is None: image_paths = {} # For future image generation

    logger.info(f"Starting PPT creation for {len(slide_data_list)} slides. Styles enabled: {apply_styles}")
    prs = Presentation()
    os.makedirs(PPT_OUTPUT_DIR, exist_ok=True)
    unique_id = uuid.uuid4().hex[:8]
    output_filename = f"{output_filename_base}_{unique_id}.pptx"
    full_path = os.path.join(PPT_OUTPUT_DIR, output_filename)

    if not slide_data_list:
        logger.warning("No slide data provided to create_presentation_from_data. Creating empty PPT.")
        # Create a single empty title slide for an empty presentation
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        if slide.shapes.title: slide.shapes.title.text = "Empty Presentation"
        prs.save(full_path)
        return full_path

    # --- Title Slide (expects first item from AI to be title slide info) ---
    logger.debug("Processing first slide as title slide...")
    title_slide_data = slide_data_list[0]
    title_slide_layout = prs.slide_layouts[0]  # Title Slide Layout
    slide = prs.slides.add_slide(title_slide_layout)
    if apply_styles: _apply_random_slide_background(slide)

    main_ppt_title = title_slide_data.get("title", "AI Generated Presentation")
    main_ppt_subtitle = "Content Overview" # Default subtitle
    if isinstance(title_slide_data.get("points"), list) and title_slide_data.get("points"):
        main_ppt_subtitle = title_slide_data.get("points")[0] 

    title_shape = slide.shapes.title
    subtitle_shape_obj = None
    if len(slide.placeholders) > 1:
        try: subtitle_shape_obj = slide.placeholders[1]
        except IndexError: logger.warning("Title slide layout (0) no placeholder at index 1 for subtitle.")
    
    if title_shape:
        title_shape.text = main_ppt_title
        if apply_styles: _style_text_shape(title_shape, is_title_style=True)
    
    if subtitle_shape_obj:
        subtitle_shape_obj.text = main_ppt_subtitle
        if apply_styles: _style_text_shape(subtitle_shape_obj, is_title_style=False)
    logger.debug("Title slide finished.")

    # --- Content Slides ---
    content_slide_layout = prs.slide_layouts[1]  # Title and Content Layout
    for i, slide_content_dict in enumerate(slide_data_list[1:]): # Start from the second item for content
        actual_index = i + 1 # To match original list index for logging/image mapping
        logger.debug(f"Creating content slide {i+1} (original index {actual_index})...")
        if not isinstance(slide_content_dict, dict):
            logger.warning(f"Skipping invalid content slide data: {slide_content_dict}"); continue
        
        slide = prs.slides.add_slide(content_slide_layout)
        if apply_styles: _apply_random_slide_background(slide)

        slide_title_text = slide_content_dict.get("title", f"Slide {actual_index + 1}")
        points = slide_content_dict.get("points", [])
        if not isinstance(points, list):
            logger.warning(f"Points for '{slide_title_text}' not list."); points = []
        
        if slide.shapes.title:
            slide.shapes.title.text = slide_title_text
            if apply_styles: _style_text_shape(slide.shapes.title, is_title_style=True)
        
        body_shape = None
        if len(slide.placeholders) > 1: # Body is typically placeholder 1 for layout 1
            try: body_shape = slide.placeholders[1]
            except IndexError: logger.warning(f"No placeholder at index 1 for '{slide_title_text}'.")
        
        if body_shape:
            tf = body_shape.text_frame; tf.clear()
            for point_text in points:
                if isinstance(point_text, str):
                    p = tf.add_paragraph(); p.text = point_text; p.level = 0
                    if apply_styles and p.runs: _apply_run_style(p.runs[0], is_title_style=False)
                else: logger.warning(f"Invalid point type: {point_text} in '{slide_title_text}'")
            # Add image here if image_paths[actual_index] exists
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
        logger.info("Saving PPT file..."); prs.save(full_path)
        logger.info(f"PPT saved to {full_path}"); return full_path
    except Exception as e:
        logger.error(f"Failed to save PPT {full_path}: {e}", exc_info=True)
        # Re-raise or handle as appropriate for the main endpoint
        raise