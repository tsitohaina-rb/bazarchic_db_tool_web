"""
Image Extraction Service
Extract product image URLs by EAN or REF codes
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class ImageExtractorService:
    """Service for extracting product image URLs by EAN or REF"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                port=int(os.getenv('DB_PORT', 3306))
            )
            return self.connection.is_connected()
        except mysql.connector.Error as e:
            print(f"Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_images_by_ean(self, ean_codes: List[str]) -> Dict:
        """
        Get all product images for given EAN codes
        Returns dict with EAN as key and image data as value
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if isinstance(ean_codes, str):
                ean_codes = [ean_codes]
            
            clean_eans = [str(ean).strip() for ean in ean_codes if str(ean).strip()]
            
            if not clean_eans:
                return {}
            
            # Query with LEFT JOINs for all 10 image positions
            query = self._build_image_query('ean', len(clean_eans))
            cursor.execute(query, clean_eans)
            results = cursor.fetchall()
            cursor.close()
            
            # Group by EAN
            images_by_ean = {}
            for row in results:
                ean = row['ean']
                if ean not in images_by_ean:
                    images_by_ean[ean] = row
            
            return images_by_ean
            
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            return {}
    
    def get_images_by_ref(self, ref_codes: List[str]) -> List[Dict]:
        """
        Get all product images for given REF codes
        Returns list of dicts (one REF can have multiple products)
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if isinstance(ref_codes, str):
                ref_codes = [ref_codes]
            
            clean_refs = [str(ref).strip() for ref in ref_codes if str(ref).strip()]
            
            if not clean_refs:
                return []
            
            # Query with LEFT JOINs for all 10 image positions
            query = self._build_image_query('ref', len(clean_refs))
            cursor.execute(query, clean_refs)
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            return []
    
    def _build_image_query(self, search_type: str, count: int) -> str:
        """Build SQL query for image extraction"""
        
        # Build image CASE statements for positions 0-9
        image_cases = []
        for i in range(10):
            image_cases.append(f"""
                CASE 
                    WHEN g{i+1}.idimage IS NOT NULL 
                    THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g{i+1}.idimage, '.', g{i+1}.ext)
                    ELSE ''
                END as image_{i+1}
            """)
        
        # Build LEFT JOIN statements
        joins = []
        for i in range(10):
            joins.append(f"""
                LEFT JOIN produits_gallery g{i+1} 
                ON p.idproduit_group = g{i+1}.idproduit_group 
                AND g{i+1}.position = {i} 
                AND g{i+1}.status = 'on'
            """)
        
        # Select fields based on search type
        if search_type == 'ean':
            select_fields = "p.ean, p.idproduit_group"
            where_clause = f"WHERE p.ean IN ({','.join(['%s'] * count)})"
            order_by = "ORDER BY p.ean"
        else:  # ref
            select_fields = "p.ref, p.ean, p.idproduit_group"
            where_clause = f"WHERE p.ref IN ({','.join(['%s'] * count)})"
            order_by = "ORDER BY p.ref, p.ean"
        
        query = f"""
            SELECT 
                {select_fields},
                {','.join(image_cases)}
            FROM produits_view3 p
            {' '.join(joins)}
            {where_clause}
            AND p.status = 'on'
            {order_by}
        """
        
        return query
    
    def export_to_csv(self, codes: List[str], search_type: str = 'ean', 
                      filename: Optional[str] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Export product images to CSV files
        Returns tuple of (file_all, file_found, file_not_found)
        """
        try:
            clean_codes = [str(code).strip() for code in codes if str(code).strip()]
            
            if not clean_codes:
                print(f"No valid {search_type.upper()} codes provided")
                return None, None, None
            
            # Get images data
            if search_type == 'ean':
                images_data = self.get_images_by_ean(clean_codes)
                images_list = list(images_data.values())
            else:
                images_list = self.get_images_by_ref(clean_codes)
                images_data = {row['ref']: row for row in images_list}
            
            # Generate filenames
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = filename.replace('.csv', '') if filename else f"images_by_{search_type}"
            file_all = f"{base_name}_ALL_{timestamp}.csv"
            file_found = f"{base_name}_FOUND_{timestamp}.csv"
            file_not_found = f"{base_name}_NOT_FOUND_{timestamp}.csv"
            
            # Headers
            if search_type == 'ean':
                headers = ['ean'] + [f'image_{i}' for i in range(1, 11)]
            else:
                headers = ['ref', 'ean'] + [f'image_{i}' for i in range(1, 11)]
            
            # Track found/not found
            if search_type == 'ean':
                found_codes = list(images_data.keys())
                not_found = [code for code in clean_codes if code not in images_data]
            else:
                found_refs = set(row['ref'] for row in images_list)
                found_codes = list(found_refs)
                not_found = [code for code in clean_codes if code not in found_refs]
            
            # Write ALL file
            self._write_csv_file(file_all, headers, clean_codes, images_data, 
                               images_list, search_type, not_found)
            
            # Write FOUND file
            self._write_csv_file(file_found, headers, found_codes, images_data, 
                               images_list, search_type, [])
            
            # Write NOT FOUND file
            with open(file_not_found, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for code in not_found:
                    if search_type == 'ean':
                        writer.writerow([code] + [''] * 10)
                    else:
                        writer.writerow([code, ''] + [''] * 10)
            
            print(f"\nExport completed: {len(found_codes)} found, {len(not_found)} not found")
            
            return file_all, file_found, file_not_found
            
        except Exception as e:
            print(f"Export error: {e}")
            return None, None, None
    
    def _write_csv_file(self, filename: str, headers: List[str], codes: List[str],
                       images_data: Dict, images_list: List[Dict], 
                       search_type: str, not_found: List[str]):
        """Helper to write CSV file"""
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            if search_type == 'ean':
                for code in codes:
                    if code in images_data:
                        row_data = images_data[code]
                        row = [code] + [row_data.get(f'image_{i}', '') for i in range(1, 11)]
                        writer.writerow(row)
                    elif code in not_found:
                        writer.writerow([code] + [''] * 10)
            else:
                # For REF, write all products
                written_refs = set()
                for code in codes:
                    if code not in not_found:
                        for row_data in images_list:
                            if row_data['ref'] == code:
                                row = [row_data['ref'], row_data['ean']] + \
                                      [row_data.get(f'image_{i}', '') for i in range(1, 11)]
                                writer.writerow(row)
                                written_refs.add(code)
                
                # Write not found refs
                for code in not_found:
                    writer.writerow([code, ''] + [''] * 10)
