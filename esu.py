import asyncio
import base64
import os
import time
from typing import Any

import pandas as pd
import requests  # type: ignore
from dotenv import load_dotenv

load_dotenv()

API_USERNAME = str(os.getenv("API_USERNAME"))
API_PASSWORD = str(os.getenv("API_PASSWORD"))
API_REGISTER_URL = str(os.getenv("API_REGISTER_URL"))
API_OWNERSHIP_URL = str(os.getenv("API_OWNERSHIP_URL"))
COMPANY_TITLE = str(os.getenv("COMPANY_TITLE"))
COMPANY_EMRA_LICENSE_CODE = str(os.getenv("COMPANY_EMRA_LICENSE_CODE"))
COMPANY_TAX_NR = str(os.getenv("COMPANY_TAX_NR"))


def create_token(username: str, password: str) -> str:
    token = f"{username}:{password}".encode("utf-8")
    return base64.b64encode(token).decode("utf-8")


async def api_request_1(data: Any) -> requests.Response:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {create_token(API_USERNAME, API_PASSWORD)}",
    }
    response = requests.post(API_REGISTER_URL, headers=headers, json=data, verify=False)
    return response


async def api_request_2(data: Any) -> requests.Response:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {create_token(API_USERNAME, API_PASSWORD)}",
    }
    response = requests.post(
        API_OWNERSHIP_URL, headers=headers, json=data, verify=False
    )
    return response


def sleep(ms: float) -> None:
    time.sleep(ms / 1000)


def prepare_record_for_request_1(record: dict) -> Any:
    soket_detay = [
        {"soket_no": pair.split(":")[0], "soket_tip": pair.split(":")[1]}
        for pair in record["esu_soket_detay"].split(";")
    ]

    return {
        "firma_kodu": API_USERNAME,
        "firma_vkn": COMPANY_TAX_NR,
        "epdk_lisans_no": COMPANY_EMRA_LICENSE_CODE,
        "kayit_bilgisi": {
            "esu_seri_no": record["esu_seri_no"],
            "esu_soket_tipi": record["esu_soket_tipi"],
            "esu_soket_sayisi": record["esu_soket_sayisi"],
            "esu_soket_detay": soket_detay,
            "esu_markasi": record["esu_markasi"],
            "esu_modeli": record["esu_modeli"],
        },
    }


def convert_date_string(date_str: str) -> str:
    day, month, year = date_str.split(".")
    return f"{year}-{month}-{day}"


def prepare_record_for_request_2(record: dict) -> Any:
    return {
        "firma_kodu": API_USERNAME,
        "durum_bilgileri": {
            "esu_seri_no": record["esu_seri_no"],
            "il_kodu": record["il_kodu"],
            "ilce": record["ilce"],
            "adres_numarası": "",
            "koordinat": "",
            "mukellef_vkn": COMPANY_TAX_NR,
            "mukellef_unvan": COMPANY_TITLE,
            "sertifika_no": "",
            "sertifika_tarihi": "",
            "fatura_tarihi": convert_date_string(record["fatura_tarihi"]),
            "fatura_ettn": record["fatura_ettn"],
            "mulkiyet_sahibi_vkn_tckn": "",
            "mulkiyet_sahibi_ad_unvan": "",
        },
    }


async def process_record(record: dict) -> None:
    response1 = await api_request_1(prepare_record_for_request_1(record))
    print("Response from Request 1:", response1.json())
    sleep(2000)  # Keeping the sleep function synchronous
    response2 = await api_request_2(prepare_record_for_request_2(record))
    print("Response from Request 2:", response2.json())
    print("Both requests succeeded for record:", record["esu_seri_no"])


async def process_csv(file_path: str) -> None:
    column_names = ["il_kodu"]
    records = pd.read_csv(file_path, dtype={column_names[0]: str})
    print("CSV file read")

    for index, record in records.iterrows():
        await process_record(record)  # type: ignore
    print("All done")


if __name__ == "__main__":
    asyncio.run(process_csv("./resources/data/esu_list.csv"))
    print("All records processed successfully")
