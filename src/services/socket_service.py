from flask_socketio import SocketIO, emit
from typing import Optional
from .match_service import MatchService

class SocketService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.match_service = MatchService.get_instance()
        self.setup_handlers()

    def setup_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            # Send current state on connect
            state = self.match_service.get_match_state()
            if state:
                emit('match_update', state)

        @self.socketio.on('score_update')
        def handle_score_update(data):
            player = data.get('player') # 1 or 2
            if not player:
                return
            
            new_state = self.match_service.score_point(int(player))
            if new_state:
                emit('match_update', new_state, broadcast=True)
                
        @self.socketio.on('reset_match')
        def handle_reset():
            # Logic to reset match
            pass
