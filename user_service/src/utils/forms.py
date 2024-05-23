from wtforms import Form, BooleanField, StringField, PasswordField, validators


class LoginForm(Form):
    login = StringField("Login", validators=[validators.Length(min=7, max=50),
                                             validators.DataRequired(message="Please Fill This Field")])

    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])


class RegisterForm(Form):
    username = StringField("Username", validators=[validators.Length(min=3, max=25),
                                                   validators.DataRequired(message="Please Fill This Field")])

    login = StringField("Login", validators=[validators.Length(min=7, max=50),
                                             validators.DataRequired(message="Please Fill This Field")])

    admin = BooleanField("Admin")

    password = PasswordField("Password", validators=[

        validators.DataRequired(message="Please Fill This Fiield"),

        validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
    ])

    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")])


class UpdateForm(Form):
    login = StringField("Login", validators=[validators.Length(min=7, max=50),
                                             validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[

        validators.DataRequired(message="Please Fill This Fiield"),

        validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
    ])

    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")])
