from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.create_all()
        print("Base de datos creada con éxito.")
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

if __name__ == '__main__':
    app.run(debug=True)
