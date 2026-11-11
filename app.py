from flask import Flask, render_template_string, request, jsonify
import math

app = Flask(__name__)

# كود واجهة المستخدم والتصميم داخل السكربت مباشرة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحدي الذكاء الاصطناعي - XO</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-x: #38bdf8;
            --accent-o: #f43f5e;
            --text-color: #f8fafc;
        }

        * {
            box-sizing: border-box;
            font-family: 'Tajawal', sans-serif;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .container {
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 24px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 420px;
            width: 90%;
        }

        h1 {
            font-weight: 900;
            margin-bottom: 1.5rem;
            font-size: 2rem;
            background: linear-gradient(to right, var(--accent-x), var(--accent-o));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .symbol-select {
            margin-bottom: 1.5rem;
        }

        .symbol-select p {
            margin-bottom: 0.5rem;
            color: #94a3b8;
        }

        .btn-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }

        .symbol-btn {
            background: #334155;
            color: #fff;
            border: 2px solid transparent;
            padding: 10px 24px;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }

        .symbol-btn.active-x {
            border-color: var(--accent-x);
            color: var(--accent-x);
            background: rgba(56, 189, 248, 0.1);
        }

        .symbol-btn.active-o {
            border-color: var(--accent-o);
            color: var(--accent-o);
            background: rgba(244, 63, 94, 0.1);
        }

        .board {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 1.5rem;
        }

        .cell {
            width: 100%;
            aspect-ratio: 1;
            background: #334155;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            user-select: none;
        }

        .cell:hover {
            background: #475569;
            transform: translateY(-2px);
        }

        .cell.x { color: var(--accent-x); }
        .cell.o { color: var(--accent-o); }

        .status {
            font-size: 1.2rem;
            font-weight: bold;
            min-height: 28px;
            margin-bottom: 1rem;
        }

        .reset-btn {
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: opacity 0.2s;
            width: 100%;
        }

        .reset-btn:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>تحدي الـ XO الذكي</h1>
    
    <div class="symbol-select">
        <p>اختر رمزا للعب:</p>
        <div class="btn-group">
            <button class="symbol-btn active-x" onclick="selectSymbol('X')">X</button>
            <button class="symbol-btn" onclick="selectSymbol('O')">O</button>
        </div>
    </div>

    <div class="board" id="board">
        <div class="cell" onclick="makeMove(0)"></div>
        <div class="cell" onclick="makeMove(1)"></div>
        <div class="cell" onclick="makeMove(2)"></div>
        <div class="cell" onclick="makeMove(3)"></div>
        <div class="cell" onclick="makeMove(4)"></div>
        <div class="cell" onclick="makeMove(5)"></div>
        <div class="cell" onclick="makeMove(6)"></div>
        <div class="cell" onclick="makeMove(7)"></div>
        <div class="cell" onclick="makeMove(8)"></div>
    </div>

    <div class="status" id="status">دورك للعب!</div>
    <button class="reset-btn" onclick="resetGame()">إعادة اللعب</button>
</div>

<script>
    let board = ["", "", "", "", "", "", "", "", ""];
    let playerSymbol = "X";
    let aiSymbol = "O";
    let isGameActive = true;

    function selectSymbol(symbol) {
        if (board.some(cell => cell !== "")) return;
        playerSymbol = symbol;
        aiSymbol = symbol === 'X' ? 'O' : 'X';

        document.querySelectorAll('.symbol-btn').forEach(btn => {
            btn.classList.remove('active-x', 'active-o');
        });

        if (symbol === 'X') {
            document.querySelectorAll('.symbol-btn')[0].classList.add('active-x');
        } else {
            document.querySelectorAll('.symbol-btn')[1].classList.add('active-o');
            aiFirstMove();
        }
    }

    async function aiFirstMove() {
        document.getElementById('status').innerText = 'الذكاء الاصطناعي يفكر...';
        const response = await fetch('/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: board, player_symbol: playerSymbol })
        });
        const data = await response.json();
        board = data.board;
        renderBoard();
        document.getElementById('status').innerText = 'دورك الآن!';
    }

    async function makeMove(index) {
        if (board[index] !== "" || !isGameActive) return;

        board[index] = playerSymbol;
        renderBoard();

        document.getElementById('status').innerText = 'الذكاء الاصطناعي يفكر...';

        const response = await fetch('/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: board, player_symbol: playerSymbol })
        });

        const data = await response.json();
        board = data.board;
        renderBoard();

        if (data.winner) {
            isGameActive = false;
            if (data.winner === 'Draw') {
                document.getElementById('status').innerText = 'تعادل!';
            } else if (data.winner === playerSymbol) {
                document.getElementById('status').innerText = 'لقد فزت! 🎉';
            } else {
                document.getElementById('status').innerText = 'فاز الذكاء الاصطناعي! 🤖';
            }
        } else {
            document.getElementById('status').innerText = 'دورك الآن!';
        }
    }

    function renderBoard() {
        const cells = document.querySelectorAll('.cell');
        board.forEach((val, idx) => {
            cells[idx].innerText = val;
            cells[idx].className = 'cell ' + val.toLowerCase();
        });
    }

    function resetGame() {
        board = ["", "", "", "", "", "", "", "", ""];
        isGameActive = true;
        document.getElementById('status').innerText = 'دورك للعب!';
        renderBoard();
        if (playerSymbol === 'O') {
            aiFirstMove();
        }
    }
</script>

</body>
</html>
"""

def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # أفقي
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # رأسي
        [0, 4, 8], [2, 4, 6]             # قطري
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != "":
            return board[condition[0]]
    if "" not in board:
        return "Draw"
    return None

def minimax(board, depth, is_maximizing, ai_symbol, player_symbol):
    winner = check_winner(board)
    if winner == ai_symbol:
        return 10 - depth
    elif winner == player_symbol:
        return depth - 10
    elif winner == "Draw":
        return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = ai_symbol
                score = minimax(board, depth + 1, False, ai_symbol, player_symbol)
                board[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = player_symbol
                score = minimax(board, depth + 1, True, ai_symbol, player_symbol)
                board[i] = ""
                best_score = min(score, best_score)
        return best_score

def get_best_move(board, ai_symbol, player_symbol):
    best_score = -math.inf
    best_move = None
    for i in range(9):
        if board[i] == "":
            board[i] = ai_symbol
            score = minimax(board, 0, False, ai_symbol, player_symbol)
            board[i] = ""
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    board = data.get('board')
    player_symbol = data.get('player_symbol')
    ai_symbol = 'O' if player_symbol == 'X' else 'X'

    winner = check_winner(board)
    if winner:
        return jsonify({'board': board, 'winner': winner})

    ai_move = get_best_move(board, ai_symbol, player_symbol)
    if ai_move is not None:
        board[ai_move] = ai_symbol

    winner = check_winner(board)
    return jsonify({'board': board, 'winner': winner, 'ai_move': ai_move})

if __name__ == '__main__':
    print("تشغيل الخادم... افتح الرابط التالي في المتصفح: http://127.0.0.1:5000")
    app.run(debug=True)
  
