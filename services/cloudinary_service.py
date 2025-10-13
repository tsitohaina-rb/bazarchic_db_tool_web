"""
Cloudinary Upload Service
Handle image uploads from local storage and Dropbox to Cloudinary
"""

import os
import csv
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import cloudinary
import cloudinary.uploader
import dropbox
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print(os.getenv('CLOUDINARY_CLOUD_NAME'))
print(os.getenv('CLOUDINARY_API_KEY'))
print(os.getenv('CLOUDINARY_API_SECRET'))


class CloudinaryService:
    """Service for uploading images to Cloudinary"""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    
    def __init__(self):
        self.upload_stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        self.stats_lock = Lock()
    
    def upload_from_local(self, folder_path: str, cloudinary_folder: str = 'bazarchic_images',
                         max_workers: int = 10) -> List[Dict]:
        """
        Upload images from local folder to Cloudinary
        
        Args:
            folder_path: Local folder path containing images
            cloudinary_folder: Destination folder in Cloudinary
            max_workers: Number of concurrent upload threads
            
        Returns:
            List of dicts with upload results
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            print(f"Error: Folder '{folder_path}' does not exist")
            return []
        
        # Get all image files
        image_files = [
            f for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]
        
        if not image_files:
            print("No supported image files found")
            return []
        
        print(f"Found {len(image_files)} images to upload")
        print(f"Using {max_workers} concurrent threads")
        
        # Reset stats
        self.upload_stats = {
            'total': len(image_files),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        results = []
        
        # Upload with thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._upload_single_file, str(file_path), cloudinary_folder): file_path
                for file_path in image_files
            }
            
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update stats
                    with self.stats_lock:
                        if result['status'] == 'success':
                            self.upload_stats['successful'] += 1
                        else:
                            self.upload_stats['failed'] += 1
                            if len(self.upload_stats['errors']) < 10:
                                self.upload_stats['errors'].append(result['error'])
                    
                    # Progress logging
                    completed = self.upload_stats['successful'] + self.upload_stats['failed']
                    if completed % 10 == 0:
                        print(f"Progress: {completed}/{len(image_files)} "
                              f"({self.upload_stats['successful']} successful, "
                              f"{self.upload_stats['failed']} failed)")
                
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")
                    results.append({
                        'local_filename': file_path.stem,
                        'cloudinary_url': 'UPLOAD_FAILED',
                        'status': 'failed',
                        'error': str(e)
                    })
        
        print(f"\n{'='*60}")
        print(f"Upload Summary:")
        print(f"  Total: {self.upload_stats['total']}")
        print(f"  Successful: {self.upload_stats['successful']}")
        print(f"  Failed: {self.upload_stats['failed']}")
        if self.upload_stats['errors']:
            print(f"\nFirst errors:")
            for error in self.upload_stats['errors'][:5]:
                print(f"  - {error}")
        
        return results
    
    def upload_from_dropbox(self, dropbox_path: str, max_workers: int = 10) -> List[Dict]:
        """
        Upload images from Dropbox to Cloudinary (direct transfer, no local download)
        
        Args:
            dropbox_path: Path to folder in Dropbox
            max_workers: Number of concurrent upload threads
            
        Returns:
            List of dicts with upload results
        """
        try:
            dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))
            
            # Ensure path starts with /
            if not dropbox_path.startswith('/'):
                dropbox_path = '/' + dropbox_path
            
            print(f"Scanning Dropbox folder: {dropbox_path}")
            
            # List files in folder
            try:
                result = dbx.files_list_folder(dropbox_path)
            except dropbox.exceptions.ApiError as e:
                print(f"Error accessing Dropbox folder: {e}")
                return []
            
            # Filter image files
            image_files = [
                entry for entry in result.entries
                if isinstance(entry, dropbox.files.FileMetadata) and
                Path(entry.name).suffix.lower() in self.SUPPORTED_EXTENSIONS
            ]
            
            if not image_files:
                print("No supported image files found in Dropbox folder")
                return []
            
            print(f"Found {len(image_files)} images to upload")
            print(f"Using {max_workers} concurrent threads")
            
            # Reset stats
            self.upload_stats = {
                'total': len(image_files),
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            results = []
            
            # Upload with thread pool
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._upload_from_dropbox_url, dbx, entry): entry
                    for entry in image_files
                }
                
                for future in as_completed(futures):
                    entry = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Update stats
                        with self.stats_lock:
                            if result['status'] == 'success':
                                self.upload_stats['successful'] += 1
                            else:
                                self.upload_stats['failed'] += 1
                                if len(self.upload_stats['errors']) < 10:
                                    self.upload_stats['errors'].append(result['error'])
                        
                        # Progress logging
                        completed = self.upload_stats['successful'] + self.upload_stats['failed']
                        if completed % 10 == 0:
                            print(f"Progress: {completed}/{len(image_files)} "
                                  f"({self.upload_stats['successful']} successful, "
                                  f"{self.upload_stats['failed']} failed)")
                    
                    except Exception as e:
                        print(f"Error processing {entry.name}: {e}")
                        results.append({
                            'local_filename': Path(entry.name).stem,
                            'cloudinary_url': 'UPLOAD_FAILED',
                            'status': 'failed',
                            'error': str(e)
                        })
            
            print(f"\n{'='*60}")
            print(f"Upload Summary:")
            print(f"  Total: {self.upload_stats['total']}")
            print(f"  Successful: {self.upload_stats['successful']}")
            print(f"  Failed: {self.upload_stats['failed']}")
            
            return results
            
        except Exception as e:
            print(f"Dropbox error: {e}")
            return []
    
    def list_dropbox_folders(self) -> List[str]:
        """List all folders in Dropbox account"""
        try:
            dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))
            
            folders = []
            result = dbx.files_list_folder('')
            
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FolderMetadata):
                    folders.append(entry.path_display)
            
            # Handle pagination
            while result.has_more:
                result = dbx.files_list_folder_continue(result.cursor)
                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FolderMetadata):
                        folders.append(entry.path_display)
            
            return sorted(folders)
            
        except Exception as e:
            print(f"Error listing Dropbox folders: {e}")
            return []
    
    def _upload_single_file(self, file_path: str, cloudinary_folder: str) -> Dict:
        """Upload a single file to Cloudinary"""
        file_path = Path(file_path)
        filename_without_ext = file_path.stem
        
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                str(file_path),
                folder=cloudinary_folder,
                public_id=filename_without_ext,
                use_filename=True,
                unique_filename=False,
                overwrite=True,
                resource_type='image'
            )
            
            return {
                'local_filename': filename_without_ext,
                'cloudinary_url': upload_result['secure_url'],
                'status': 'success',
                'error': None
            }
            
        except Exception as e:
            return {
                'local_filename': filename_without_ext,
                'cloudinary_url': 'UPLOAD_FAILED',
                'status': 'failed',
                'error': str(e)
            }
    
    def _upload_from_dropbox_url(self, dbx: dropbox.Dropbox, 
                                 entry: dropbox.files.FileMetadata) -> Dict:
        """Upload image from Dropbox to Cloudinary using temporary link"""
        filename_without_ext = Path(entry.name).stem
        
        try:
            # Get temporary link (valid for 4 hours)
            link = dbx.files_get_temporary_link(entry.path_lower)
            temp_url = link.link
            
            # Upload to Cloudinary from URL
            upload_result = cloudinary.uploader.upload(
                temp_url,
                folder='bazarchic_dropbox',
                public_id=filename_without_ext,
                use_filename=True,
                unique_filename=False,
                overwrite=True,
                resource_type='image'
            )
            
            return {
                'local_filename': filename_without_ext,
                'cloudinary_url': upload_result['secure_url'],
                'status': 'success',
                'error': None
            }
            
        except Exception as e:
            return {
                'local_filename': filename_without_ext,
                'cloudinary_url': 'UPLOAD_FAILED',
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def save_results_to_csv(results: List[Dict], output_file: str):
        """Save upload results to CSV file"""
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['local_filename', 'cloudinary_url'])
            
            for result in results:
                writer.writerow([
                    result['local_filename'],
                    result['cloudinary_url']
                ])
        
        print(f"Results saved to: {output_file}")
