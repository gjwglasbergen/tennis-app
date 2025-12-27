from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from services.match_service import MatchService

match_bp = Blueprint('match', __name__)
match_service = MatchService.get_instance()

from datetime import datetime

class MockMatch:
    def __init__(self, match_service):
        state = match_service.get_match_state()
        self.id = 1
        self.player1 = state['p1_name'] if state else "Unknown"
        self.player2 = state['p2_name'] if state else "Unknown"
        self.date_created = datetime.now()
        self.active = True

@match_bp.route('/')
def index():
    return render_template('index.html')

@match_bp.route('/create-match', methods=['GET', 'POST'])
def create_match():
    if request.method == 'POST':
        p1 = request.form.get('player1')
        p2 = request.form.get('player2')
        sets = int(request.form.get('best_of_num_sets', 3))
        games = int(request.form.get('num_games_to_win', 6))
        
        match_service.create_match(p1, p2, sets, games_to_win=games)
        return redirect(url_for('match.broadcast'))
    
    return render_template('creatematch.html')

@match_bp.route('/matches')
def matches():
    # Helper to show current match
    matches_list = []
    if match_service.active_match:
        matches_list.append(MockMatch(match_service))
    return render_template('matches.html', matches=matches_list)

@match_bp.route('/match/<int:match_id>')
def view_match(match_id):
    return render_template('viewmatch.html', mode='spectate')

@match_bp.route('/broadcast')
def broadcast():
    match = MockMatch(match_service) if match_service.active_match else None
    return render_template('viewmatch.html', mode='broadcast', tennis_match=match)

@match_bp.route('/spectate')
def spectate():
    match = MockMatch(match_service) if match_service.active_match else None
    return render_template('viewmatch.html', mode='spectate', tennis_match=match)

@match_bp.route('/api/state')
def get_state():
    return jsonify(match_service.get_match_state())
