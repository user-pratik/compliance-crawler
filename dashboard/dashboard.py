# Dashboard module
from flask import Blueprint, render_template, request, redirect, url_for, send_file
import os
from core import master
import json



dashboard = Blueprint(
    "dashboard",
    __name__,
    template_folder="templates",
    static_folder="static"
)

TEMP_DIR = os.path.join(os.getcwd(), "temp")


@dashboard.route("/")
def home():
    return render_template("landing.html")

@dashboard.route("/demo")
def demo():
    return render_template("index.html")


@dashboard.route("/process", methods=["GET", "POST"])
def process():
    if request.method == "POST":
        product_url = request.form.get("product_url")
        if product_url:
            data = master.process_product(product_url)
            # save raw data to temp (for now as a txt file)
            os.makedirs(TEMP_DIR, exist_ok=True)
            with open(os.path.join(TEMP_DIR, "output.txt"), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return redirect(url_for("dashboard.report"))
    return render_template("process.html")


@dashboard.route("/report")
def report():
    data = None
    output_file = os.path.join(TEMP_DIR, "output.txt")
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Convert local image paths to web-accessible URLs
        if data and "images" in data:
            web_images = []
            for img_path in data["images"]:
                if os.path.exists(img_path):
                    # Get relative path from temp directory
                    rel_path = os.path.relpath(img_path, TEMP_DIR)
                    web_url = url_for("dashboard.serve_temp_image", filename=rel_path.replace("\\", "/"))
                    web_images.append(web_url)
            data["images"] = web_images
            
    return render_template("report.html", data=data)


@dashboard.route("/temp/<path:filename>")
def serve_temp_image(filename):
    """Serve images from the temp directory"""
    temp_path = os.path.join(TEMP_DIR, filename.replace("/", os.sep))
    if os.path.exists(temp_path) and os.path.isfile(temp_path):
        return send_file(temp_path)
    return "Image not found", 404
