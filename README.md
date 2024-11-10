# Danish Schools Map

An interactive web application that displays Norwegian schools on a map with filtering capabilities.

## Features
- Interactive map showing all schools in Denmark
- Filter schools by institution type and kommune
- Detailed information for each school
- Clustering of markers for better performance
- Responsive design

## Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose (optional)
- PostgreSQL database

## Installation

### Using Docker (Recommended)
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

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
