from django.forms import Form, EmailField


class SecretAllySignupForm (Form):
    email = EmailField()
