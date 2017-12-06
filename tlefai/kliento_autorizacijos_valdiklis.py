from flask import Flask
from flask import render_template
from flask import request


def patikrinti_duomenis(username, password):
    return True

def prisijungti(username):
    return 'Prijungto vartotojo puslapis, vartotojas: ' + username