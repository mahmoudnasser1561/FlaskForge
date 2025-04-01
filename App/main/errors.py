from flask import render_template
from . import main

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@main.errorhandler(405)
def method_not_allowed(e):
    return render_template('500.html'), 500