"""
Cloudinary Upload Service
Handle image uploads from local storage and Dropbox to Cloudinary
Also handle downloading URLs from Cloudinary folders
"""

import os
import csv
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime
import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary import Search
import dropbox
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)


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
    
    def list_dropbox_folders(self, include_subdirs=True) -> List[str]:
        """
        List all folders in Dropbox account
        
        Args:
            include_subdirs: If True, lists all subdirectories recursively
        
        Returns:
            Sorted list of all folder paths
        """
        try:
            dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))
            all_folders = []
            
            def scan_folder(folder_path=''):
                """Recursively scan folders starting from folder_path"""
                try:
                    # List folder contents (non-recursive API call)
                    result = dbx.files_list_folder(
                        path=folder_path,
                        recursive=False,  # We handle recursion manually
                        include_deleted=False
                    )
                    
                    folders_to_scan = []
                    
                    # Process entries
                    for entry in result.entries:
                        if isinstance(entry, dropbox.files.FolderMetadata):
                            all_folders.append(entry.path_display)
                            if include_subdirs:
                                folders_to_scan.append(entry.path_display)
                    
                    # Handle pagination
                    while result.has_more:
                        result = dbx.files_list_folder_continue(result.cursor)
                        for entry in result.entries:
                            if isinstance(entry, dropbox.files.FolderMetadata):
                                all_folders.append(entry.path_display)
                                if include_subdirs:
                                    folders_to_scan.append(entry.path_display)
                    
                    # Recursively scan subfolders
                    if include_subdirs:
                        for subfolder in folders_to_scan:
                            scan_folder(subfolder)
                            
                except Exception as e:
                    print(f"⚠️  Error listing folder '{folder_path}': {e}")
            
            # Start scanning from root
            scan_folder('')
            
            print(f"📁 Found {len(all_folders)} folders in Dropbox (including subdirectories)")
            
            return sorted(all_folders)
            
        except Exception as e:
            print(f"❌ Error listing Dropbox folders: {e}")
            import traceback
            traceback.print_exc()
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

    def list_cloudinary_folders(self, max_pages: int = 50) -> List[str]:
        """
        List all folders in Cloudinary by scanning resources
        
        Args:
            max_pages: Safety cap on pagination loops
            
        Returns:
            Sorted list of discovered folder names
        """
        discovered = set()
        
        try:
            # Try root_folders API first
            try:
                root = cloudinary.api.root_folders()
                for f in root.get('folders', []):
                    name = f.get('name')
                    if name:
                        discovered.add(name)
            except Exception:
                pass  # root_folders not available on all plans
            
            # Scan resources for folder prefixes
            next_cursor = None
            page = 0
            
            while True:
                page += 1
                if page > max_pages:
                    break
                    
                if next_cursor:
                    resp = cloudinary.api.resources(
                        type='upload',
                        max_results=500,
                        next_cursor=next_cursor
                    )
                else:
                    resp = cloudinary.api.resources(
                        type='upload',
                        max_results=500
                    )
                
                resources = resp.get('resources', [])
                for r in resources:
                    public_id = r.get('public_id', '')
                    if '/' in public_id:
                        prefix = public_id.split('/')[0]
                        if prefix:
                            discovered.add(prefix)
                
                next_cursor = resp.get('next_cursor')
                if not next_cursor:
                    break
                    
        except Exception as e:
            print(f"Error scanning folders: {e}")
        
        return sorted(discovered)
    
    def get_folder_structure(self, max_pages: int = 100) -> Dict[str, List[str]]:
        """
        Comprehensively get all folder structure including deep subfolders
        Using the same method as the original download_cloudinary_urls.py script
        
        Returns:
            Dictionary with main folders as keys and all paths as values
        """
        folder_structure = {}
        discovered_paths = set()
        
        print("📂 Discovering folders in your Cloudinary account...")
        
        try:
            # Try root_folders API first (may not be enabled on all accounts/plans)
            try:
                root = cloudinary.api.root_folders()
                for f in root.get('folders', []):
                    name = f.get('name')
                    if name:
                        discovered_paths.add(name)
                        print(f"   • root folder: {name}")
            except Exception as e:
                print(f"   ⚠️  root_folders not available: {e}")

            # Comprehensive scan using paginated resources API
            print("🔍 Scanning all resources for folder prefixes...")
            next_cursor = None
            page = 0
            total_resources_scanned = 0
            
            while True:
                page += 1
                if page > max_pages:
                    print(f"   ⚠️  Stopping after {max_pages} pages (safety cap)")
                    break
                
                try:
                    if next_cursor:
                        resp = cloudinary.api.resources(
                            type='upload',
                            max_results=500,
                            next_cursor=next_cursor
                        )
                    else:
                        resp = cloudinary.api.resources(
                            type='upload', 
                            max_results=500
                        )
                    
                    resources = resp.get('resources', [])
                    total_resources_scanned += len(resources)
                    print(f"   Page {page}: {len(resources)} resources (Total scanned: {total_resources_scanned})")
                    
                    for r in resources:
                        public_id = r.get('public_id', '')
                        if '/' in public_id:
                            # Extract all folder levels from the public_id
                            parts = public_id.split('/')
                            # Add all possible folder paths
                            for i in range(1, len(parts)):
                                folder_path = '/'.join(parts[:i])
                                if folder_path:
                                    discovered_paths.add(folder_path)
                    
                    next_cursor = resp.get('next_cursor')
                    if not next_cursor:
                        print(f"   ✅ Completed scan - no more pages")
                        break
                        
                except Exception as e:
                    print(f"   ⚠️  Resource scan page {page} interrupted: {e}")
                    break
            
            print(f"📊 Total unique folder paths discovered: {len(discovered_paths)}")
            
            # Organize into hierarchical structure
            all_folders = sorted(discovered_paths)
            
            for path in all_folders:
                parts = path.split('/')
                main_folder = parts[0]
                
                if main_folder not in folder_structure:
                    folder_structure[main_folder] = []
                
                # Add the full path (including main folder itself and all subfolders)
                if path not in folder_structure[main_folder] and path != main_folder:
                    folder_structure[main_folder].append(path)
            
            # Sort subfolders for each main folder
            for main_folder in folder_structure:
                folder_structure[main_folder].sort()
            
            # Also add main folders that don't have subfolders
            for path in all_folders:
                if '/' not in path and path not in folder_structure:
                    folder_structure[path] = []
            
            print(f"📁 Organized into {len(folder_structure)} main folders")
            for main_folder, subfolders in folder_structure.items():
                print(f"   • {main_folder} ({len(subfolders)} subfolders)")
                
        except Exception as e:
            print(f"❌ Error getting folder structure: {e}")
        
        return folder_structure
    
    def get_images_from_folder(self, folder_name: str, max_results: int = 500, use_search_api: bool = False) -> List[Dict]:
        """
        Retrieve all images from a specific Cloudinary folder
        
        Args:
            folder_name: Name of the Cloudinary folder
            max_results: Maximum number of results to retrieve
            use_search_api: Whether to use Search API instead of resources API
            
        Returns:
            List of image resources
        """
        if use_search_api:
            return self._get_images_search_api(folder_name, max_results)
        else:
            return self._get_images_resources_api(folder_name, max_results)
    
    def _get_images_resources_api(self, folder_name: str, max_results: int) -> List[Dict]:
        """Get images using the resources API"""
        all_resources = []
        next_cursor = None
        
        try:
            while True:
                if next_cursor:
                    result = cloudinary.api.resources(
                        type='upload',
                        prefix=folder_name,
                        max_results=min(max_results, 500),
                        next_cursor=next_cursor
                    )
                else:
                    result = cloudinary.api.resources(
                        type='upload',
                        prefix=folder_name,
                        max_results=min(max_results, 500)
                    )
                
                resources = result.get('resources', [])
                all_resources.extend(resources)
                
                next_cursor = result.get('next_cursor')
                if not next_cursor or len(all_resources) >= max_results:
                    break
            
            return all_resources[:max_results]
            
        except Exception as e:
            print(f"Error retrieving images: {e}")
            return []
    
    def _get_images_search_api(self, folder_name: str, max_results: int) -> List[Dict]:
        """Get images using the Search API"""
        expression = f'folder="{folder_name}"'
        search = Search().expression(expression).max_results(500)
        all_resources = []
        
        try:
            data = search.execute()
            batch = data.get('resources', [])
            all_resources.extend(batch)
            
            while 'next_cursor' in data:
                if max_results != -1 and len(all_resources) >= max_results:
                    break
                cursor = data['next_cursor']
                search = Search().expression(expression).max_results(500).next_cursor(cursor)
                data = search.execute()
                batch = data.get('resources', [])
                all_resources.extend(batch)
            
            return all_resources if max_results == -1 else all_resources[:max_results]
            
        except Exception as e:
            print(f"Search API error: {e}")
            return []
    
    def export_urls_to_csv(self, images: List[Dict], folder_name: str) -> str:
        """
        Export image URLs to CSV file in a temporary location
        
        Args:
            images: List of image resources from Cloudinary
            folder_name: Name of the folder (for filename)
            
        Returns:
            Path to the created CSV file
        """
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{folder_name.replace('/', '_')}_URLs_{timestamp}.csv"
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.csv', 
            prefix=f"{folder_name.replace('/', '_')}_", 
            delete=False,
            encoding='utf-8',
            newline=''
        )
        
        # Prepare CSV data
        csv_data = []
        
        for img in images:
            public_id = img.get('public_id', '')
            filename = os.path.basename(public_id) if public_id else 'unknown'
            
            csv_data.append({
                'filename': filename,
                'public_id': public_id,
                'secure_url': img.get('secure_url', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'format': img.get('format', ''),
                'bytes': img.get('bytes', ''),
                'created_at': img.get('created_at', '')
            })
        
        # Sort by filename for consistency
        csv_data.sort(key=lambda x: x['filename'])
        
        # Write CSV file
        fieldnames = ['filename', 'public_id', 'secure_url', 'width', 'height', 'format', 'bytes', 'created_at']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(csv_data)
        
        temp_file.close()
        
        return temp_file.name
