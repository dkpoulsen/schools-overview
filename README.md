# Danish Schools Map

An interactive web application that displays Danish schools on a map with filtering capabilities.

## Features
- Interactive map showing all schools in Denmark
- Filter schools by institution type and kommune
- Detailed information for each school
- Clustering of markers for better performance
- Responsive design

## Prerequisites
- For static site: Python 3.8+ (to build JSON) and any static host
- Legacy backend (optional): Docker/Compose and PostgreSQL

## Static Hosting (Recommended)

You can host this as a purely static site (no backend).

1. Build JSON data from `schools.csv`:
   ```bash
   python3 scripts/build_data.py
   ```
   This writes `data/schools.json`, `data/inst_types.json`, and `data/kommune_list.json`.

2. Serve the site with any static server (examples):
   ```bash
   # Python
   python3 -m http.server 8000
   # or Node
   npx serve . --cors --single
   ```

3. Open `http://localhost:8000` and use `index.html`.

4. Deploy to any static host (GitHub Pages, Netlify, S3/CloudFront). Ensure `index.html`, `static/`, and `data/` are deployed.

### GitHub Pages quick start
- Push `index.html`, `static/`, and `data/` to the repository
- Enable Pages in repo settings (deploy from root or `/docs` if you relocate files)

## Legacy Backend (Optional)

### Using Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/dkpoulsen/schools-overview.git
   cd schools-overview
   ```

2. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the application at `http://localhost:5000`

### Manual Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/dkpoulsen/schools-overview.git
   cd schools-overview
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database and update connection settings in `school_data_mapper.py`

5. Run the application:
   ```bash
   python api.py
   ```

6. Access the application at `http://localhost:5000`

Note: The backend is no longer required for typical usage and is kept for reference only.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
