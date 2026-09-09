from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, Optional


SERVICE_CHOICES = [
    ("", "Select a service"),
    ("Civil Engineering & Building Works", "Civil Engineering & Building Works"),
    ("Building Materials & Commodities", "Building Materials & Commodities"),
    ("Transport & Project Logistics", "Transport & Project Logistics"),
    ("Skilled Workforce", "Skilled Workforce"),
    ("Industrial Structures", "Industrial Structures"),
    ("Interior & Specialist Trades", "Interior & Specialist Trades"),
    ("General Enquiry", "General Enquiry"),
]


class EnquiryForm(FlaskForm):
    full_name = StringField(
        "Full name", validators=[DataRequired(), Length(min=2, max=120)]
    )
    company = StringField("Company", validators=[Optional(), Length(max=160)])
    email = EmailField("Business email", validators=[DataRequired(), Email()])
    phone = StringField(
        "Phone number", validators=[DataRequired(), Length(min=7, max=60)]
    )
    service = SelectField(
        "Service required", choices=SERVICE_CHOICES, validators=[DataRequired()]
    )
    project_location = StringField(
        "Project or delivery location", validators=[Optional(), Length(max=160)]
    )
    message = TextAreaField(
        "Tell us what you need",
        validators=[DataRequired(), Length(min=20, max=3000)],
    )
    consent = BooleanField(
        "I agree to be contacted about this enquiry.", validators=[DataRequired()]
    )
    submit = SubmitField("Send enquiry")


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me signed in")
    submit = SubmitField("Sign in")

