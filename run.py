from app import create_app, db
from config import Config
from app.extensions import socketio


app = create_app()
app.debug = True
app.config.from_object(Config)

if __name__ == '__main__':
    print("🚀 Running...")
    #app.run(debug=True)
    socketio.run(app, debug=True)