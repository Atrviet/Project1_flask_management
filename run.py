from app import create_app, db

app = create_app()

with app.app_context():
    # Import models TRONG app context
    from app.models import Admin
    
    db.create_all()
    
    # Tạo admin mặc định
    if not Admin.query.filter_by(username='admin').first():
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')
        db.session.add(default_admin)
        db.session.commit()
        print("Đã tạo admin mặc định!")

if __name__ == '__main__':
    print("Running...")
    app.run(debug=True)