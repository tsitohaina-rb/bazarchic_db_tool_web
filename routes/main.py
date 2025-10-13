"""
Main Routes Blueprint
Dashboard and home page
"""

from flask import Blueprint, render_template
from services.database_service import BazarchicDB

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page with dashboard statistics"""
    try:
        db = BazarchicDB()
        cursor = db.connection.cursor(dictionary=True)
        
        # Total products count
        cursor.execute("SELECT COUNT(*) as total FROM produits_view3 WHERE status = 'on'")
        total_products = cursor.fetchone()['total']
        
        # Products with EAN
        cursor.execute("""
            SELECT COUNT(*) as total FROM produits_view3 
            WHERE ean IS NOT NULL AND ean != '' AND status = 'on'
        """)
        products_with_ean = cursor.fetchone()['total']
        
        # Products with images
        cursor.execute("""
            SELECT COUNT(DISTINCT p.idproduit_group) as total 
            FROM produits_view3 p
            JOIN produits_gallery g ON p.idproduit_group = g.idproduit_group
            WHERE p.status = 'on' AND g.status = 'on'
        """)
        products_with_images = cursor.fetchone()['total']
        
        # Count database tables
        cursor.execute("SHOW TABLES")
        total_tables = len(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        stats = {
            'total_products': total_products,
            'products_with_ean': products_with_ean,
            'ean_products': products_with_ean,  # Alias for template compatibility
            'products_with_images': products_with_images,
            'total_tables': total_tables,
            'ean_percentage': round((products_with_ean / total_products * 100), 1) if total_products > 0 else 0,
            'images_percentage': round((products_with_images / total_products * 100), 1) if total_products > 0 else 0
        }
        
        return render_template('index.html', stats=stats)
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return render_template('index.html', stats=None, error=str(e))
