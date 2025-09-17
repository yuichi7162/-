# import os
# from flask import Flask, request, render_template

# from model import get_predicted_ingredients

# #
# UPLOAD_FOLDER = "./static/vegetable_image"

# app = Flask(__name__)


# @app.route("/")
# def index():
#     return render_template("index.html")


# @app.route("/upload", methods=["GET", "POST"])
# def upload_user_files():
#     if request.method == "POST":
#         upload_file = request.files["upload_file"]
#         img_path = os.path.join(UPLOAD_FOLDER, upload_file.filename)
#         upload_file.save(img_path)
#         result, score = get_predicted_ingredients(img_path)
#         return render_template(
#             "result.html", score=int(score * 100), result=result, img_path=img_path
#         )


# if __name__ == "__main__":
#     app.run(debug=True)

import os
import requests
import json
import time
from flask import Flask, request, render_template

# model.pyから必要な関数をインポート
# get_predicted_ingredients と find_recipes_by_ingredients
from model import get_predicted_ingredients, find_recipes_by_ingredients

# Flaskアプリのインスタンスを作成
app = Flask(__name__)
# 画像の保存先フォルダを設定
UPLOAD_FOLDER = "./static/vegetable_image"

# --- アプリケーション起動時に実行されるレシピデータ取得ロジック ---
# レシピデータを格納するグローバル変数
final_recipes = {}

# 楽天レシピAPIのカテゴリIDを定義
categories = {
    "spring": "12-100",
    "summer": "12-101",
    "autumn": "12-102",
    "winter": "12-103",
    "prepare": "20-199-2185",
    "curry": "30-307-1164",
    "stir_fry": "30-312-1211",
}

# 各カテゴリのURLからレシピデータを取得
for category_name, category_id in categories.items():
    url = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1052309877447068248&categoryId={category_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を投げる
        json_data = json.loads(response.text)
        recipes_list = []
        if "result" in json_data and "recipes" in json_data["result"]:
            for recipe in json_data["result"]["recipes"]:
                extracted_data = {
                    "rank": recipe.get("recipeRanking", None),
                    "recipeMaterial": recipe.get("recipeMaterial", []),
                    "recipeUrl": recipe.get("recipeUrl", None),
                    "recipeTitle": recipe.get("recipeTitle", None),
                }
                recipes_list.append(extracted_data)
        final_recipes[category_name] = recipes_list
        time.sleep(1)  # APIに負荷をかけないよう1秒待機
    except requests.exceptions.RequestException as e:
        print(f"エラー: {category_name} の取得をスキップします。")
        continue

# --- ルーティング ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_user_files():
    # # ファイルがリクエストに含まれているか確認
    # if "upload_file" not in request.files:
    #     return "ファイルがアップロードされていません", 400

    upload_file = request.files["upload_file"]
    # # ファイル名が空かどうか確認
    # if upload_file.filename == "":
    #     return "ファイルが選択されていません", 400

    # 画像の保存パスを生成
    img_path = os.path.join(UPLOAD_FOLDER, upload_file.filename)

    try:
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        # ファイルを保存
        upload_file.save(img_path)
    except Exception as e:
        return f"ファイルの保存中にエラーが発生しました: {e}", 500

    # `model.py`からインポートした関数を呼び出す
    predicted_ingredients = get_predicted_ingredients(img_path)

    # レシピ検索
    matching_recipes = find_recipes_by_ingredients(final_recipes, predicted_ingredients)

    # テンプレートにデータを渡してレンダリング
    return render_template(
        "result.html",
        # img_path=img_path.replace("./static", ""),  # HTML用にパスを修正
        img_path=os.path.join("vegetable_image", upload_file.filename),
        predicted_ingredients=predicted_ingredients,
        matching_recipes=matching_recipes,
    )


# スクリプトが直接実行された場合にサーバーを起動
if __name__ == "__main__":
    app.run(debug=True)
