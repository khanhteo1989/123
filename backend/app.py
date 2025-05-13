from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

# Khởi tạo cơ sở dữ liệu
db = SQLAlchemy(app)

# Mẫu bảng khách hàng trong cơ sở dữ liệu
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)

# Hàm kiểm tra loại file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Trang chủ
@app.route('/')
def index():
    customers = Customer.query.all()  # Lấy danh sách khách hàng từ cơ sở dữ liệu
    return render_template('index.html', customers=customers)

# Trang upload file Excel
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Kiểm tra xem có file trong request không
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        
        # Kiểm tra nếu file có hợp lệ
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Xử lý file Excel
            df = pd.read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Đọc dữ liệu từ file Excel và lưu vào cơ sở dữ liệu
            for index, row in df.iterrows():
                new_customer = Customer(
                    name=row['Name'],
                    phone=row['Phone'],
                    email=row['Email'],
                    address=row['Address']
                )
                db.session.add(new_customer)
            
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('upload.html')

if __name__ == '__main__':
    db.create_all()  # Tạo cơ sở dữ liệu nếu chưa có
    app.run(debug=True)
