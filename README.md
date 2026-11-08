# Danish Schools Map

An interactive web application that displays Danish schools on a map with filtering capabilities.

https://danish-schools-overview.netlify.app

## Features
- Interactive map showing all schools in Denmark
- Filter schools by institution type and kommune
- Detailed information for each school
- Clustering of markers for better performance
- Responsive design

This is a static site. There is no backend: `schools.csv` is converted into JSON files at build time, and the browser reads those files.

## Build the data

```bash
python3 scripts/build_data.py
```

This reads `schools.csv` (UTF-16LE, semicolon separated) and writes `data/schools.json`, `data/inst_types.json`, and `data/kommune_list.json`. The generated files are committed, so a rebuild only matters when `schools.csv` changes.

## Run locally

```bash
# Python
python3 -m http.server 8000
# or Node
npx serve .
```

Open `http://localhost:8000`.

## Deploy

Upload `index.html`, `static/`, and `data/` to any static host (Netlify, GitHub Pages, S3/CloudFront).

## Tests

```bash
python3 -m pytest scripts
```

## Prerequisites

- Python 3.8+ (only for regenerating `data/` and running the tests)
- Node 18+ (optional, only for `npx serve`)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
