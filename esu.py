import base64
import sys
import time
from enum import Enum
from typing import Any

import pandas as pd
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

is_prod_api = (config["PROD_API"] or "0") != "0"  # TEST ortamı varsayılan
use_ssl_verification = (
    config["SSL_VERIFICATION"] or "1"
) != "0"  # SSL doğrulama varsayılan

use_test_company_tax_nr = (
    config["USE_TEST_COMPANY"] or "0"
) != "0"  # Gerçek vkn varsayılan

API_REGISTER_URL = (
    config["GIB_API_REGISTER_URL"]
    if is_prod_api
    else config["GIB_TEST_API_REGISTER_URL"]
) or ""
API_OWNERSHIP_URL = (
    config["GIB_API_OWNERSHIP_URL"]
    if is_prod_api
    else config["GIB_TEST_API_OWNERSHIP_URL"]
) or ""
API_USERNAME = config["GIB_API_USERNAME"] or ""
API_PASSWORD = config["GIB_API_PASSWORD"] or ""

COMPANY_TITLE = config["COMPANY_TITLE"]
COMPANY_EMRA_LICENSE_CODE = config["COMPANY_EMRA_LICENSE_CODE"]
COMPANY_TAX_NR = (
    config["COMPANY_TAX_NR"]
    if not use_test_company_tax_nr
    else config["GIB_TEST_TAX_NR"]
)

# use_ssl_verification `False` is uyarı mesajları gösterilmez
if not use_ssl_verification:
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning

    urllib3.disable_warnings(InsecureRequestWarning)


class RequestTypes(str, Enum):
    REGISTRATION = "REGISTRATION"
    OWNERSHIP = "OWNERSHIP"


def create_token(username: str, password: str) -> str:
    token = f"{username}:{password}".encode("utf-8")
    return base64.b64encode(token).decode("utf-8")


def api_request(
    data: Any, type: RequestTypes = RequestTypes.REGISTRATION
) -> requests.Response:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {create_token(API_USERNAME, API_PASSWORD)}",
    }
    url = API_REGISTER_URL if type == RequestTypes.REGISTRATION else API_OWNERSHIP_URL
    response = requests.post(
        url=url,
        headers=headers,
        json=data,
        verify=use_ssl_verification,
    )
    return response


def sleep(ms: float) -> None:
    time.sleep(ms / 1000)


def prepare_payload_for_registration_request(record: dict) -> Any:
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
    if "-" in date_str:
        return date_str
    day, month, year = date_str.split(".")
    return f"{year}-{month}-{day}"


def pad_with_zeroes(digits: Any) -> str:
    digits_str = str(int(digits))
    padded_str = digits_str.zfill(10)
    return padded_str


def prepare_payload_for_ownership_info_request(record: dict) -> Any:
    return {
        "firma_kodu": API_USERNAME,
        "durum_bilgileri": {
            "esu_seri_no": record["esu_seri_no"],
            "il_kodu": record["il_kodu"],
            "ilce": record["ilce"],
            "adres_numarası": "",
            "koordinat": "",
            "mukellef_vkn": (
                pad_with_zeroes(record["mukellef_vkn"])
                if record.get("mukellef_vkn")
                else COMPANY_TAX_NR
            ),
            "mukellef_unvan": (
                record["mukellef_unvan"]
                if record.get("mukellef_unvan")
                else COMPANY_TITLE
            ),
            "sertifika_no": (
                record["sertifika_no"] if record.get("sertifika_no") else ""
            ),
            "sertifika_tarihi": (
                convert_date_string(record["sertifika_tarihi"])
                if record.get("sertifika_tarihi")
                else ""
            ),
            "fatura_tarihi": (
                convert_date_string(record["fatura_tarihi"])
                if not record.get("mulkiyet_vkn") and record["fatura_tarihi"]
                else ""
            ),
            "fatura_ettn": (
                record["fatura_ettn"] if not record.get("mulkiyet_vkn") else ""
            ),
            "mulkiyet_sahibi_vkn_tckn": (
                pad_with_zeroes(record["mulkiyet_vkn"])
                if record.get("mulkiyet_vkn")
                else ""
            ),
            "mulkiyet_sahibi_ad_unvan": (
                record["mulkiyet_unvan"] if record.get("mulkiyet_unvan") else ""
            ),
        },
    }


def process_record(record: dict) -> None:
    response1 = api_request(prepare_payload_for_registration_request(record))
    print("Response 1:", response1.json())
    sleep(2000)
    rec = prepare_payload_for_ownership_info_request(record)
    print(rec)
    response2 = api_request(rec, RequestTypes.OWNERSHIP)
    print("Response 2:", response2.json())
    print("Requests made for record:", record["esu_seri_no"])


def process_csv(input_file_path: str, output_file_path: str) -> None:

    with open(output_file_path, "w") as f:
        sys.stdout = f

        column_names = ["il_kodu"]
        records = pd.read_csv(input_file_path, dtype={column_names[0]: str})
        records = records.fillna("")
        print("CSV file read")

        for _index, record in records.iterrows():
            process_record(dict(record))


if __name__ == "__main__":
    process_csv("./resources/data/esu_list.csv", "output.txt")
    sys.stdout = sys.__stdout__
    print("All records processed successfully")
