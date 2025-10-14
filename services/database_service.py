"""
Bazarchic Database Connection and Operations
"""

import mysql.connector
from dotenv import load_dotenv
import os
import tempfile
from datetime import datetime
import re
from html import unescape

# Load environment variables
load_dotenv()

def clean_html(text):
    """Remove HTML tags and decode HTML entities from text"""
    if not text or text.strip() == '':
        return ''
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', str(text))
    
    # Decode HTML entities (like &amp;, &lt;, &gt;, etc.)
    clean_text = unescape(clean_text)
    
    # Clean up extra whitespace
    clean_text = ' '.join(clean_text.split())
    
    return clean_text.strip()

class BazarchicDB:
    """Bazarchic Database Connection and Operations"""
    
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
            
            if self.connection.is_connected():
                print(f"✅ Connected to database: {os.getenv('DB_NAME')}")
                return True
        except mysql.connector.Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Database connection closed")
    
    def get_capacity_from_product(self, product_data):
        """Extract capacity from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND (dk.valeur LIKE '%capacité%' OR dk.valeur LIKE '%capacity%' OR 
                   dk.valeur LIKE '%volume%' OR dk.valeur LIKE '%contenance%')
              AND dv.valeur IS NOT NULL AND dv.valeur != ''
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (product_group_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0].strip() if result and result[0] else ""
        except:
            return ""

    def get_dlc_from_product(self, product_data):
        """Extract DLC from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND dk.valeur LIKE '%DLC%'
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (product_group_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0].strip() if result and result[0] else ""
        except:
            return ""

    def get_weight_from_product(self, product_data):
        """Extract Weight from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND dk.valeur LIKE '%Poids%'
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (product_group_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0].strip() if result and result[0] else ""
        except:
            return ""
    
    def get_dimensions_from_product(self, product_data):
        """Extract Dimensions from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND dk.valeur LIKE '%Dimensions%'
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (product_group_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0].strip() if result and result[0] else ""
        except:
            return ""

    def get_motif_from_product(self, product_data):
        """Extract Motif from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND dk.valeur LIKE '%Motif%'
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (product_group_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0].strip() if result and result[0] else ""
        except:
            return ""
    
    def get_ddm_from_product(self, product_data):
        """Extract DDM from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND (dk.valeur LIKE '%DDM%' OR dk.valeur LIKE '%durabilité%')
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (product_group_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0].strip() if result and result[0] else ""
        except:
            return ""

    def get_ingredients_from_product(self, product_data):
        """Extract ingredients from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id or product_group_id == 0:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND (dk.valeur = 'Ingrédients' OR dk.valeur = 'Ingredients' 
                   OR dk.valeur LIKE '%ngrédient%' OR dk.valeur LIKE '%ngredient%')
              AND dv.valeur IS NOT NULL AND LENGTH(dv.valeur) > 20
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (int(product_group_id),))
            result = cursor.fetchone()
            cursor.close()
            if result and result[0]:
                text = result[0].strip().replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                return text[:1000] + "..." if len(text) > 1000 else text
            return ""
        except:
            return ""

    def get_color_from_product(self, product_data):
        """Extract color from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id or product_group_id == 0:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND (dk.valeur = 'Couleurs' OR dk.valeur = 'Couleur')
              AND dv.valeur IS NOT NULL AND LENGTH(dv.valeur) > 20
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (int(product_group_id),))
            result = cursor.fetchone()
            cursor.close()
            if result and result[0]:
                text = result[0].strip().replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                return text[:500] + "..." if len(text) > 500 else text
            return ""
        except:
            return ""

    def get_care_advice_from_product(self, product_data):
        """Extract care advice from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id or product_group_id == 0:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND dk.valeur = 'Conseil d''entretien'
              AND dv.valeur IS NOT NULL AND LENGTH(dv.valeur) > 10
            ORDER BY pgc.position LIMIT 1
            """
            cursor.execute(query, (int(product_group_id),))
            result = cursor.fetchone()
            cursor.close()
            if result and result[0]:
                text = result[0].strip().replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                return text[:500] + "..." if len(text) > 500 else text
            return ""
        except:
            return ""
    
    def get_composition_from_product(self, product_data, composition_number=1):
        """Extract composition fields from product data"""
        try:
            product_group_id = product_data.get('product_group_id')
            if not product_group_id:
                return ""
            cursor = self.connection.cursor()
            query = """
            SELECT dv.valeur FROM produits_group_caracteristiques pgc
            JOIN caracteristiques c ON pgc.idcaracteristique = c.idcaracteristique
            JOIN dictionnaires_langues dk ON c.iddictionnaire_cle = dk.iddictionnaire
            JOIN dictionnaires_langues dv ON c.iddictionnaire_valeur = dv.iddictionnaire
            WHERE pgc.idproduit_group = %s AND pgc.status = 'on' AND c.status = 'on'
              AND dk.valeur LIKE '%Composition%'
              AND dv.valeur IS NOT NULL AND LENGTH(dv.valeur) > 5
            ORDER BY pgc.position LIMIT 3
            """
            cursor.execute(query, (product_group_id,))
            results = cursor.fetchall()
            cursor.close()
            if results and len(results) >= composition_number:
                text = results[composition_number - 1][0].strip().replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
                return text[:200] + "..." if len(text) > 200 else text
            return ""
        except:
            return ""

    def export_comprehensive_csv(self, limit=None, ean_filter=None, ref_filter=None):
        """Export products with comprehensive data
        Creates separate CSV files for found and not found codes when searching by EAN or REF
        """
        try:
            import csv
            
            base_query = """
            SELECT 
                '' as 'Catégorie', p.ref as 'Shop sku',
                CASE 
                    WHEN p.nom_fr != '' AND p.nom_fr IS NOT NULL THEN p.nom_fr
                    WHEN p.keywords != '' AND p.keywords IS NOT NULL THEN p.keywords
                    ELSE CONCAT('Produit ', p.idproduit)
                END as 'Titre du produit',
                COALESCE(p.marque_fr, 'Marque inconnue') as 'Marque',
                COALESCE(p.description_fr, '') as 'Description Longue',
                COALESCE(p.ean, '') as 'EAN',
                '' as 'Couleur commercial',
                CASE WHEN g1.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g1.idimage, '.', g1.ext) ELSE '' END as 'Image principale',
                CASE WHEN g2.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g2.idimage, '.', g2.ext) ELSE '' END as 'image secondaire',
                CASE WHEN g3.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g3.idimage, '.', g3.ext) ELSE '' END as 'Image 3',
                CASE WHEN g4.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g4.idimage, '.', g4.ext) ELSE '' END as 'Image 4',
                CASE WHEN g5.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g5.idimage, '.', g5.ext) ELSE '' END as 'Image 5',
                CASE WHEN g6.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g6.idimage, '.', g6.ext) ELSE '' END as 'Image 6',
                CASE WHEN g7.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g7.idimage, '.', g7.ext) ELSE '' END as 'Image 7',
                CASE WHEN g8.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g8.idimage, '.', g8.ext) ELSE '' END as 'Image 8',
                CASE WHEN g9.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g9.idimage, '.', g9.ext) ELSE '' END as 'Image 9',
                CASE WHEN g10.idimage IS NOT NULL THEN CONCAT('https://cdn.bazarchic.com/i/tmp/', g10.idimage, '.', g10.ext) ELSE '' END as 'Image_10',
                CASE WHEN p.idproduit_group > 0 THEN 'Oui' ELSE 'Non' END as 'Produit Parent (identification)',
                '' as 'Id de rattachement',
                '' as 'Composition 1', '' as 'Composition 2', '' as 'Composition 3',
                '' as 'Conseil d\'entretien', '' as 'Capacité', '' as 'Dimensions',
                '' as 'DLC (Date limite de consommation)', '' as 'DDM (Date de durabilité minimale)',
                p.idproduit_group as 'product_group_id', '' as 'Ingrédients',
                CASE WHEN p.poids > 0 THEN CONCAT(p.poids) ELSE '' END as 'Poids net du produit',
                '' as 'Motif', '' as 'Garantie commerciale', 'Non' as 'Eco-responsable',
                'Non' as 'Métrage ? (oui /non)',
                CASE WHEN p.virtuel = 'oui' THEN 'Service' ELSE 'Produit' END as 'Produit ou Service',
                '' as 'BZC ( à ne pas remplir )', COALESCE(p.poids, 0) as 'Poids du colis (kg)',
                CASE
                    WHEN p.cols IN ('T.U.', 'T.U') THEN 'Taille Unique'
                    WHEN p.cols LIKE 'T.%' THEN SUBSTRING(p.cols, 3) 
                    WHEN p.cols IS NULL OR p.cols = '' THEN ''   
                    ELSE p.cols
                END AS `Taille unique`
            FROM produits_view3 p
            LEFT JOIN produits_gallery g1 ON p.idproduit_group = g1.idproduit_group AND g1.position = 0 AND g1.status = 'on'
            LEFT JOIN produits_gallery g2 ON p.idproduit_group = g2.idproduit_group AND g2.position = 1 AND g2.status = 'on'
            LEFT JOIN produits_gallery g3 ON p.idproduit_group = g3.idproduit_group AND g3.position = 2 AND g3.status = 'on'
            LEFT JOIN produits_gallery g4 ON p.idproduit_group = g4.idproduit_group AND g4.position = 3 AND g4.status = 'on'
            LEFT JOIN produits_gallery g5 ON p.idproduit_group = g5.idproduit_group AND g5.position = 4 AND g5.status = 'on'
            LEFT JOIN produits_gallery g6 ON p.idproduit_group = g6.idproduit_group AND g6.position = 5 AND g6.status = 'on'
            LEFT JOIN produits_gallery g7 ON p.idproduit_group = g7.idproduit_group AND g7.position = 6 AND g7.status = 'on'
            LEFT JOIN produits_gallery g8 ON p.idproduit_group = g8.idproduit_group AND g8.position = 7 AND g8.status = 'on'
            LEFT JOIN produits_gallery g9 ON p.idproduit_group = g9.idproduit_group AND g9.position = 8 AND g9.status = 'on'
            LEFT JOIN produits_gallery g10 ON p.idproduit_group = g10.idproduit_group AND g10.position = 9 AND g10.status = 'on'
            WHERE p.status = 'on'
            """
            
            clean_codes = []
            search_type = 'products'
            
            if ean_filter:
                if isinstance(ean_filter, str):
                    ean_filter = [ean_filter]
                clean_codes = [str(ean).strip() for ean in ean_filter if str(ean).strip()]
                if clean_codes:
                    ean_placeholders = ', '.join(['%s'] * len(clean_codes))
                    base_query += f" AND p.ean IN ({ean_placeholders})"
                    search_type = 'EAN'
            
            elif ref_filter:
                if isinstance(ref_filter, str):
                    ref_filter = [ref_filter]
                clean_codes = [str(ref).strip() for ref in ref_filter if str(ref).strip()]
                if clean_codes:
                    ref_conditions = " OR ".join(["p.ref LIKE %s" for _ in clean_codes])
                    base_query += f" AND ({ref_conditions})"
                    search_type = 'REF'
            
            if limit:
                base_query += f" LIMIT {limit}"
            
            print(f"\n�� Starting comprehensive CSV export...")
            print("=" * 60)
            if clean_codes:
                print(f"🔍 Searching {len(clean_codes)} {search_type} code(s)...")
            
            cursor = self.connection.cursor(dictionary=True)
            
            if clean_codes:
                if ref_filter:
                    like_params = [f"%{ref}%" for ref in clean_codes]
                    cursor.execute(base_query, like_params)
                else:
                    cursor.execute(base_query, clean_codes)
            else:
                cursor.execute(base_query)
            
            products = cursor.fetchall()
            total_exported = len(products)
            cursor.close()
            
            display_headers = [
                'Category', 'Shop sku', 'Titre du produit', 'Marque', 'Description Longue',
                'EAN', 'Couleur commercial', 'Image principale', 'image secondaire',
                'Image 3', 'Image 4', 'Image 5', 'Image 6', 'Image 7', 'Image 8',
                'Image 9', 'Image_10', 'Produit Parent (identification)', 'Id de rattachement',
                'Composition 1', 'Composition 2', 'Composition 3', 'Conseil d\'entretien',
                'Capacité', 'Dimensions', 'DLC (Date limite de consommation)',
                'DDM (Date de durabilité minimale)', 'Ingrédients', 'Poids net du produit',
                'Motif', 'Garantie commerciale', 'Eco-responsable', 'Métrage ? (oui /non)',
                'Produit ou Service', 'BZC ( à ne pas remplir )', 'Poids du colis (kg)', 'Taille unique'
            ]
            
            technical_mappings = [
                'family_id', 'shop_sku', 'name', 'brand_id', 'description',
                'ean', 'technical_spec_1_color', 'media_1', 'media_2',
                'media_3', 'media_4', 'media_5', 'media_6', 'media_7', 'media_8',
                'media_9', 'media_10', 'is_parent', 'variant_group_code',
                'technical_spec_1_composition', 'technical_spec_2_composition', 'technical_spec_3_composition', 'technical_spec_1_care_advice',
                'technical_spec_1_capacity', 'technical_spec_1_dimensions', 'technical_spec_1_expiration_date',
                'technical_spec_1_durability_date', 'technical_spec_1_ingredients', 'technical_spec_1_net_weight',
                'technical_spec_1_pattern', 'technical_spec_1_commercial_warranty', 'technical_spec_1_eco_responsibility', 'is_cloth',
                'is_virtual', 'is_bzc', 'weight', 'size_id'
            ]
            
            def write_product_row(prod, writer):
                desc_cleaned = clean_html(prod.get('Description Longue', ''))
                capacity = self.get_capacity_from_product(prod)
                dimensions = self.get_dimensions_from_product(prod)
                weight = self.get_weight_from_product(prod)
                color = self.get_color_from_product(prod)
                motif = self.get_motif_from_product(prod)
                dlc = self.get_dlc_from_product(prod)
                ddm = self.get_ddm_from_product(prod)
                ingredients = self.get_ingredients_from_product(prod)
                care_advice = self.get_care_advice_from_product(prod)
                composition1 = self.get_composition_from_product(prod, 1)
                composition2 = self.get_composition_from_product(prod, 2)
                composition3 = self.get_composition_from_product(prod, 3)
                size = prod.get('Taille unique', 'Taille Unique')
                
                data_row = [
                    prod.get('Catégorie', ''), prod.get('Shop sku', ''), prod.get('Titre du produit', ''), 
                    prod.get('Marque', ''), desc_cleaned, prod.get('EAN', ''), 
                    color, prod.get('Image principale', ''), 
                    prod.get('image secondaire', ''), prod.get('Image 3', ''), prod.get('Image 4', ''), 
                    prod.get('Image 5', ''), prod.get('Image 6', ''), prod.get('Image 7', ''), 
                    prod.get('Image 8', ''), prod.get('Image 9', ''), prod.get('Image_10', ''), 
                    prod.get('Produit Parent (identification)', ''), prod.get('Id de rattachement', ''),
                    composition1, composition2, composition3,
                    care_advice, capacity, dimensions,
                    dlc, ddm,
                    ingredients, weight, motif,
                    prod.get('Garantie commerciale', ''), prod.get('Eco-responsable', ''), prod.get('Métrage ? (oui /non)', ''),
                    prod.get('Produit ou Service', ''), prod.get('BZC ( à ne pas remplir )', ''), 
                    prod.get('Poids du colis (kg)', ''), size
                ]
                writer.writerow(data_row)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if (ean_filter or ref_filter) and clean_codes:
                # Use temporary directory for online app
                export_dir = tempfile.mkdtemp(prefix=f'export_{timestamp}_')
                
                filename_all = os.path.join(export_dir, f"ALL_products.csv")
                filename_found = os.path.join(export_dir, f"FOUND_products.csv")
                filename_not_found = os.path.join(export_dir, f"NOT_FOUND_products.csv")
                
                found_by_code = {}
                search_field = 'EAN' if ean_filter else 'Shop sku'
                
                print(f"�� Organizing results by {search_type}...")
                
                for prod in products:
                    code_key = prod.get(search_field, '')
                    if ref_filter:
                        for input_code in clean_codes:
                            if input_code.lower() in code_key.lower() or code_key.lower() in input_code.lower():
                                if input_code not in found_by_code:
                                    found_by_code[input_code] = []
                                found_by_code[input_code].append(prod)
                    else:
                        if code_key not in found_by_code:
                            found_by_code[code_key] = []
                        found_by_code[code_key].append(prod)
                
                found_codes = []
                not_found_codes = []
                
                print(f"📝 Writing CSV files...")
                
                with open(filename_all, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(display_headers)
                    writer.writerow(technical_mappings)
                    for code in clean_codes:
                        if code in found_by_code:
                            for prod in found_by_code[code]:
                                write_product_row(prod, writer)
                        else:
                            empty_row = ['' for _ in display_headers]
                            empty_row[0] = ''
                            if ean_filter:
                                empty_row[display_headers.index('EAN')] = code
                            else:
                                empty_row[display_headers.index('Shop sku')] = code
                            writer.writerow(empty_row)
                
                with open(filename_found, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(display_headers)
                    writer.writerow(technical_mappings)
                    for code in clean_codes:
                        if code in found_by_code:
                            found_codes.append(code)
                            for prod in found_by_code[code]:
                                write_product_row(prod, writer)
                
                with open(filename_not_found, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(display_headers)
                    writer.writerow(technical_mappings)
                    for code in clean_codes:
                        if code not in found_by_code:
                            not_found_codes.append(code)
                            empty_row = ['' for _ in display_headers]
                            empty_row[0] = ''
                            if ean_filter:
                                empty_row[display_headers.index('EAN')] = code
                            else:
                                empty_row[display_headers.index('Shop sku')] = code
                            writer.writerow(empty_row)
                
                file_size_all = os.path.getsize(filename_all) / 1024 / 1024
                file_size_found = os.path.getsize(filename_found) / 1024 / 1024
                file_size_not_found = os.path.getsize(filename_not_found) / 1024 / 1024
                
                print(f"\n✅ Comprehensive CSV export completed!")
                print("=" * 60)
                print(f"📁 Export Directory: {export_dir}")
                print()
                print(f"📄 ALL Products File: ALL_products.csv")
                print(f"   💾 File size: {file_size_all:.2f} MB")
                print()
                print(f"📄 FOUND Products File: FOUND_products.csv")
                print(f"   📊 {search_type}s found: {len(found_codes)}")
                print(f"   📊 Products exported: {total_exported:,}")
                print(f"   💾 File size: {file_size_found:.2f} MB")
                print()
                print(f"📄 NOT FOUND Products File: NOT_FOUND_products.csv")
                print(f"   📊 {search_type}s not found: {len(not_found_codes)}")
                print(f"   💾 File size: {file_size_not_found:.2f} MB")
                print()
                print(f"📋 Summary:")
                print(f"   Total {search_type}s searched: {len(clean_codes)}")
                print(f"   Found: {len(found_codes)} ({len(found_codes)/len(clean_codes)*100:.1f}%)")
                print(f"   Not Found: {len(not_found_codes)} ({len(not_found_codes)/len(clean_codes)*100:.1f}%)")
                
                return export_dir, (len(found_codes), len(not_found_codes), total_exported)
            
            else:
                filename = f"comprehensive_products_{timestamp}.csv"
                with open(filename, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(display_headers)
                    writer.writerow(technical_mappings)
                    if products:
                        for prod in products:
                            write_product_row(prod, writer)
                
                file_size = os.path.getsize(filename) / 1024 / 1024
                print(f"\n✅ Comprehensive CSV export completed!")
                print(f"📁 File: {filename}")
                print(f"📊 Products exported: {total_exported:,}")
                print(f"💾 File size: {file_size:.2f} MB")
                return filename, total_exported
                
        except Exception as e:
            print(f"❌ Export error: {e}")
            return None, 0
