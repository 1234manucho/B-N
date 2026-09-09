# B&N Immo-Invest Limited — Flask Website

A responsive corporate website and enquiry-management application for B&N Immo-Invest Limited. The content has been rebuilt from the supplied construction profile and expanded to include transport and project logistics for purchased materials and commodities.

## Included

- Multi-page Flask website: Home, About, Services, service detail pages, Capabilities, Partners and Contact
- Custom B&N logo system: full dark logo, light logo, compact mark and favicon
- Responsive navigation, subtle motion and mobile-first layouts
- Tailwind CSS CDN configuration, custom inline critical CSS, static CSS and inline/static JavaScript
- Enquiry form with validation, CSRF protection and SQLite/PostgreSQL storage
- Secure administrator login and enquiry dashboard with status filters
- Custom 403, 404 and 500 pages
- Sitemap, robots.txt and health-check endpoint
- Render/Gunicorn deployment configuration

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Open `http://127.0.0.1:5000/` for the website and `http://127.0.0.1:5000/login` for the administration area.

The development administrator values are in `.env`. Change `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` and the provisional company email before production deployment. The phone numbers and address are carried over from the supplied company profile.

## Production

The project includes `render.yaml`, `Procfile`, `runtime.txt` and PostgreSQL support. In production, configure environment variables in the host rather than committing `.env`.

Start command:

```bash
gunicorn app:app
```

Run `flask --app app init-db` once after connecting the production database to create the administrator account.

## Project structure

```text
bn_immo_invest/
├── app.py
├── config.py
├── extensions.py
├── forms.py
├── models.py
├── templates/
│   ├── admin/
│   └── errors/
├── static/
│   ├── css/
│   ├── images/
│   └── js/
├── tests/
├── .env
├── requirements.txt
└── render.yaml
```

