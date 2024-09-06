from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import io
import matplotlib.pyplot as plt
import base64

app = Flask(__name__)

# プロダクトデータを保持するリスト
product_data = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global product_data
    selected_product = None
    chart_data = None

    if request.method == 'POST':
        if 'add_product' in request.form:
            # プロダクトを追加または更新
            product = request.form['product']
            effectiveness = float(request.form['effectiveness'])
            invasiveness = float(request.form['invasiveness'])
            cost = float(request.form['cost'])
            usability = float(request.form['usability'])

            # 既存のプロダクトを更新、なければ追加
            for prod in product_data:
                if prod['product'] == product:
                    prod['effectiveness'] = effectiveness
                    prod['invasiveness'] = invasiveness
                    prod['cost'] = cost
                    prod['usability'] = usability
                    break
            else:
                product_data.append({
                    'product': product,
                    'effectiveness': effectiveness,
                    'invasiveness': invasiveness,
                    'cost': cost,
                    'usability': usability
                })

        elif 'select_product' in request.form:
            selected_product_name = request.form['selected_product']
            for prod in product_data:
                if prod['product'] == selected_product_name:
                    selected_product = prod
                    break

        elif 'create_chart' in request.form:
            # バブルチャートのための選択された軸を取得
            x_axis = request.form['x_axis']
            y_axis = request.form['y_axis']
            bubble_size = request.form['bubble_size']

            # データ取得
            x = [float(prod[x_axis]) for prod in product_data]
            y = [float(prod[y_axis]) for prod in product_data]
            size = [float(prod[bubble_size]) for prod in product_data]
            labels = [prod['product'] for prod in product_data]

            # バブルチャート作成
            fig, ax = plt.subplots(figsize=(10, 10))
            scatter = ax.scatter(x, y, s=[s*1000 for s in size], alpha=0.3, color='green')
            ax.set_title('Bubble Chart')
            ax.set_xlabel(x_axis.capitalize())
            ax.set_ylabel(y_axis.capitalize())
            ax.set_xlim(0, 7)  # x軸の範囲を固定
            ax.set_ylim(0, 7)  # y軸の範囲を固定

            # プロダクト名を描画
            for i, label in enumerate(labels):
                ax.text(x[i], y[i], label, fontsize=12, ha='center')

            # 画像を保存しエンコード
            png_image = io.BytesIO()
            plt.savefig(png_image, format='png')
            plt.close(fig)  # メモリ節約のために図を閉じる
            png_image.seek(0)
            chart_data = base64.b64encode(png_image.getvalue()).decode()

        elif 'import_csv' in request.form:
            # CSVファイルの読み込み
            file = request.files['csv_file']
            if file:
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.DictReader(stream)
                product_data = []
                for row in csv_reader:
                    # データ型を適切に変換
                    product_data.append({
                        'product': row['product'],
                        'effectiveness': float(row['effectiveness']),
                        'invasiveness': float(row['invasiveness']),
                        'cost': float(row['cost']),
                        'usability': float(row['usability'])
                    })
                # インポート後に選択されたプロダクトをリセット
                selected_product = None

        elif 'export_csv' in request.form:
            # CSVファイルの出力
            csv_output = io.StringIO()
            fieldnames = ['product', 'effectiveness', 'invasiveness', 'cost', 'usability']
            writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(product_data)
            csv_output.seek(0)

            return send_file(
                io.BytesIO(csv_output.getvalue().encode('utf-8')),
                mimetype="text/csv",
                as_attachment=True,
                attachment_filename="product_data.csv"
            )

    return render_template(
        'index.html',
        product_data=product_data,
        selected_product=selected_product,
        chart_data=chart_data
    )

if __name__ == '__main__':
    app.run(debug=True)
