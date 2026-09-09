import os
from datetime import datetime

import click
from flask import Flask, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from config import Config
from extensions import csrf, db, login_manager
from forms import EnquiryForm, LoginForm
from models import Enquiry, User


SERVICES = [
    {
        "slug": "civil-engineering",
        "number": "01",
        "icon": "building-2",
        "title": "Civil Engineering & Building Works",
        "short": "Structural delivery for residential, commercial and industrial developments.",
        "summary": "We translate architectural concepts into safe, practical structural frameworks, coordinating people, materials and site execution from the earliest works through delivery.",
        "points": [
            "Civil and structural works",
            "Commercial and residential buildings",
            "Road and site infrastructure",
            "Heavy-duty foundations and industrial flooring",
        ],
        "image": "images/civil-works.jpg",
    },
    {
        "slug": "materials-commodities",
        "number": "02",
        "icon": "package-check",
        "title": "Building Materials & Commodities",
        "short": "Quality-controlled sourcing and supply for projects of every scale.",
        "summary": "Our procurement team sources dependable construction materials and project commodities from vetted suppliers, with attention to specifications, compliance and delivery schedules.",
        "points": [
            "Reinforcement and structural steel",
            "Cement and essential building inputs",
            "Supplier verification and quality coordination",
            "Bulk orders and scheduled site deliveries",
        ],
        "image": "images/reinforcement-steel.jpg",
    },
    {
        "slug": "transport-logistics",
        "number": "03",
        "icon": "truck",
        "title": "Transport & Project Logistics",
        "short": "Coordinated movement of purchased materials and commodities to site.",
        "summary": "We connect procurement with delivery. Our logistics coordination covers route planning, dispatch scheduling, load documentation and delivery confirmation for materials and commodities purchased through us.",
        "points": [
            "Construction-material transport",
            "Project cargo and bulk-load coordination",
            "Dispatch scheduling and route planning",
            "Proof of delivery and site handover",
        ],
        "image": None,
    },
    {
        "slug": "skilled-workforce",
        "number": "04",
        "icon": "hard-hat",
        "title": "Skilled Workforce",
        "short": "Qualified technical and site personnel aligned to project needs.",
        "summary": "We provide professional civil engineers, construction workers and trained site personnel to reinforce project teams and maintain delivery standards.",
        "points": [
            "Professional civil engineers",
            "Construction workers and site teams",
            "Plumbers and electricians",
            "Carpenters, tilers and finishing personnel",
        ],
        "image": "images/engineer-on-site.jpg",
    },
    {
        "slug": "industrial-structures",
        "number": "05",
        "icon": "warehouse",
        "title": "Industrial Structures",
        "short": "Steel frameworks and robust foundations for demanding operations.",
        "summary": "Drawing on our construction and steel-supply background, we support warehouses, factories, processing plants and other performance-critical industrial facilities.",
        "points": [
            "Warehouse and factory structures",
            "Steel framework coordination",
            "Plant and machinery support bases",
            "High-capacity storage foundations",
        ],
        "image": "images/civil-works.jpg",
    },
    {
        "slug": "specialist-trades",
        "number": "06",
        "icon": "ruler",
        "title": "Interior & Specialist Trades",
        "short": "Reliable tradespeople for installations, fit-outs and final finishes.",
        "summary": "Specialist teams help take projects from shell to completion with coordinated mechanical, electrical and interior workmanship.",
        "points": [
            "Gypsum ceilings and drywall partitions",
            "Electrical and plumbing installations",
            "Carpentry and tiling",
            "Interior finishing support",
        ],
        "image": None,
    },
]

PARTNERS = ["Bamburi Cement", "Bitzer", "IECooling", "Carrier", "Bock"]
SECTORS = [
    "Residential developments",
    "Commercial spaces",
    "Industrial facilities",
    "Road and site infrastructure",
    "Hospitality venues",
    "Warehousing and storage",
]


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "login"
    login_manager.login_message = "Please sign in to access the administration area."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_globals():
        return {
            "company": {
                "name": app.config["COMPANY_NAME"],
                "email": app.config["COMPANY_EMAIL"],
                "phone": app.config["COMPANY_PHONE"],
                "phone_alt": app.config["COMPANY_PHONE_ALT"],
                "address": app.config["COMPANY_ADDRESS"],
            },
            "nav_services": SERVICES[:4],
            "current_year": datetime.utcnow().year,
        }

    @app.after_request
    def secure_response(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        return response

    @app.get("/")
    def index():
        return render_template(
            "index.html", services=SERVICES, partners=PARTNERS, sectors=SECTORS
        )

    @app.get("/about")
    def about():
        return render_template("about.html", sectors=SECTORS)

    @app.get("/services")
    def services():
        return render_template("services.html", services=SERVICES)

    @app.get("/services/<slug>")
    def service_detail(slug):
        service = next((item for item in SERVICES if item["slug"] == slug), None)
        if not service:
            abort(404)
        related = [item for item in SERVICES if item["slug"] != slug][:3]
        return render_template(
            "service_detail.html", service=service, related=related
        )

    @app.get("/capabilities")
    def capabilities():
        return render_template("capabilities.html", sectors=SECTORS)

    @app.get("/partners")
    def partners():
        return render_template("partners.html", partners=PARTNERS)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = EnquiryForm()
        requested_service = request.args.get("service", "")
        if request.method == "GET" and requested_service:
            match = next(
                (item["title"] for item in SERVICES if item["slug"] == requested_service),
                None,
            )
            if match:
                form.service.data = match

        if form.validate_on_submit():
            enquiry = Enquiry(
                full_name=form.full_name.data.strip(),
                company=(form.company.data or "").strip(),
                email=form.email.data.lower().strip(),
                phone=form.phone.data.strip(),
                service=form.service.data,
                project_location=(form.project_location.data or "").strip(),
                message=form.message.data.strip(),
            )
            db.session.add(enquiry)
            db.session.commit()
            return redirect(url_for("thank_you"))
        return render_template("contact.html", form=form)

    @app.get("/thank-you")
    def thank_you():
        return render_template("thank_you.html")

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": app.config["COMPANY_NAME"]}

    @app.get("/robots.txt")
    def robots():
        content = f"User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: {url_for('sitemap', _external=True)}\n"
        return Response(content, mimetype="text/plain")

    @app.get("/sitemap.xml")
    def sitemap():
        pages = [
            url_for("index", _external=True),
            url_for("about", _external=True),
            url_for("services", _external=True),
            url_for("capabilities", _external=True),
            url_for("partners", _external=True),
            url_for("contact", _external=True),
        ] + [url_for("service_detail", slug=item["slug"], _external=True) for item in SERVICES]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
            f"<url><loc>{page}</loc></url>" for page in pages
        ) + "</urlset>"
        return Response(xml, mimetype="application/xml")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("admin_dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower().strip()).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                    return redirect(next_page)
                return redirect(url_for("admin_dashboard"))
            flash("The email or password is incorrect.", "error")
        return render_template("login.html", form=form)

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been signed out.", "success")
        return redirect(url_for("login"))

    @app.get("/admin")
    @login_required
    def admin_dashboard():
        if current_user.role != "admin":
            abort(403)
        status = request.args.get("status", "all")
        query = Enquiry.query.order_by(Enquiry.created_at.desc())
        if status in {"new", "contacted", "closed"}:
            query = query.filter_by(status=status)
        enquiries = query.all()
        counts = {
            "all": Enquiry.query.count(),
            "new": Enquiry.query.filter_by(status="new").count(),
            "contacted": Enquiry.query.filter_by(status="contacted").count(),
            "closed": Enquiry.query.filter_by(status="closed").count(),
        }
        return render_template(
            "admin/dashboard.html",
            enquiries=enquiries,
            counts=counts,
            active_status=status,
        )

    @app.post("/admin/enquiries/<int:enquiry_id>/status")
    @login_required
    def update_enquiry_status(enquiry_id):
        if current_user.role != "admin":
            abort(403)
        enquiry = db.get_or_404(Enquiry, enquiry_id)
        new_status = request.form.get("status")
        if new_status not in {"new", "contacted", "closed"}:
            abort(400)
        enquiry.status = new_status
        db.session.commit()
        flash("Enquiry status updated.", "success")
        return redirect(url_for("admin_dashboard"))

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        admin = User.query.filter_by(email=app.config["ADMIN_EMAIL"]).first()
        if not admin:
            admin = User(
                full_name="B&N Administrator",
                email=app.config["ADMIN_EMAIL"],
                role="admin",
            )
            admin.set_password(app.config["ADMIN_PASSWORD"])
            db.session.add(admin)
            db.session.commit()
            click.echo("Database initialized and administrator created.")
        else:
            click.echo("Database initialized. Administrator already exists.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--name", prompt=True, default="B&N Administrator")
    def create_admin_command(email, password, name):
        admin = User.query.filter_by(email=email.lower().strip()).first()
        if not admin:
            admin = User(full_name=name.strip(), email=email.lower().strip(), role="admin")
            db.session.add(admin)
        admin.full_name = name.strip()
        admin.role = "admin"
        admin.set_password(password)
        db.session.commit()
        click.echo("Administrator account is ready.")

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
