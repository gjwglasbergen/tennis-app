from flask import Flask
from flask_socketio import SocketIO
from services.socket_service import SocketService
from routes.match_routes import match_bp

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    
    # Register Blueprints
    app.register_blueprint(match_bp)
    
    # Init SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Init Socket Service
    SocketService(socketio)
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
