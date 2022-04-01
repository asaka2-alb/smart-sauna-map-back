# smart-sauna-map

## 開発環境の構築方法

### Frontend 開発用 server の立て方

1. terminal window 上で front/smart-sauna-map ディレクトリに移動します。

    ```shell
    cd front/smart-sauna-map
    ```

1. 以下のコマンドを実行してフロントエンド用のパッケージをインストールします。

    ```shell
    yarn install --immutable --immutable-cache --check-cache
    ```

1. 以下のコマンドを実行してフロントエンド用のサーバーを立ち上げます。

    ```shell
    yarn start
    ```

### Backend server の立て方

このアプリはバックエンドにサウナ検索サーバー (Sauna search server) を設置し、そこに地名などを問い合わせることで周辺のサウナ情報を取得します。
以下は開発時のサーバーの立て方です。プロダクション時には別途方法を示します。

1. フロントエンドとは別の terminal window で server ディレクトリに移動します。

    ```shell
    cd server
    ```

1. poetry を使って動作に必要なパッケージをインストールします。

    ```shell
    poetry install
    ```

1. poetry の仮想環境を立ち上げます。

    ```shell
    poetry shell
    ```

1. 開発用 Python サーバーを立ち上げます。

    ```shell
    python src/smart_sauna_map/server.py
    ```

## 以前の作品

https://github.com/siida36/spa-boot-camp
