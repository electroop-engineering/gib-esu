# gib_esu

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gib-esu) ![PyPI - Downloads](https://img.shields.io/pypi/dm/gib_esu) ![Build Status](https://github.com/electroop-engineering/gib-esu/actions/workflows/publish.yml/badge.svg) [![Tests Status](https://electroop-engineering.github.io/gib-esu/reports/junit/tests-badge.svg?v=108)](https://electroop-engineering.github.io/gib-esu/reports/junit/report.html) [![Coverage Status](https://electroop-engineering.github.io/gib-esu/reports/coverage/coverage-badge.svg?v=108)](https://electroop-engineering.github.io/gib-esu/reports/coverage/index.html) [![Flake8 Status](https://electroop-engineering.github.io/gib-esu/reports/flake8/flake8-badge.svg?v=108)](https://electroop-engineering.github.io/gib-esu/reports/flake8/index.html) ![GitHub Repo stars](https://img.shields.io/github/stars/electroop-engineering/gib-esu) ![PyPI - Version](https://img.shields.io/pypi/v/gib_esu) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Amaç ve Kapsam

[Electroop](https://electroop.io) tarafından sağlanan açık kaynak kodlu *gib_esu* Python kütüphanesi ile Gelir İdaresi Başkanlığı'nın EŞÜ (Elektrikli Şarj Ünitesi) EKS (Elektronik Kayıt Sistemi) servisi üzerinden yapılan cihaz kayıt, mükellef bilgi/durum kaydetme/güncelleme, cihaz kapatma ve cihaz devir işlemleri gerçekleştirilebilir.

## Gerekli Python Sürümü

Python >= 3.8
(Çok çekirdekli işlemcilerle yazılım daha iyi performans gösterir.)

## Kurulum

```bash
pip install gib_esu
```

## Kullanım

_EsuServis_, kütüphanenin GİB EŞÜ EKS servisine istekler göndermekte kullanılan temel sınıfıdır.
Servis, çalışma parametrelerini projenin kök dizininde bulunan _.env_ dosyasından okur. Örnek bir .env dosyası içeriği aşağıda (ve ayrıca projenin GitHub reposundaki sample.env dosyası içinde) sunulmuştur.

### Örnek .env dosyası

```ini
###### ERİŞİM BİLGİLERİ - DEĞİŞTİRİLMELİ!! ######
GIB_FIRMA_KODU=J000
GIB_API_SIFRE=Abc123

###### ŞİRKET BİLGİLERİ - DEĞİŞTİRİLMELİ!! ######
FIRMA_UNVAN=ENERJİ ANONİM ŞİRKETİ
EPDK_LISANS_KODU=ŞH/12345-6/00789
FIRMA_VKN=1234567890

###### İSTEK PARAMETRELERİ - SEÇİLMELİ!! ######
PROD_API=1 # Test API kullanılacaksa PROD_API=0
SSL_DOGRULAMA=1 # SSL Doğrulama kullanılmayacaksa SSL_DOGRULAMA=0 (Canlı ortamda önerilmez)
TEST_FIRMA_KULLAN=0 #TEST_FIRMA_KULLAN=1 ise şirket VKN yerine 3900383669 (GİB test VKN) gönderilir

###### TEST VKN - GİB DEĞİŞTİRMEDİKÇE DEGİŞTİRİLMEMELİ ######
GIB_TEST_FIRMA_VKN=3900383669
```

## Servis Metotları
Elektrikli şarj ünitesinin (EŞÜ) kaydı, _ESUServis_ sınıfının *cihaz_kayit* metodu ile, ünitenin mükellef bilgisinin/durumunun GİB'e bildirimi ise yine aynı servis sınıfının *mukellef_kayit* metodu ile yapılmaktadır.

Bir EŞÜ'nün GİB EŞÜ EKS kaydının tamamlanmış olması için önce _cihaz_kayit_ metodu ile cihaz kaydının, ardından da _mukellef_kayit_ metodu ile mükellef kaydının gerçekleştirilmiş olması gerekmektedir.

Şarj ünitesi envanterlerini GİB'e ilk kez kaydettirecek olan şarj ağı işletmecileri, sisteme genellikle onlarca, hatta yüzlerce ünitenin bilgisini yüklemek durumunda kalmaktadırlar. Bu ihtiyacı karşılamak ve toplu envanter gönderimini kolaylaştırmak amacıyla servis sınıfına, paralel ya da ardışık modda çalıştırılabilen *toplu_kayit* metodu eklenmiştir. Toplu kayıt metodunun gerektirdiği .csv veri deseni, projenin GitHub sayfasındaki [örnek .csv dosyası](https://github.com/electroop-engineering/gib-esu/blob/main/sample.envanter.csv) içinde verilmiştir. Toplu gönderim sonuçları, isteğe bağlı olarak, json formatındaki bir dosyaya yazdırılarak raporlanabilir.

Not: Csv formatındaki giriş metin dosyasında _mukellef_vkn_ ve _mukellef_unvan_ alanları boş bırakılmış ise program, bu alanlar için .env dosyası içinde verilen _FIRMA_VKN_ ve FIRMA_UNVAN bilgilerini kullanır. GİB'in ilgili kılavuzlarında belirtilmiş olduğu üzere, _adres_no_, _koordinat_, _sertifika_no_, _sertifika_tarihi_  alanları boş bırakılabilir. Fatura ve mükellef bilgileri ile mülkiyet sahibi bilgileri birbirini dışlamak durumundadır. Diğer bir deyişle, _mukellef_vkn_ ile _mulkiyet_sahibi_vkn_tckn_ bilgileri aynı istekte dolu olarak gönderilemezler. Öte yandan, _mukellef_vkn_ verili ise _fatura_tarihi_ ve _fatura_ettn_ alanları da boş bırakılamaz. GİB EŞÜ servisinde tarih bilgilerinin tümünün YYYY-MM-DD (Örneğin 2024-11-28) biçiminde olması beklenmektedir. _gib_esu_ kütüphanesini kullandığınızda GİB tarafından belirlenmiş olan bu tür mantıksal ve biçimsel kurallar her isteğe ayrı ayrı uygulanarak istekler gönderimden önce doğrulanır. Şayet istek, mantık veya biçim bakımından hatalı ise, program, hata üreterek sorunlu isteklerin GİB'e gönderilmesinin önüne geçer.

Daha önce gönderilmiş cihaz ve/veya mükellef bilgilerinin yanlışlık ya da değişiklik nedeniyle güncellenmesi gerektiğinde _ESUServis_ sınıfının *kayit_guncelle* veya *toplu_guncelle* metotları kullanılabilir. Toplu güncelleme amacıyla kullanılacak olan .csv dosyasının veri deseni, toplu kayıt için yukarıda verilen dosyanınki ile aynıdır. GİB'in, EPDK Lisans No ve EŞÜ Seri No gibi bazı temel bilgilerin güncellenmesine izin vermediği bilinerek gönderimlerde bu hususa dikkat edilmelidir.

Mükellef tarafından devir ya da başka bir gerekçe ile artık kullanılmayacağı için envanterden çıkarılmak istenen şarj üniteleri, _ESUServis_ sınıfının *cihaz_kapatma* metodu ile GİB'e bildirilebilirler. Cihazın başka bir mükellefe devri durumunda *cihaz_kapatma* işleminin ardından *mukellef_kayit* metoduyla cihazın yeni mükellefinin bilgileri GİB'e temin edilmelidir.

EŞÜ EKS servisi ile ilgili açıklamalar, GİB'in yayımladığı ilgili teknik kılavuzlarda ve servisin kullanım kılavuzunda mevcuttur. Servise getirilen yenilikler ve yapılan değişiklikler nedeniyle sürümleri GİB tarafından zaman zaman güncellenen bu kılavuzların dikkatle takip edilmesi gerekir.

## İstek Örnekleri

<details open>

<summary>Cihaz Kayıt</summary>

```python
from gib_esu.models import ESU, ESUTipi, Soket, SoketTipi
from gib_esu.services import ESUServis

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
from gib_esu.models import Fatura, Lokasyon, Mukellef
from gib_esu.services import ESUServis

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

from gib_esu.services import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

baslangic = time()

sonuc = servis.toplu_kayit(
    giris_dosya_yolu="input.csv",  # varsayılan "envanter.csv"
    dosyaya_yaz=True,  # varsayılan False
    cikti_dosya_yolu="output.json",  # varsayılan "gonderim_raporu.json"
    paralel_calistir=True,  # varsayılan False
    istekleri_logla=True,  # varsayılan False
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
from gib_esu.models import Fatura, Lokasyon, Sertifika
from gib_esu.services import ESUServis

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

from gib_esu.services import ESUServis

servis = ESUServis()  # konfigürasyonda .env dosyası kullanılır

baslangic = time()

sonuc = servis.toplu_guncelle(
    giris_dosya_yolu="input.csv",  # varsayılan "envanter.csv"
    dosyaya_yaz=True,  # varsayılan False
    cikti_dosya_yolu="output.json",  # varsayılan "gonderim_raporu.json"
    paralel_calistir=True,  # varsayılan False
    istekleri_logla=True,  # varsayılan False
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
from gib_esu.services import ESUServis

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


## Kod Dokümantasyonu
Kod dokümantasyonuna [buradan](https://github.com/electroop-engineering/gib-esu/blob/main/doc.md) ulaşılabilir.
<br>
<br>
&copy;Electroop, 2024
