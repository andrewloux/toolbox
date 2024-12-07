import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import logging
import tempfile
from typing import List, Dict
import json
import math
from operator import itemgetter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Increase PIL image size limit
Image.MAX_IMAGE_PIXELS = None

def split_image_into_chunks(image: Image.Image, chunk_height: int = 10000) -> List[Dict]:
    """Split a large image into manageable chunks."""
    width, height = image.size
    chunks = []
    
    num_chunks = math.ceil(height / chunk_height)
    logger.info(f"Splitting image of height {height} into {num_chunks} chunks")
    
    for i in range(num_chunks):
        start_y = i * chunk_height
        end_y = min((i + 1) * chunk_height, height)
        chunk = image.crop((0, start_y, width, end_y))
        chunks.append({
            'image': chunk,
            'offset_y': start_y
        })
    
    return chunks

def perform_ocr_on_chunk(chunk: Dict) -> List[Dict]:
    """Perform OCR on a single chunk of the image."""
    image = chunk['image']
    offset_y = chunk['offset_y']
    
    try:
        # Perform OCR with additional configuration for better results
        ocr_config = '--oem 3 --psm 1'
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=ocr_config)
        
        # Clean up the OCR data
        cleaned_text = []
        for i in range(len(ocr_data['text'])):
            if int(ocr_data['conf'][i]) > 30:  # Filter out low-confidence text
                text = ocr_data['text'][i].strip()
                if text:  # Only include non-empty text
                    cleaned_text.append({
                        'text': text,
                        'confidence': ocr_data['conf'][i],
                        'block_num': ocr_data['block_num'][i],
                        'line_num': ocr_data['line_num'][i],
                        'word_num': ocr_data['word_num'][i],
                        'left': ocr_data['left'][i],
                        'top': ocr_data['top'][i] + offset_y,  # Adjust Y coordinate for chunk position
                        'width': ocr_data['width'][i],
                        'height': ocr_data['height'][i]
                    })
        
        return cleaned_text
    finally:
        image.close()

def organize_text_blocks(text_blocks: List[Dict], line_height_threshold: int = 50) -> List[str]:
    """Organize text blocks into lines based on vertical position."""
    if not text_blocks:
        return []
    
    # Sort blocks by vertical position first
    sorted_blocks = sorted(text_blocks, key=itemgetter('top'))
    
    # Group blocks into lines
    lines = []
    current_line = []
    current_y = sorted_blocks[0]['top']
    
    for block in sorted_blocks:
        # If this block is roughly on the same line (within threshold)
        if abs(block['top'] - current_y) <= line_height_threshold:
            current_line.append(block)
        else:
            # Sort current line by horizontal position and add to lines
            if current_line:
                current_line.sort(key=itemgetter('left'))
                line_text = ' '.join(b['text'] for b in current_line)
                lines.append(line_text)
            # Start new line
            current_line = [block]
            current_y = block['top']
    
    # Don't forget the last line
    if current_line:
        current_line.sort(key=itemgetter('left'))
        line_text = ' '.join(b['text'] for b in current_line)
        lines.append(line_text)
    
    return lines

def perform_ocr_on_page(image: Image.Image, page_num: int) -> Dict:
    """Process a single page by splitting it into chunks if necessary."""
    try:
        logger.info(f"Processing page {page_num}")
        width, height = image.size
        logger.info(f"Page {page_num} dimensions: {width}x{height}")
        
        chunks = split_image_into_chunks(image)
        all_text = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)} of page {page_num}")
            chunk_text = perform_ocr_on_chunk(chunk)
            all_text.extend(chunk_text)
        
        # Organize text into readable lines
        organized_lines = organize_text_blocks(all_text)
        
        return {
            'page_number': page_num,
            'page_dimensions': {'width': width, 'height': height},
            'raw_content': all_text,  # Keep the detailed data
            'text_content': organized_lines,  # Add organized text content
            'full_text': '\n'.join(organized_lines)  # Add full text as single string
        }
        
    except Exception as e:
        logger.error(f"Error processing page {page_num}: {str(e)}")
        raise
    finally:
        image.close()

def process_pdf(input_pdf_path: str, output_json_path: str, dpi: int = 300):
    """Process PDF file and extract text content through OCR."""
    logger.info(f"Starting OCR processing of {input_pdf_path}")
    
    all_pages_data = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            pages = convert_from_path(
                input_pdf_path,
                dpi=dpi,
                output_folder=temp_dir,
                fmt='jpg',
                thread_count=4
            )
            total_pages = len(pages)
            logger.info(f"Found {total_pages} pages")
            
            for i, page in enumerate(pages, start=1):
                try:
                    page_data = perform_ocr_on_page(page, i)
                    all_pages_data.append(page_data)
                    logger.info(f"Completed OCR for page {i}/{total_pages}")
                    
                    # Print the organized text content for immediate review
                    logger.info(f"\nPage {i} Text Content:")
                    for line in page_data['text_content']:
                        logger.info(line)
                    logger.info("-" * 80)
                    
                except Exception as e:
                    logger.error(f"Failed to process page {i}: {str(e)}")
                    continue
            
            # Save results
            logger.info("Saving OCR results...")
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'pdf_name': os.path.basename(input_pdf_path),
                    'total_pages': total_pages,
                    'pages': all_pages_data
                }, f, ensure_ascii=False, indent=2)
            
            # Create a simple text file with just the text content
            text_output_path = output_json_path.rsplit('.', 1)[0] + '.txt'
            with open(text_output_path, 'w', encoding='utf-8') as f:
                for page in all_pages_data:
                    f.write(f"\n\n=== Page {page['page_number']} ===\n\n")
                    f.write(page['full_text'])
            
            logger.info(f"OCR completed. Results saved to {output_json_path}")
            logger.info(f"Plain text saved to {text_output_path}")
            
        except Exception as e:
            logger.error(f"Error during PDF processing: {str(e)}")
            raise

if __name__ == "__main__":
    input_pdf = "output_right_half.pdf"
    output_json = "extracted_text.json"
    
    if not os.path.exists(input_pdf):
        logger.error(f"Error: Input file '{input_pdf}' not found!")
    else:
        process_pdf(input_pdf, output_json, dpi=300)
