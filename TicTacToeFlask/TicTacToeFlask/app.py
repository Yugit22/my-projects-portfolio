from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret"

def check_winner(board, player):
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    return any(board[i] == board[j] == board[k] == player for i,j,k in wins)

def minimax(board, player):
    if check_winner(board, 'X'):
        return {'score': -1}
    if check_winner(board, 'O'):
        return {'score': 1}
    if '' not in board:
        return {'score': 0}

    moves = []
    for i in range(9):
        if board[i] == '':
            board[i] = player
            result = minimax(board, 'X' if player == 'O' else 'O')
            moves.append({'index': i, 'score': result['score']})
            board[i] = ''

    if player == 'O':
        return max(moves, key=lambda m: m['score'])
    else:
        return min(moves, key=lambda m: m['score'])

@app.route("/")
def index():
    if 'board' not in session:
        session['board'] = [''] * 9
        session['winner'] = None
    return render_template("index.html", board=session['board'], winner=session['winner'])

@app.route("/move/<int:index>", methods=['POST'])
def move(index):
    board = session['board']
    if board[index] == '' and session['winner'] is None:
        board[index] = 'X'
        if check_winner(board, 'X'):
            session['winner'] = 'You'
        elif '' not in board:
            session['winner'] = 'Draw'
        else:
            ai_move = minimax(board, 'O')['index']
            board[ai_move] = 'O'
            if check_winner(board, 'O'):
                session['winner'] = 'AI'
            elif '' not in board:
                session['winner'] = 'Draw'
    session['board'] = board
    return redirect(url_for('index'))

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
