"""
Product Search Routes Blueprint
Search and export products by EAN or REF
"""

import os
import shutil
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from services.database_service import BazarchicDB
import traceback

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
def index():
    """Search products page"""
    return render_template('search.html')


@search_bp.route('/export', methods=['POST'])
def export():
    """Search and export products by EAN or REF"""
    try:
        search_method = request.form.get('search_method')
        search_type = request.form.get('search_type', 'ean')  # 'ean' or 'ref'
        export_type = request.form.get('export_type', 'comprehensive')
        
        codes = []
        
        # Get codes based on method
        if search_method == 'single':
            code = request.form.get('code', '').strip()
            if code:
                codes = [code]
        
        elif search_method == 'multiple':
            codes_input = request.form.get('codes', '').strip()
            if codes_input:
                codes = [code.strip() for code in codes_input.split(',') if code.strip()]
        
        elif search_method == 'file':
            if 'file' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(url_for('search.index'))
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('search.index'))
            
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
            return redirect(url_for('search.index'))
        
        print(f"🔍 Searching {len(codes)} {search_type.upper()} codes...")
        
        db = BazarchicDB()
        
        if export_type == 'comprehensive':
            # Search by EAN or REF
            if search_type == 'ean':
                result = db.export_comprehensive_csv(ean_filter=codes)
            else:  # REF search
                result = db.export_comprehensive_csv(ref_filter=codes)
            
            db.close()
            
            if result and result[0]:
                export_dir = result[0]
                counts = result[1]
                found_count, not_found_count, total_exported = counts
                
                # Create ZIP file
                zip_filename = f"{export_dir}.zip"
                shutil.make_archive(export_dir, 'zip', export_dir)
                
                # Clean up directory
                try:
                    shutil.rmtree(export_dir)
                except Exception as e:
                    print(f"Warning: Could not remove directory {export_dir}: {e}")
                
                flash(f'Export completed! Found: {found_count}, Not found: {not_found_count}, Total products: {total_exported}', 'success')
                
                # Send ZIP file
                response = send_file(zip_filename, as_attachment=True, 
                                   download_name=f"export_{os.path.basename(export_dir)}.zip")
                
                @response.call_on_close
                def cleanup_zip():
                    try:
                        if os.path.exists(zip_filename):
                            os.remove(zip_filename)
                    except:
                        pass
                
                return response
        
        flash('No products found', 'warning')
        return redirect(url_for('search.index'))
        
    except Exception as e:
        flash(f'Search error: {str(e)}', 'error')
        traceback.print_exc()
        return redirect(url_for('search.index'))
