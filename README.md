## GİB EŞÜ EKS Servisi
<details open>

<summary>Cihaz Kayıt</summary>

```python
from models.api_models import ESU, ESUTipi, Soket, SoketTipi
from services.esu_service import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır
esu = ESU(
    esu_seri_no="7001324500027",
    esu_soket_tipi=ESUTipi.AC_DC,
    esu_soket_sayisi="2",
    esu_soket_detay=[
        Soket(soket_no="Soket1", soket_tip=SoketTipi.AC),
        Soket(soket_no="Soket2", soket_tip=SoketTipi.DC),
    ],
    esu_markasi="Vestel",
    esu_modeli="EVC04",
)

yanit = servis.cihaz_kayit(esu)

print(yanit.durum)  # "success"
print(yanit.sonuc[0].mesaj)  # "Basarili"
print(yanit.sonuc[0].kod)  # "1000"
print(yanit.sonuc[0].esu_seri_no)  # "7001324500027"
```

</details>
<details>

<summary>Mükellef Kayıt</summary>

```python
from models.api_models import Fatura, Lokasyon, Mukellef
from services.esu_service import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

seri_no = "7001324500027"

lokasyon = Lokasyon(
    il_kodu="034",
    ilce="Sarıyer",
    adres_numarası="2324516851",
    koordinat="41°11'20.7528\"N, 29°2'51.0756\"E",
)

fatura = Fatura(fatura_tarihi="2024-11-29", fatura_ettn="G212024000000049")

mukellef = Mukellef(
    mukellef_vkn="1234567890", mukellef_unvan="Yeşilçam Enerji Anonim Şirketi"
)

yanit = servis.mukellef_kayit(
    esu=seri_no, lokasyon=lokasyon, fatura=fatura, mukellef=mukellef
)

print(yanit.durum)  # "success"
print(yanit.sonuc[0].mesaj)  # "Basarili"
print(yanit.sonuc[0].kod)  # "1000"
print(yanit.sonuc[0].esu_seri_no)  # "7001324500027"
```

</details>

<details>

<summary>Toplu Kayıt</summary>

```python
from time import time

from services.esu_service import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

baslangic = time()

sonuc = servis.toplu_kayit(
    giris_dosya_yolu="input.csv",  # varsayılan "envanter.csv"
    dosyaya_yaz=True,  # varsayılan False
    cikti_dosya_yolu="output.json",  # varsayılan "gonderim_raporu.json"
    paralel_calistir=True,  # varsayılan False
)

bitis = time()

print(sonuc)

sure = bitis - baslangic
print(f"Süre: {sure:.2f} saniye")
```
</details>

<details>

<summary>Kayıt Güncelleme</summary>

```python
from models.api_models import Fatura, Lokasyon, Sertifika
from services.esu_service import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

seri_no = "7001324500027"

lokasyon = Lokasyon(
    il_kodu="034",
    ilce="Sarıyer",
    adres_numarası="2324516851",
    koordinat="41°11'20.7528\"N, 29°2'51.0756\"E",
)

fatura = Fatura(fatura_tarihi="2024-11-29", fatura_ettn="G212024000000049")

sertifika = Sertifika(sertifika_no="SE2024013000012", sertifika_tarihi="2024-01-30")

yanit = servis.kayit_guncelle(
    esu_seri_no=seri_no,
    lokasyon=lokasyon,
    fatura=fatura,
    sertifika=sertifika,
)

print(yanit.durum)  # "success"
print(yanit.sonuc[0].mesaj)  # "Basarili"
print(yanit.sonuc[0].kod)  # "1000"
print(yanit.sonuc[0].esu_seri_no)  # "7001324500027"
```

</details>

<details>

<summary>Toplu Kayıt Güncelleme</summary>

```python
from time import time

from services.esu_service import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

baslangic = time()

sonuc = servis.toplu_guncelle(
    giris_dosya_yolu="input.csv",  # varsayılan "envanter.csv"
    dosyaya_yaz=True,  # varsayılan False
    cikti_dosya_yolu="output.json",  # varsayılan "gonderim_raporu.json"
    paralel_calistir=True,  # varsayılan False
)

bitis = time()

print(sonuc)

sure = bitis - baslangic
print(f"Süre: {sure:.2f} saniye")
```

</details>
<details>

<summary>Cihaz Kapatma</summary>

```python
from services.esu_service import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

seri_no = "7001324500027"

yanit = servis.cihaz_kapatma(esu_seri_no=seri_no)

print(yanit.durum)  # "success"
print(yanit.sonuc[0].mesaj)  # "Basarili"
print(yanit.sonuc[0].kod)  # "1000"
print(yanit.sonuc[0].esu_seri_no)  # "7001324500027"
```

</details>
<br>

 [Dokümantasyon](doc.md)
<br>
<br>
&copy;Electroop, 2024
