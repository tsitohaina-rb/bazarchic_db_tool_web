"""
Image Extraction Routes Blueprint
Extract product image URLs by EAN or REF
"""

import os
import shutil
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from services.image_service import ImageExtractorService

images_bp = Blueprint('images', __name__, url_prefix='/images')


@images_bp.route('/extractor')
def extractor():
    """Image URL extractor page"""
    return render_template('images_extractor.html')


@images_bp.route('/extractor/export', methods=['POST'])
def extractor_export():
    """Extract and export product image URLs"""
    try:
        search_type = request.form.get('search_type', 'ean')
        search_method = request.form.get('search_method', 'single')
        
        codes = []
        
        # Get codes based on method
        if search_method == 'single':
            code = request.form.get('code', '').strip()
            if code:
                codes = [code]
        
        elif search_method == 'multiple':
            codes_input = request.form.get('codes', '').strip()
            if codes_input:
                codes = [c.strip() for c in codes_input.replace(',', '\n').split('\n') if c.strip()]
        
        elif search_method == 'file':
            if 'file' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(url_for('images.extractor'))
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('images.extractor'))
            
            filename = secure_filename(file.filename)
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                codes = [line.strip() for line in f if line.strip()]
            
            os.remove(filepath)
        
        if not codes:
            flash(f'No {search_type.upper()} codes provided', 'error')
            return redirect(url_for('images.extractor'))
        
        print(f"Extracting images for {len(codes)} {search_type.upper()} code(s)...")
        
        # Use image service
        extractor = ImageExtractorService()
        file_all, file_found, file_not_found = extractor.export_to_csv(codes, search_type)
        extractor.close()
        
        if file_all and file_found and file_not_found:
            # Create export directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_dir = os.path.join('exports', f"images_{search_type}_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)
            
            # Move files to export directory
            final_all = os.path.join(export_dir, os.path.basename(file_all))
            final_found = os.path.join(export_dir, os.path.basename(file_found))
            final_not_found = os.path.join(export_dir, os.path.basename(file_not_found))
            
            shutil.move(file_all, final_all)
            shutil.move(file_found, final_found)
            shutil.move(file_not_found, final_not_found)
            
            # Create ZIP file
            zip_filename = f"{export_dir}.zip"
            shutil.make_archive(export_dir, 'zip', export_dir)
            
            # Clean up directory
            try:
                shutil.rmtree(export_dir)
            except:
                pass
            
            flash(f'Image URLs extracted successfully!', 'success')
            
            # Send ZIP file
            response = send_file(zip_filename, as_attachment=True, 
                               download_name=f"images_{search_type}_{timestamp}.zip")
            
            # Clean up ZIP after sending
            @response.call_on_close
            def cleanup_zip():
                try:
                    if os.path.exists(zip_filename):
                        os.remove(zip_filename)
                except:
                    pass
            
            return response
        else:
            flash('No images found or extraction failed', 'error')
            return redirect(url_for('images.extractor'))
            
    except Exception as e:
        flash(f'Extraction error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('images.extractor'))
