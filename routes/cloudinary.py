"""
Cloudinary Upload Routes Blueprint
Upload images from local storage or Dropbox to Cloudinary
"""

import os
import tempfile
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from services.cloudinary_service import CloudinaryService

cloudinary_bp = Blueprint('cloudinary', __name__, url_prefix='/cloudinary')


@cloudinary_bp.route('/local')
def local():
    """Local upload page"""
    return render_template('cloudinary_local.html')


@cloudinary_bp.route('/local/upload', methods=['POST'])
def local_upload():
    """Upload images from uploaded files to Cloudinary"""
    temp_dir = None
    try:
        max_workers = int(request.form.get('max_workers', 10))
        cloudinary_folder = request.form.get('cloudinary_folder', 'bazarchic_images').strip()
        
        # Handle file uploads
        if 'files' not in request.files:
            flash('No files uploaded', 'error')
            return redirect(url_for('cloudinary.local'))
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            flash('No files selected', 'error')
            return redirect(url_for('cloudinary.local'))
        
        # Create temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp(prefix='cloudinary_upload_')
        
        # Save uploaded files to temporary directory
        saved_count = 0
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(temp_dir, filename))
                saved_count += 1
        
        print(f"✅ Saved {saved_count} files to temporary directory: {temp_dir}")
        
        # Upload from temporary directory
        service = CloudinaryService()
        results = service.upload_from_local(temp_dir, cloudinary_folder, max_workers)
        
        if results:
            # Save to CSV in temporary location
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', 
                                                   prefix=f'cloudinary_upload_{timestamp}_')
            output_csv = temp_csv.name
            temp_csv.close()
            
            service.save_results_to_csv(results, output_csv)
            
            successful = sum(1 for r in results if r['status'] == 'success')
            failed = sum(1 for r in results if r['status'] == 'failed')
            flash(f'Upload completed! ✅ Success: {successful} | ❌ Failed: {failed}', 'success')
            
            # Send CSV file
            if os.path.exists(output_csv):
                response = send_file(output_csv, as_attachment=True,
                                   download_name=f'cloudinary_upload_{timestamp}.csv')
                
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(output_csv):
                            os.remove(output_csv)
                        if temp_dir and os.path.exists(temp_dir):
                            import shutil
                            shutil.rmtree(temp_dir)
                            print(f"🧹 Cleaned up temporary directory: {temp_dir}")
                    except Exception as e:
                        print(f"⚠️ Cleanup warning: {e}")
                
                return response
        
        flash('No images found or upload failed', 'error')
        return redirect(url_for('cloudinary.local'))
            
    except Exception as e:
        flash(f'Upload error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
        
        return redirect(url_for('cloudinary.local'))


@cloudinary_bp.route('/dropbox')
def dropbox():
    """Dropbox upload page"""
    try:
        # Automatically load folders on page load
        service = CloudinaryService()
        folders = service.list_dropbox_folders()
        return render_template('cloudinary_dropbox.html', folders=folders)
    except Exception as e:
        print(f"Error loading Dropbox folders: {e}")
        return render_template('cloudinary_dropbox.html', folders=[], error=str(e))


@cloudinary_bp.route('/dropbox/list', methods=['POST'])
def dropbox_list():
    """List Dropbox folders"""
    try:
        service = CloudinaryService()
        folders = service.list_dropbox_folders()
        
        if folders:
            return jsonify({
                'success': True,
                'folders': folders,
                'count': len(folders)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No folders found or connection failed'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cloudinary_bp.route('/dropbox/upload', methods=['POST'])
def dropbox_upload():
    """Upload images from Dropbox to Cloudinary"""
    try:
        dropbox_path = request.form.get('dropbox_path', '').strip()
        max_workers = int(request.form.get('max_workers', 10))
        
        if not dropbox_path:
            flash('Please provide a Dropbox folder path', 'error')
            return redirect(url_for('cloudinary.dropbox'))
        
        # Ensure path starts with /
        if not dropbox_path.startswith('/'):
            dropbox_path = '/' + dropbox_path
        
        # Upload using service
        service = CloudinaryService()
        results = service.upload_from_dropbox(dropbox_path, max_workers)
        
        if results:
            # Save to CSV in temporary location
            folder_name = os.path.basename(dropbox_path.rstrip('/'))
            temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv',
                                                   prefix=f'cloudinary_dropbox_{folder_name}_')
            output_csv = temp_csv.name
            temp_csv.close()
            
            service.save_results_to_csv(results, output_csv)
            
            successful = sum(1 for r in results if r['status'] == 'success')
            flash(f'Upload completed! {successful}/{len(results)} images uploaded', 'success')
            
            # Send CSV file
            if os.path.exists(output_csv):
                response = send_file(output_csv, as_attachment=True,
                                   download_name=f'cloudinary_dropbox_{folder_name}.csv')
                
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(output_csv):
                            os.remove(output_csv)
                    except:
                        pass
                
                return response
        
        flash('No images found or upload failed', 'error')
        return redirect(url_for('cloudinary.dropbox'))
            
    except Exception as e:
        flash(f'Upload error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('cloudinary.dropbox'))
