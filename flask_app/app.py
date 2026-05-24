# flask_app/app.py
# Main Flask application entry point.
# Run: python flask_app/app.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask           import Flask, render_template, request, jsonify
from dotenv          import load_dotenv
from services.material_finder import find_materials
from services.risk_analyser   import analyse_manufacturer

load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    """Search page — user enters manufacturer type."""
    return render_template('index.html')


@app.route('/analyse', methods=['POST'])
def analyse():
    """
    Receives manufacturer name from search form.
    Identifies materials and redirects to results.
    """
    manufacturer = request.form.get('manufacturer', '').strip()

    if not manufacturer:
        return render_template('index.html', error='Please enter a manufacturer type.')

    # Find raw materials
    materials = find_materials(manufacturer)

    return render_template(
        'loading.html',
        manufacturer = manufacturer,
        materials    = materials,
    )


@app.route('/results')
def results():
    """Results dashboard page."""
    manufacturer = request.args.get('manufacturer', '')
    return render_template('results.html', manufacturer=manufacturer)


@app.route('/api/analyse')
def api_analyse():
    """
    API endpoint — called by frontend via AJAX.
    Returns full risk analysis as JSON.
    """
    manufacturer = request.args.get('manufacturer', '').strip()

    if not manufacturer:
        return jsonify({'error': 'No manufacturer specified'}), 400

    materials = find_materials(manufacturer)
    result    = analyse_manufacturer(manufacturer, materials)

    return jsonify(result)


@app.route('/api/materials')
def api_materials():
    """Returns identified materials for a manufacturer."""
    manufacturer = request.args.get('manufacturer', '').strip()
    materials    = find_materials(manufacturer)
    return jsonify({'manufacturer': manufacturer, 'materials': materials})


if __name__ == '__main__':
    app.run(debug=True, port=5000)