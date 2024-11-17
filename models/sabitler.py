# string constants

from pydantic import BaseModel, ConfigDict

F_DURUM_BILGILERI = "durum_bilgileri"
F_ESU_SERI_NO = "esu_seri_no"
F_FATURA_ETTN = "fatura_ettn"
F_FATURA_TARIHI = "fatura_tarihi"
F_FIRMA_KODU = "firma_kodu"
F_GUNCELLEME_BILGILERI = "guncelleme_istek_bilgileri"
F_IL_KODU = "il_kodu"
F_ILCE = "ilce"
F_KAYIT_BILGISI = "kayit_bilgisi"
F_MARKA = "esu_markasi"
F_MODEL = "esu_modeli"
F_MUKELLEF_UNVAN = "mukellef_unvan"
F_MUKELLEF_VKN = "mukellef_vkn"
F_SAHIP_AD_UNVAN = "mulkiyet_sahibi_ad_unvan"
F_SAHIP_VKN_TCKN = "mulkiyet_sahibi_vkn_tckn"
F_SERTIFIKA_NO = "sertifika_no"
F_SERTIFIKA_TARIHI = "sertifika_tarihi"
F_SOKET_DETAY = "esu_soket_detay"
F_SOKET_SAYISI = "esu_soket_sayisi"
F_SOKET_TIPI = "esu_soket_tipi"

STR_AC = "AC"
STR_AC_DC = "AC/DC"
STR_DC = "DC"
STR_BOS = ""
STR_BIR = "1"
STR_SIFIR = "0"
STR_TARIH_FORMATI = "YYYY-MM-DD"
STR_API_BASARI = "success"
STR_API_HATA = "basarisiz"

# numerical constants

MIN_MARKA = MIN_MODEL = 1
MIN_LEN_ILCE = MIN_LEN_MUKELLEF_UNVAN = 2
MIN_FIRMA_KODU = MIN_SERI_NO = MIN_FIRMA_UNVAN = LEN_IL_KODU = MIN_LEN_FATURA_ETTN = 3
LEN_KOD = 4
MIN_SIFRE = 6
LEN_VKN = 10
LEN_VKN_TCKN = [10, 11]

# regex expressions

REGEX_API_KOD = r"^\d{4}$"
REGEX_EPDK_LISANS_KODU = r"^ŞH/?\d{5}-\d+/\d{5}$"
REGEX_FIRMA_VKN = rf"\b\d{{{LEN_VKN}}}\b"
REGEX_IL_KODU = rf"\b\d{{{LEN_IL_KODU}}}\b"
REGEX_MULKIYET_SAHIBI_VKN_TCKN = rf"\b\d{{{','.join(map(str, LEN_VKN_TCKN))}}}\b"
REGEX_SOKET_SAYISI = r"^\d+$"
REGEX_SOKET_NO = r"^Soket\d+$"
REGEX_TARIH = r"^\d{4}-\d{2}-\d{2}$"  # YYYY-MM-DD

# error messages

ERROR_FATURA = (
    f"{F_FATURA_TARIHI} ve {F_FATURA_ETTN} tutarsız; "
    "ikisi de boş veya ikisi de dolu olmalı"
)
ERROR_FATURA_ETTN = (
    f"{F_FATURA_ETTN} en az " f"{MIN_LEN_FATURA_ETTN} karakter uzunluğunda olmalı"
)
ERROR_FATURA_TARIHI = f"{F_FATURA_TARIHI} {STR_TARIH_FORMATI} formatında olmalıdır"
ERROR_KAYIT_BILGILERI_EKSIK = "Kayıt bilgileri eksik"
ERROR_MUKELLEF_EKSIK = "Mükellef bilgileri eksik"
ERROR_MUKELLEF_UNVAN = (
    f"{F_MUKELLEF_UNVAN} en az " f"{MIN_LEN_MUKELLEF_UNVAN} karakter uzunluğunda olmalı"
)
ERROR_MUKELLEF_VKN = f"{F_MUKELLEF_VKN} {LEN_VKN} karakter uzunluğunda olmalı"
ERROR_MULKİYET = (
    f"{F_SAHIP_VKN_TCKN} ve {F_SAHIP_AD_UNVAN} tutarsız; "
    "ikisi de boş veya ikisi de dolu olmalı"
)
ERROR_MULKIYET_SAHIBI_AD_UNVAN = (
    f"{F_SAHIP_AD_UNVAN} en az " f"{MIN_LEN_MUKELLEF_UNVAN} karakter uzunluğunda olmalı"
)
ERROR_MULKIYET_SAHIBI_VKN_TCKN = (
    f"{F_SAHIP_VKN_TCKN} "
    f"{' veya '.join(map(str, LEN_VKN_TCKN))} karakter uzunluğunda olmalı"
)
ERROR_SERTIFIKA = (
    f"{F_SERTIFIKA_NO} ve {F_SERTIFIKA_TARIHI} tutarsız; "
    "ikisi de boş veya ikisi de dolu olmalı"
)
ERROR_SERTIFIKA_TARIHI = (
    f"{F_SERTIFIKA_TARIHI} {STR_TARIH_FORMATI} formatında olmalıdır"
)
ERROR_SERTIFIKA_VE_MULKIYET = (
    "sertifika bilgilerini gönderebilmek için " f"{F_SAHIP_VKN_TCKN} doldurulmalıdır"
)
ERROR_SOKET_DETAY_TIP = f"soket detayları {F_SOKET_TIPI} ile uyumlu değil"
ERROR_SOKET_DETAY_UZUNLUK = f"{F_SOKET_SAYISI} kadar soket detayı sağlanmalı"
ERROR_SOKET_DETAY_ACDC = f"{F_SOKET_TIPI} [AC/DC] soket detayları ile uyumlu değil"
ERROR_YA_FATURA_YA_MULKIYET = (
    f"{F_FATURA_ETTN} veya {F_SAHIP_VKN_TCKN} "
    "alanlarından biri ve yalnız biri mevcut olmalıdır"
)

# custom base model


class CustomBaseModel(BaseModel):
    # ignore extra fields
    model_config = ConfigDict(extra="ignore")
