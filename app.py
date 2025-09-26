from flask import Flask
from dashboard.dashboard import dashboard

def create_app():
    app = Flask(__name__)
    app.static_folder = 'dashboard/static'
    app.register_blueprint(dashboard)
    return app

# Create a module-level app variable for Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    