from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

def init_db():
    conn = sqlite3.connect('material.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            part_number TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            image TEXT,
            min_quantity INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.before_first_request
def create_tables():
    init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('material.db')
    c = conn.cursor()

    if request.method == 'POST':
        if 'add' in request.form:
            name = request.form['name']
            part_number = request.form['part_number']
            quantity = int(request.form['quantity'])
            min_quantity = int(request.form.get('min_quantity', 0))
            image = request.files['image']
            filename = None
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            c.execute('INSERT INTO materials (name, part_number, quantity, image, min_quantity) VALUES (?, ?, ?, ?, ?)',
                      (name, part_number, quantity, filename, min_quantity))
            conn.commit()
        elif 'stock_in' in request.form:
            mat_id = int(request.form['stock_in'])
            c.execute('UPDATE materials SET quantity = quantity + 1 WHERE id = ?', (mat_id,))
            conn.commit()
        elif 'stock_out' in request.form:
            mat_id = int(request.form['stock_out'])
            c.execute('UPDATE materials SET quantity = quantity - 1 WHERE id = ?', (mat_id,))
            conn.commit()
        elif 'delete' in request.form:
            mat_id = int(request.form['delete'])
            c.execute('DELETE FROM materials WHERE id = ?', (mat_id,))
            conn.commit()

    c.execute('SELECT * FROM materials')
    materials = c.fetchall()
    conn.close()
    return render_template('index.html', materials=materials)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)
