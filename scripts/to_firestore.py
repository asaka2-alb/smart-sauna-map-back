# -*- coding: utf-8 -*-
from __future__ import annotations

import dataclasses
import time

import firebase_admin
from firebase_admin import credentials, firestore

from smart_sauna_map.search_sauna import search_sauna

SECRET = "../secrets/smart-sauna-map-firebase-adminsdk-kwl6u-5067562322.json"

if __name__ == "__main__":

    # Firestore の初期化
    firebase_admin.initialize_app(credentials.Certificate(SECRET))
    db = firestore.client()

    page_indexes = range(0, 560)
    for page_index in page_indexes:
        # batch の取得
        batch = db.batch()

        # sauna の取得
        saunas = search_sauna("", prefecture="", page_index=page_index)
        print(saunas)
        time.sleep(10)

        for sauna in saunas:
            # sauna の辞書化
            sauna = dataclasses.asdict(sauna)

            # sauna document reference の取得
            sauna_ref = db.collection("saunas").document(str(sauna["sauna_id"]))

            # sauna の batch への書き込み
            batch.set(sauna_ref, sauna)

        # batch の commit
        batch.commit()
