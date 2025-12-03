import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# ------------------------------------
# Flask 初期化
# ------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shiritori.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 画像保存先
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ------------------------------------
# DBモデル
# ------------------------------------
# 絵を投稿
class Drawing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 画像のパス
    image_path = db.Column(db.String(255), nullable=False)
    # タイトル（任意）
    title = db.Column(db.String(100))
    # 投稿日
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # しりとりの前の絵（チェーン構造）
    previous_id = db.Column(db.Integer, db.ForeignKey("drawing.id"))
    previous = db.relationship("Drawing", remote_side=[id])
    # 次の人が描く頭文字（任意）
    next_head = db.Column(db.String(10))

# リクエスト
class RequestState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drawing_id = db.Column(db.Integer)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    limit_seconds = db.Column(db.Integer, default=120)
    active = db.Column(db.Boolean, default=True)



# ------------------------------------
# ルーティング
# ------------------------------------

@app.route('/')
def index():
    # 進行中のリクエストを取得
    active_req = RequestState.query.filter_by(active=True).first()

    remaining = None
    if active_req:
        elapsed = (datetime.utcnow() - active_req.start_time).total_seconds()
        remaining = max(0, active_req.limit_seconds - int(elapsed))

        # タイムアウトしたら無効化
        if remaining <= 0:
            active_req.active = False
            db.session.commit()

    # 最新の絵を20件
    drawings = Drawing.query.order_by(Drawing.id.desc()).limit(20).all()

    return render_template(
        "index.html",
        drawings=drawings,
        active_req=active_req,
        remaining=remaining
    )



# 新規投稿フォーム
@app.route('/post', methods=['GET'])
def post_form():
    # 前の絵のID
    prev_id = request.args.get("prev_id", None)
    return render_template("post.html", prev_id=prev_id)


# 投稿処理
@app.route('/post', methods=['POST'])
def post():
    file = request.files['image']
    title = request.form.get('title')
    prev_id = request.form.get('prev_id')
    next_head = request.form.get('next_head')

    if not file:
        return "画像がありません", 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    drawing = Drawing(
        image_path=filename,
        title=title,
        previous_id=prev_id if prev_id else None,
        next_head=next_head
    )
    db.session.add(drawing)
    db.session.commit()

    return redirect(url_for("chain", drawing_id=drawing.id))


# チェーン表示
@app.route('/chain/<int:drawing_id>')
def chain(drawing_id):
    # 逆方向にたどる（前の絵 → さらに前の絵 → …）
    chain_list = []
    cur = Drawing.query.get(drawing_id)

    while cur:
        chain_list.append(cur)
        cur = cur.previous

    chain_list.reverse()

    return render_template("chain.html", chain=chain_list)

@app.route('/request_start/<int:drawing_id>')
def request_start(drawing_id):
    # 他のリクエストを終了
    RequestState.query.update({RequestState.active: False})

    req = RequestState(
        drawing_id=drawing_id,
        start_time=datetime.utcnow(),
        limit_seconds=120,
        active=True
    )
    db.session.add(req)
    db.session.commit()

    return redirect(url_for("post_form", prev_id=drawing_id))


# ------------------------------------
# 起動
# ------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
