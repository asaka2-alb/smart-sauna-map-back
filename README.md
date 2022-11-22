# smart-sauna-map

このアプリはバックエンドにサウナ検索サーバー (Sauna search server) を設置し、そこに地名などを問い合わせることで周辺のサウナ情報を取得します。

## Requirement

本プロジェクトは以下の環境を前提をしております。

- Python: 3.9

## 開発環境の構築方法

以下は開発時のサーバーの立て方です。

1. 本リポジトリをクローンします。

    ```console
    git clone git@github.com:asaka2-alb/smart-sauna-map-back.git
    ```

2. terminal window 上で smart-sauna-map-back ディレクトリに移動します。

    ```console
    cd smart-sauna-map-back
    ```

3. [Poetry](https://github.com/python-poetry/poetry) の仮想環境を立ち上げます。

    ```console
    poetry shell
    ```

4. [Poetry](https://github.com/python-poetry/poetry) を使って動作に必要なパッケージをインストールします。

    ```console
    poetry install
    ```

## Backend server の立て方

以下のコマンドを実行して、開発用 Python サーバーを立ち上げます。

```console
python app.py
```

## テストの実行方法

テストを実行するには、本リポジトリ直下のディレクトリで以下のコマンドを実行してください。

```console
pytest
```

## デプロイ

### デプロイのための準備

以下のコマンドを実行して `poetry.lock` ファイルに記載されている依存パッケージを `requirements.txt` に出力します。この `requirements.txt` は後のデプロイプロセスにおいて必要となるため `git` の管理下に置いて下さい。

```console
poetry export -f requirements.txt --output requirements.txt
```

### デプロイの手順

本レポジトリは [Render](https://render.com/) を用いてデプロイを実行しています。開発用ブランチを `main` ブランチにマージすると、`main` ブランチから自動的にデプロイが実行されます。

## 以前の作品

`https://github.com/siida36/spa-boot-camp`
