"""
Cloudinary Upload Routes Blueprint
Upload images from local storage or Dropbox to Cloudinary
"""

import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, jsonify
from services.cloudinary_service import CloudinaryService

cloudinary_bp = Blueprint('cloudinary', __name__, url_prefix='/cloudinary')


@cloudinary_bp.route('/local')
def local():
    """Local upload page"""
    return render_template('cloudinary_local.html')


@cloudinary_bp.route('/local/upload', methods=['POST'])
def local_upload():
    """Upload images from local folder to Cloudinary"""
    try:
        folder_path = request.form.get('folder_path', '').strip()
        max_workers = int(request.form.get('max_workers', 10))
        cloudinary_folder = request.form.get('cloudinary_folder', 'bazarchic_images').strip()
        
        if not folder_path:
            flash('Please provide a folder path', 'error')
            return redirect(url_for('cloudinary.local'))
        
        if not os.path.exists(folder_path):
            flash(f'Folder does not exist: {folder_path}', 'error')
            return redirect(url_for('cloudinary.local'))
        
        # Upload using service
        service = CloudinaryService()
        results = service.upload_from_local(folder_path, cloudinary_folder, max_workers)
        
        if results:
            # Save to CSV
            output_csv = f"cloudinary_local_upload_{os.path.basename(folder_path)}.csv"
            service.save_results_to_csv(results, output_csv)
            
            successful = sum(1 for r in results if r['status'] == 'success')
            flash(f'Upload completed! {successful}/{len(results)} images uploaded', 'success')
            
            # Send CSV file
            if os.path.exists(output_csv):
                response = send_file(output_csv, as_attachment=True)
                
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(output_csv):
                            os.remove(output_csv)
                    except:
                        pass
                
                return response
        
        flash('No images found or upload failed', 'error')
        return redirect(url_for('cloudinary.local'))
            
    except Exception as e:
        flash(f'Upload error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
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
            # Save to CSV
            folder_name = os.path.basename(dropbox_path.rstrip('/'))
            output_csv = f"cloudinary_dropbox_upload_{folder_name}.csv"
            service.save_results_to_csv(results, output_csv)
            
            successful = sum(1 for r in results if r['status'] == 'success')
            flash(f'Upload completed! {successful}/{len(results)} images uploaded', 'success')
            
            # Send CSV file
            if os.path.exists(output_csv):
                response = send_file(output_csv, as_attachment=True)
                
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
