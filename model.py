# import requests
# import json
# import time
# from pprint import pprint

# # 必要なモジュールのインポート
# # 注: この環境ではVGG16モデルの利用をシミュレートしています
# from tensorflow.keras.applications.vgg16 import (
#     VGG16,
#     preprocess_input,
#     decode_predictions,
# )
# from tensorflow.keras.preprocessing import image
# import numpy as np


# # 食材の表記ゆれを修正するための辞書
# normalization_dict = {
#     "人参": "にんじん",
#     "ニンジン": "にんじん",
#     "にんじん": "にんじん",
#     "じゃがいも": "じゃがいも",
#     "ジャガイモ": "じゃがいも",
#     "玉ねぎ": "たまねぎ",
#     "玉葱": "たまねぎ",
#     "たまねぎ": "たまねぎ",
#     "牛肉": "牛肉",
#     "鶏肉": "鶏肉",
#     "豚肉": "豚肉",
#     "キャベツ": "キャベツ",
#     "もやし": "もやし",
# }

# # 予測結果とレシピ材料を紐づけるためのマッピング
# # VGG16の予測クラス名と、レシピの食材名を対応付けます
# prediction_to_material_map = {
#     "carrot": "にんじん",
#     "potato": "じゃがいも",
#     "onion": "たまねぎ",
#     "beef": "牛肉",
#     "chicken": "鶏肉",
#     "pork": "豚肉",
#     "cabbage": "キャベツ",
#     "bean_sprout": "もやし",
# }


# # 食材の表記ゆれを修正する関数
# def normalize_name(name: str) -> str:
#     # 前後の空白除去
#     name = name.strip()
#     # 置換辞書で統一（存在しなければそのまま）
#     return normalization_dict.get(name, name)


# # --- 画像から物体を予測する関数 ---
# def get_predicted_ingredients(image_path: str) -> list:
#     """
#     画像から物体を予測し、レシピ材料に変換してリストで返します。
#     """
#     try:
#         # 画像の読み込みと前処理
#         input_image = image.load_img(image_path, target_size=(224, 224))
#         input_image = image.img_to_array(input_image)
#         input_image = np.expand_dims(input_image, axis=0)
#         input_image = preprocess_input(input_image)

#         # 既存モデルの導入と予測
#         model = VGG16(weights="imagenet")
#         results = model.predict(input_image)
#         decode_results = decode_predictions(results, top=5)[0]

#         predicted_ingredients = []
#         for _, predicted_class, _ in decode_results:
#             # 予測されたクラス名をレシピ材料名にマッピング
#             normalized_material = prediction_to_material_map.get(predicted_class, None)
#             if normalized_material:
#                 predicted_ingredients.append(normalized_material)

#         return predicted_ingredients
#     except Exception as e:
#         print(f"画像予測中にエラーが発生しました: {e}")
#         return []


# # --- レシピ検索関数 ---
# def find_recipes_by_ingredients(final_recipes: dict, ingredients: list) -> dict:
#     """
#     与えられた食材リストを含むレシピを検索し、カテゴリごとに辞書で返します。
#     """
#     # 食材リストをセットに変換して検索を高速化
#     ingredients_set = set(ingredients)

#     # マッチしたレシピをカテゴリごとに格納するための新しい辞書
#     matching_recipes = {}

#     # final_recipes 辞書の各カテゴリをループ
#     for category_name, recipes_in_category in final_recipes.items():
#         matched_list = []
#         # 各カテゴリのレシピリストをループ
#         for recipe in recipes_in_category:
#             # レシピの材料リストに、検索したい食材が一つでも含まれているかチェック
#             recipe_materials_set = set(recipe["recipeMaterial"])
#             if ingredients_set.intersection(recipe_materials_set):
#                 matched_list.append(recipe)

#         # マッチしたレシピが存在すれば、新しい辞書にカテゴリごとに追加
#         if matched_list:
#             matching_recipes[category_name] = matched_list

#     return matching_recipes


# # --- 以下、全体の処理フロー ---
# def main():
#     # カテゴリ名と対応するIDをまとめた辞書
#     categories = {
#         "spring": "12-100",
#         "summer": "12-101",
#         "autumn": "12-102",
#         "winter": "12-103",
#         "prepare": "20-199-2185",  # 作り置き
#         "curry": "30-307-1164",  # 野菜カレー
#         "stir_fry": "30-312-1211",  # 肉野菜炒め
#     }

#     # 最終的な結果を格納する辞書
#     final_recipes = {}

#     # 各カテゴリのURLとデータを取得し、必要な情報だけを抽出
#     for category_name, category_id in categories.items():
#         url = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId=1052309877447068248&categoryId={category_id}"

#         try:
#             response = requests.get(url)
#             response.raise_for_status()  # HTTPエラーが発生した場合に例外を投げる
#             json_data = json.loads(response.text)

#             recipes_list = []
#             if "result" in json_data and "recipes" in json_data["result"]:
#                 for recipe in json_data["result"]["recipes"]:
#                     extracted_data = {
#                         "rank": recipe.get("recipeRanking", None),
#                         "recipeMaterial": recipe.get("recipeMaterial", []),
#                         "recipeUrl": recipe.get("recipeUrl", None),
#                         "recipeTitle": recipe.get("recipeTitle", None),
#                     }
#                     recipes_list.append(extracted_data)

#             final_recipes[category_name] = recipes_list
#             print(f"{category_name} のデータを取得しました。")

#             time.sleep(1)

#         except requests.exceptions.RequestException as e:
#             print(f"エラーが発生しました: {e}")
#             print(f"カテゴリ: {category_name} の取得をスキップします。")
#             continue

#     # 全レシピの材料表記を正規化
#     for category_name, recipes_in_category in final_recipes.items():
#         for recipe in recipes_in_category:
#             normalized_materials = []
#             for material in recipe["recipeMaterial"]:
#                 normalized_materials.append(normalize_name(material))
#             recipe["recipeMaterial"] = normalized_materials

#     # --- 画像から食材を予測し、レシピを検索 ---
#     input_filename = input("画像のパスを入力してください: ")
#     predicted_ingredients = get_predicted_ingredients(input_filename)

#     print("\n--- 画像から予測された食材 ---")
#     if not predicted_ingredients:
#         print("予測された食材はありませんでした。")
#     else:
#         print(predicted_ingredients)

#     matching_recipes = find_recipes_by_ingredients(final_recipes, predicted_ingredients)

#     # 結果を表示
#     print("\n--- 予測食材を含むレシピ ---")
#     if not matching_recipes:
#         print("一致するレシピは見つかりませんでした。")
#     else:
#         pprint(matching_recipes)


# if __name__ == "__main__":
#     main()


# model.pyの内容
import requests
import json
import time
from pprint import pprint

# 必要なモジュールのインポート
from tensorflow.keras.applications.vgg16 import (
    VGG16,
    preprocess_input,
    decode_predictions,
)
from tensorflow.keras.preprocessing import image
import numpy as np


# 食材の表記ゆれを修正するための辞書
normalization_dict = {
    "人参": "にんじん",
    "ニンジン": "にんじん",
    "にんじん": "にんじん",
    "じゃがいも": "じゃがいも",
    "ジャガイモ": "じゃがいも",
    "玉ねぎ": "たまねぎ",
    "玉葱": "たまねぎ",
    "たまねぎ": "たまねぎ",
    "牛肉": "牛肉",
    "鶏肉": "鶏肉",
    "豚肉": "豚肉",
    "キャベツ": "キャベツ",
    "もやし": "もやし",
}

# 予測結果とレシピ材料を紐づけるためのマッピング
prediction_to_material_map = {
    "carrot": "にんじん",
    "potato": "じゃがいも",
    "onion": "たまねぎ",
    "beef": "牛肉",
    "chicken": "鶏肉",
    "pork": "豚肉",
    "cabbage": "キャベツ",
    "bean_sprout": "もやし",
}


# 食材の表記ゆれを修正する関数
def normalize_name(name: str) -> str:
    name = name.strip()
    return normalization_dict.get(name, name)


# --- 画像から物体を予測する関数 ---
def get_predicted_ingredients(image_path: str) -> list:
    """
    画像から物体を予測し、レシピ材料に変換してリストで返します。
    """
    try:
        input_image = image.load_img(image_path, target_size=(224, 224))
        input_image = image.img_to_array(input_image)
        input_image = np.expand_dims(input_image, axis=0)
        input_image = preprocess_input(input_image)

        model = VGG16(weights="imagenet")
        results = model.predict(input_image)
        decode_results = decode_predictions(results, top=5)[0]

        predicted_ingredients = []
        for _, predicted_class, _ in decode_results:
            normalized_material = prediction_to_material_map.get(predicted_class, None)
            if normalized_material:
                predicted_ingredients.append(normalized_material)

        return predicted_ingredients
    except Exception as e:
        print(f"画像予測中にエラーが発生しました: {e}")
        return []


# --- レシピ検索関数 ---
def find_recipes_by_ingredients(final_recipes: dict, ingredients: list) -> dict:
    """
    与えられた食材リストを含むレシピを検索し、カテゴリごとに辞書で返します。
    """
    ingredients_set = set(ingredients)
    matching_recipes = {}

    for category_name, recipes_in_category in final_recipes.items():
        matched_list = []
        for recipe in recipes_in_category:
            recipe_materials_set = set(recipe["recipeMaterial"])
            if ingredients_set.intersection(recipe_materials_set):
                matched_list.append(recipe)

        if matched_list:
            matching_recipes[category_name] = matched_list

    return matching_recipes


# `main()`関数は削除するか、デバッグ用に残す
if __name__ == "__main__":
    # ここにテスト用のコードを記述
    pass
