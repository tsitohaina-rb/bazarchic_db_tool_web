"""
Cloudinary Upload Routes Blueprint
Upload images from local storage or Dropbox to Cloudinary
Also handle downloading URLs from Cloudinary folders
"""

import os
import tempfile
from datetime import datetime
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


@cloudinary_bp.route('/download-urls')
def download_urls():
    """Download URLs page"""
    return render_template('cloudinary_download_urls.html')


@cloudinary_bp.route('/api/folders')
def api_get_folders():
    """API endpoint to get folder structure"""
    try:
        print("🔄 Starting folder discovery...")
        service = CloudinaryService()
        folder_structure = service.get_folder_structure()
        
        print(f"📂 Raw folder structure discovered: {len(folder_structure)} main folders")
        for main, subs in folder_structure.items():
            print(f"   • {main}: {len(subs)} subfolders")
        
        # Convert to format suitable for select options with better hierarchy
        folders = []
        
        # Sort main folders alphabetically
        sorted_main_folders = sorted(folder_structure.keys())
        
        for main_folder in sorted_main_folders:
            subfolders = folder_structure[main_folder]
            
            # Add main folder
            folders.append({
                'value': main_folder,
                'label': f"📁 {main_folder}",
                'type': 'main'
            })
            
            # Add all subfolders with proper indentation
            for subfolder in sorted(subfolders):
                # Calculate depth based on number of slashes
                depth = subfolder.count('/')
                indent = "  " * depth
                
                # Get the last part of the path for display
                display_name = subfolder.split('/')[-1] if '/' in subfolder else subfolder
                
                folders.append({
                    'value': subfolder,
                    'label': f"{indent}└─ {display_name}",
                    'type': 'sub',
                    'depth': depth,
                    'full_path': subfolder
                })
        
        print(f"📋 Prepared {len(folders)} folder options for dropdown")
        
        return jsonify({
            'success': True,
            'folders': folders,
            'total_folders': len(folders)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cloudinary_bp.route('/download-urls/export', methods=['POST'])
def export_urls():
    """Export URLs from selected folder to CSV"""
    try:
        folder_name = request.form.get('folder_name', '').strip()
        max_results = int(request.form.get('max_results', 500))
        use_search_api = request.form.get('use_search_api') == 'on'
        
        if not folder_name:
            flash('Please select a folder', 'error')
            return redirect(url_for('cloudinary.download_urls'))
        
        service = CloudinaryService()
        
        # Get images from folder
        images = service.get_images_from_folder(
            folder_name=folder_name,
            max_results=max_results,
            use_search_api=use_search_api
        )
        
        if not images:
            flash(f'No images found in folder "{folder_name}"', 'warning')
            return redirect(url_for('cloudinary.download_urls'))
        
        # Export to CSV
        csv_path = service.export_urls_to_csv(images, folder_name)
        
        # Generate download filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"{folder_name.replace('/', '_')}_URLs_{timestamp}.csv"
        
        # Send file with cleanup
        response = send_file(
            csv_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='text/csv'
        )
        
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(csv_path):
                    os.remove(csv_path)
            except:
                pass
        
        flash(f'Successfully exported {len(images)} image URLs from "{folder_name}"', 'success')
        return response
        
    except Exception as e:
        flash(f'Export error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('cloudinary.download_urls'))
