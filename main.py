import pandas as pd
import traceback
from datetime import datetime


def main():
    # ===== test.csv 読み込み =====
    try:
        df = pd.read_csv("test.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        print("❌ test.csv が見つかりません")
        print("→ main.py と同じフォルダに置いてください")
        return

    # ===== 設定読み込み（config.csv）=====
    try:
        config = pd.read_csv("config.csv")
        LOW_PROFIT_RATE = float(
            config.loc[config["key"] == "low_profit_rate", "value"].values[0]
        )
    except FileNotFoundError:
        print("❌ config.csv が見つかりません")
        print("→ merch_tool フォルダに config.csv を置いてください")
        return
    except Exception:
        print("❌ config.csv の読み込みに失敗しました")
        print("→ low_profit_rate が設定されているか確認してください")
        return

    # 列名の空白対策
    df.columns = df.columns.str.strip()

    # 必須列チェック
    required_cols = ["商品名", "仕入価格", "販売価格", "在庫数"]
    for col in required_cols:
        if col not in df.columns:
            print(f"❌ 『{col}』列がありません")
            print("現在の列：", list(df.columns))
            return

    # 数値変換（入力ミス対策）
    for col in ["仕入価格", "販売価格", "在庫数"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[["仕入価格", "販売価格", "在庫数"]].isnull().any().any():
        print("❌ 数値が正しく入力されていない行があります")
        return

    # ===== 判定処理 =====
    df["利益"] = df["販売価格"] - df["仕入価格"]

    # 利益率（%）計算（販売価格が0のときは0にする）
    df["利益率(%)"] = (
        df["利益"] / df["販売価格"].replace(0, pd.NA) * 100
    ).fillna(0).round(1)

    df["判定理由"] = ""

    # 赤字判定
    df.loc[df["利益"] < 0, "判定理由"] = "赤字"

    # 在庫なし判定（赤字より優先）
    df.loc[df["在庫数"] <= 0, "判定理由"] = "在庫なし"

    # 低利益率判定（赤字・在庫なしでないもの）
    df.loc[
        (df["判定理由"] == "") &
        (df["利益率(%)"] < LOW_PROFIT_RATE),
        "判定理由"
    ] = "低利益率"

    # 判定列
    df["判定"] = df["判定理由"].apply(
        lambda x: "NG" if x != "" else "OK"
    )

    # ===== ファイル名作成 =====
    today = datetime.now().strftime("%Y-%m-%d")
    all_filename = f"checked_items_{today}.csv"
    problem_filename = f"problem_items_{today}.csv"

    # ===== 列順を整える（スプシで見やすく）=====
    column_order = [
        "商品名",
        "判定",
        "判定理由",
        "利益率(%)",
        "利益",
        "仕入価格",
        "販売価格",
        "在庫数",
    ]

    df = df[column_order]


    # ===== 全件結果CSV =====
    df.to_csv(all_filename, index=False, encoding="utf-8-sig")

    # ===== NG商品のみ =====
    problem_df = df[df["判定"] == "NG"]

    if problem_df.empty:
        print(f"✅ 全件結果：{all_filename}")
        print("✅ 問題のあるデータはありませんでした")
        return

    problem_df.to_csv(problem_filename, index=False, encoding="utf-8-sig")

    print(f"✅ 全件結果：{all_filename}")
    print(f"✅ 問題商品：{problem_filename}（{len(problem_df)}件）")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("❌ 予期しないエラーが発生しました")
        traceback.print_exc()
        input("Enterキーで終了")
