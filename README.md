# Bazarchic Database Tool

A professional Flask web application for managing and querying the Bazarchic product database with integrated Cloudinary and Dropbox support.

## Features

- 🔍 **Product Search**: Search by EAN or REF codes with export functionality
- 🖼️ **Image URL Extraction**: Extract product image URLs with bulk processing
- ☁️ **Cloudinary Integration**: Upload images from local server or Dropbox to Cloudinary
- 📊 **CSV Export**: Comprehensive data export with multiple formats
- 📱 **Responsive Design**: Modern UI with Tailwind CSS

## Deployment on Render

### Prerequisites

1. A Render account (free tier available)
2. Database credentials for the Bazarchic database
3. Cloudinary account credentials
4. Dropbox API token (optional)

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
# Clone or upload your code to a Git repository (GitHub, GitLab, etc.)
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repository-url
git push -u origin main
```

#### 2. Deploy on Render

1. **Go to Render Dashboard**: Visit [render.com](https://render.com) and log in
2. **Create New Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Connect your Git repository
4. **Configure Service**:
   - **Name**: `bazarchic-db-tool`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or paid for better performance)

#### 3. Set Environment Variables

In your Render service settings, add these environment variables:

```env
# Database Configuration
DB_HOST=
DB_USER=
DB_PASSWORD=your_database_password
DB_NAME=
DB_PORT=3306

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Dropbox Configuration (Optional)
DROPBOX_TOKEN=your_dropbox_token

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
PYTHON_VERSION=3.11.0
```

#### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Your app will be available at: `https://your-service-name.onrender.com`

### Alternative: One-Click Deploy

If you have the `render.yaml` file in your repository, you can use Render's one-click deploy:

1. Go to your Render dashboard
2. Click "New" → "Blueprint"
3. Connect your repository
4. Render will automatically detect the `render.yaml` configuration

## Local Development

### Prerequisites

- Python 3.8+
- Virtual environment

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run application
python app.py
```

**Access:** http://localhost:5000

---

## Features

### 1. Dashboard (`/`)

- Real-time database statistics
- Product counts and metrics
- Quick navigation

### 2. Product Search (`/search`)

- Search by EAN (exact match)
- Search by REF (pattern match)
- Export to CSV (3 files: ALL, FOUND, NOT FOUND)
- Download as ZIP

### 3. Image URL Extraction (`/images/extractor`)

- Extract image URLs from products
- Up to 10 images per product
- Export to CSV
- Lightweight and fast

### 4. Cloudinary Local Upload (`/cloudinary/local`)

- Upload images from local server to Cloudinary
- Multi-threaded processing (1-20 threads)
- Progress tracking
- Export results to CSV

### 5. Cloudinary Dropbox Upload (`/cloudinary/dropbox`)

- List Dropbox folders
- Upload directly from Dropbox to Cloudinary
- No local download required
- Multi-threaded processing
- Export results to CSV

---

## Project Structure

```
app/
├── app.py                      # Main application
├── config.py                   # Cloudinary configuration
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
│
├── services/                   # Business logic
│   ├── database_service.py     # Database operations
│   ├── image_service.py        # Image extraction
│   └── cloudinary_service.py   # Cloudinary uploads
│
├── routes/                     # Route handlers
│   ├── main.py                 # Dashboard routes
│   ├── search.py               # Search routes
│   ├── images.py               # Image extraction routes
│   └── cloudinary.py           # Cloudinary routes
│
└── templates/                  # HTML templates
    ├── base.html
    ├── index.html
    ├── search.html
    ├── images_extractor.html
    ├── cloudinary_local.html
    └── cloudinary_dropbox.html
```

---

## Configuration

### Environment Variables (.env)

```env
# Database
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=bazarchic
DB_PORT=3306

# Flask
SECRET_KEY=your-secret-key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Dropbox
DROPBOX_TOKEN=your_dropbox_token
```

---

## Usage Examples

### Search Products by EAN

1. Go to `/search`
2. Select "EAN" method
3. Choose input type:
   - **Single:** Enter one EAN
   - **Multiple:** Enter multiple EANs (comma-separated)
   - **File:** Upload CSV with EANs
4. Click "Search and Export"
5. Download ZIP with 3 CSV files

### Extract Image URLs

1. Go to `/images/extractor`
2. Select "EAN" or "REF"
3. Enter codes or upload file
4. Click "Extract Images"
5. Download ZIP with CSV

### Upload to Cloudinary (Local)

1. Go to `/cloudinary/local`
2. Enter local folder path (e.g., `/path/to/images`)
3. Set number of threads (recommended: 10-15)
4. Click "Upload to Cloudinary"
5. Wait for completion
6. Download results CSV

### Upload to Cloudinary (Dropbox)

1. Go to `/cloudinary/dropbox`
2. (Optional) Click "List Folders" to see available folders
3. Enter Dropbox folder path (e.g., `/My Images/Products`)
4. Set number of threads (recommended: 10-15)
5. Click "Upload to Cloudinary"
6. Wait for completion
7. Download results CSV

---

## Development

### Run in Development Mode

```bash
export FLASK_DEBUG=1
python app.py
```

### Project Architecture

This application follows Flask best practices:

- **Service Layer Pattern:** Business logic separated from routes
- **Flask Blueprints:** Routes organized by feature
- **Repository Pattern:** Database operations abstracted

**Services:**

- `database_service.py` - All database queries
- `image_service.py` - Image URL extraction logic
- `cloudinary_service.py` - Cloudinary upload operations

**Routes:**

- `main.py` - Dashboard
- `search.py` - Product search
- `images.py` - Image extraction
- `cloudinary.py` - Cloudinary uploads

---

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with more options
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 --access-logfile - app:app
```

### Using systemd

Create `/etc/systemd/system/bazarchic.service`:

```ini
[Unit]
Description=Bazarchic DB Tool
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/app/.venv/bin"
ExecStart=/path/to/app/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bazarchic
sudo systemctl start bazarchic
```

---

## Troubleshooting

### Database Connection Failed

**Error:** `Database connection failed`

**Solutions:**

1. Check `.env` credentials
2. Verify MySQL is running: `sudo systemctl status mysql`
3. Test connection: `mysql -u user -p -h host database_name`

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'services'`

**Solutions:**

1. Ensure you're in the correct directory: `cd /path/to/app`
2. Activate virtual environment: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

### Template Not Found

**Error:** `jinja2.exceptions.TemplateNotFound`

**Solutions:**

1. Verify templates folder exists: `ls -la templates/`
2. Check Flask template folder configuration in `app.py`

### Cloudinary Upload Failed

**Error:** Upload fails or times out

**Solutions:**

1. Check Cloudinary credentials in `.env`
2. Verify internet connection
3. Reduce number of threads
4. Check image file formats (JPG, PNG supported)

---

## API Routes

| Route                        | Method | Description            |
| ---------------------------- | ------ | ---------------------- |
| `/`                          | GET    | Dashboard              |
| `/search`                    | GET    | Search page            |
| `/search/export`             | POST   | Export products to CSV |
| `/images/extractor`          | GET    | Image extractor page   |
| `/images/extractor/export`   | POST   | Export image URLs      |
| `/cloudinary/local`          | GET    | Local upload page      |
| `/cloudinary/local/upload`   | POST   | Upload from local      |
| `/cloudinary/dropbox`        | GET    | Dropbox upload page    |
| `/cloudinary/dropbox/list`   | GET    | List Dropbox folders   |
| `/cloudinary/dropbox/upload` | POST   | Upload from Dropbox    |

---

## Requirements

- Python 3.8+
- MySQL 8.0+
- Flask 3.0.0
- Cloudinary account
- Dropbox account (for Dropbox features)

**Key Dependencies:**

```
Flask==3.0.0
mysql-connector-python==8.2.0
cloudinary==1.36.0
dropbox==11.36.2
python-dotenv==1.0.0
```

See `requirements.txt` for complete list.

---

## Security Notes

- **Never commit `.env` file** to version control
- Use strong `SECRET_KEY` in production
- Keep dependencies updated: `pip install --upgrade -r requirements.txt`
- Use HTTPS in production
- Implement rate limiting for production use

---

## Support

**Common Commands:**

```bash
# Test structure
python -c "from services.database_service import BazarchicDB; print('✓ OK')"

# Check database connection
python -c "from services.database_service import BazarchicDB; db = BazarchicDB()"

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

**Backup:**

```bash
# Backup database
mysqldump -u user -p bazarchic > backup.sql

# Backup application
tar -czf app_backup_$(date +%Y%m%d).tar.gz .
```

---

## License

© 2025 Bazarchic. All rights reserved.

---

**Version:** 2.0  
**Last Updated:** October 13, 2025
