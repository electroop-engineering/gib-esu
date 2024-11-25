<a id="response_models"></a>

# response\_models

<a id="response_models.Durum"></a>

## Durum Objects

```python
class Durum(str, Enum)
```

Enum for API response status codes.

<a id="response_models.Sonuc"></a>

## Sonuc Objects

```python
class Sonuc(CustomBaseModel)
```

Api result model.

<a id="response_models.Yanit"></a>

## Yanit Objects

```python
class Yanit(CustomBaseModel)
```

Api response model.

<a id="__init__"></a>

# \_\_init\_\_

<a id="request_models"></a>

# request\_models

<a id="request_models.RegEx__Tarih"></a>

#### RegEx\_\_Tarih

YYYY-MM-DD

<a id="request_models.T"></a>

#### T

Type definition of a non-empty string.

<a id="request_models.NonEmptyString"></a>

#### NonEmptyString

Type definition of a non-empty list.

<a id="request_models.NonEmptyList"></a>

#### NonEmptyList

Type definition for required tax numbers.

<a id="request_models.TaxNumber"></a>

#### TaxNumber

Type definition for optional tax numbers.

<a id="request_models.TaxNumberOrEmpty"></a>

#### TaxNumberOrEmpty

Type definition for city code.

<a id="request_models.SoketTipi"></a>

## SoketTipi Objects

```python
class SoketTipi(str, Enum)
```

Socket type enum.

<a id="request_models.ESUTipi"></a>

## ESUTipi Objects

```python
class ESUTipi(str, Enum)
```

Charge point type enum.

<a id="request_models.Soket"></a>

## Soket Objects

```python
class Soket(CustomBaseModel)
```

Charge point's connectors.

<a id="request_models.Soket.soket_no"></a>

#### soket\_no

Soket1, Soket2, Soket3, etc.

<a id="request_models.ESUSeriNo"></a>

## ESUSeriNo Objects

```python
class ESUSeriNo(CustomBaseModel)
```

Charge point's serial number.

<a id="request_models.ESU"></a>

## ESU Objects

```python
class ESU(ESUSeriNo)
```

Charge point model.

<a id="request_models.ESU.esu_soket_sayisi"></a>

#### esu\_soket\_sayisi

"1", "2", "3", etc.

<a id="request_models.FirmaKodu"></a>

## FirmaKodu Objects

```python
class FirmaKodu(CustomBaseModel)
```

Company code model.

<a id="request_models.Firma"></a>

## Firma Objects

```python
class Firma(FirmaKodu)
```

Company info model.

<a id="request_models.Lokasyon"></a>

## Lokasyon Objects

```python
class Lokasyon(CustomBaseModel)
```

EV charging location model.

<a id="request_models.Mukellef"></a>

## Mukellef Objects

```python
class Mukellef(CustomBaseModel)
```

Tax payer model.

<a id="request_models.Sertifika"></a>

## Sertifika Objects

```python
class Sertifika(CustomBaseModel)
```

Certificate model.

<a id="request_models.Fatura"></a>

## Fatura Objects

```python
class Fatura(CustomBaseModel)
```

Invoice model.

<a id="request_models.MulkiyetSahibi"></a>

## MulkiyetSahibi Objects

```python
class MulkiyetSahibi(CustomBaseModel)
```

Charge point owner model.

<a id="request_models.ESUMukellefBilgisi"></a>

## ESUMukellefBilgisi Objects

```python
class ESUMukellefBilgisi(ESUSeriNo, Fatura, Lokasyon, Mukellef, MulkiyetSahibi,
                         Sertifika)
```

Intermediary model that encapsulates charge point and tax payer information.

<a id="request_models.ESUGuncellemeBilgisi"></a>

## ESUGuncellemeBilgisi Objects

```python
class ESUGuncellemeBilgisi(ESUSeriNo, Fatura, Lokasyon, MulkiyetSahibi,
                           Sertifika)
```

Intermediary model that encapsulates charge point and ownership information.

<a id="request_models.CustomBaseModelWithValidator"></a>

## CustomBaseModelWithValidator Objects

```python
class CustomBaseModelWithValidator(CustomBaseModel)
```

Custom base model with a predefined model validator function.

<a id="request_models.ESUKayitModel"></a>

## ESUKayitModel Objects

```python
class ESUKayitModel(Firma)
```

Charge point registration request model.

<a id="request_models.ESUKayitModel.olustur"></a>

#### olustur

```python
@classmethod
def olustur(cls, firma: Firma, esu: ESU) -> ESUKayitModel
```

Constructs a ESUKayitModel from given `esu` and `firma` arguments.

**Arguments**:

- `firma` _Firma_ - Company information
- `esu` _ESU_ - Charge point information


**Returns**:

- `ESUKayitModel` - Constructed model instance

<a id="request_models.ESUKapatmaModel"></a>

## ESUKapatmaModel Objects

```python
class ESUKapatmaModel(CustomBaseModel)
```

Charge point delisting request model.

<a id="request_models.ESUMukellefModel"></a>

## ESUMukellefModel Objects

```python
class ESUMukellefModel(CustomBaseModelWithValidator, FirmaKodu)
```

Charge point tax payer info registration model.

<a id="request_models.ESUMukellefModel.olustur"></a>

#### olustur

```python
@classmethod
def olustur(cls,
            esu_seri_no: str,
            firma_kodu: str,
            fatura: Fatura,
            lokasyon: Lokasyon,
            mukellef: Mukellef,
            mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
            sertifika: Optional[Sertifika] = None) -> ESUMukellefModel
```

Constructs a ESUMukellefModel from given arguments.

**Arguments**:

- `esu_seri_no` _str_ - Charge point serial number
- `firma_kodu` _str_ - Company code
- `fatura` _Fatura_ - Invoice information
- `lokasyon` _Lokasyon_ - Location information
- `mukellef` _Mukellef_ - Tax payer information
  mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
  Ownership information. Defaults to None.
- `sertifika` _Optional[Sertifika], optional_ - Certificate. Defaults to None.


**Returns**:

- `ESUMukellefModel` - Constructed model instance

<a id="request_models.ESUGuncellemeModel"></a>

## ESUGuncellemeModel Objects

```python
class ESUGuncellemeModel(CustomBaseModelWithValidator, FirmaKodu)
```

Charge point update request model.

<a id="request_models.ESUGuncellemeModel.olustur"></a>

#### olustur

```python
@classmethod
def olustur(cls,
            esu_seri_no: ESUSeriNo,
            firma_kodu: str,
            fatura: Fatura,
            lokasyon: Lokasyon,
            mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
            sertifika: Optional[Sertifika] = None) -> ESUGuncellemeModel
```

Constructs a ESUGuncellemeModel from given arguments.

**Arguments**:

- `esu_seri_no` _str_ - Charge point serial number
- `firma_kodu` _str_ - Company code
- `fatura` _Fatura_ - Invoice information
- `lokasyon` _Lokasyon_ - Location information
  mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
  Ownership information. Defaults to None.
- `sertifika` _Optional[Sertifika], optional_ - Certificate. Defaults to None.


**Returns**:

- `ESUGuncellemeModel` - Constructed model instance

<a id="base_model"></a>

# base\_model

<a id="base_model.CustomBaseModel"></a>

## CustomBaseModel Objects

```python
class CustomBaseModel(BaseModel)
```

Custom base model that ignores extra fields.

<a id="service_models"></a>

# service\_models

<a id="service_models.EvetVeyaHayir"></a>

## EvetVeyaHayir Objects

```python
class EvetVeyaHayir(str, Enum)
```

Enum for boolean config parameters.

<a id="service_models.APIParametreleri"></a>

## APIParametreleri Objects

```python
class APIParametreleri(CustomBaseModel)
```

Service model for API parameters.

<a id="service_models.ESUServisKonfigurasyonu"></a>

## ESUServisKonfigurasyonu Objects

```python
class ESUServisKonfigurasyonu(CustomBaseModel)
```

Service configuration model.

<a id="service_models.ESUKayitSonucu"></a>

## ESUKayitSonucu Objects

```python
class ESUKayitSonucu(CustomBaseModel)
```

Charge point registration output model.

<a id="service_models.MukellefKayitSonucu"></a>

## MukellefKayitSonucu Objects

```python
class MukellefKayitSonucu(CustomBaseModel)
```

Charge point tax payer registration model.

<a id="service_models.ESUTopluKayitSonucu"></a>

## ESUTopluKayitSonucu Objects

```python
class ESUTopluKayitSonucu(ESUSeriNo, ESUKayitSonucu, MukellefKayitSonucu)
```

Batch registration output model for single charge point.

<a id="service_models.TopluKayitSonuc"></a>

## TopluKayitSonuc Objects

```python
class TopluKayitSonuc(CustomBaseModel)
```

Charge point batch registration output model.

<a id="service_models.ESUTopluGuncellemeSonucu"></a>

## ESUTopluGuncellemeSonucu Objects

```python
class ESUTopluGuncellemeSonucu(ESUSeriNo)
```

Batch update output model for single charge point.

<a id="service_models.TopluGuncellemeSonuc"></a>

## TopluGuncellemeSonuc Objects

```python
class TopluGuncellemeSonuc(CustomBaseModel)
```

Charge point batch update output model.

<a id="__init__"></a>

# \_\_init\_\_

<a id="esu_service"></a>

# esu\_service

<a id="esu_service.ESUServis"></a>

## ESUServis Objects

```python
class ESUServis()
```

Class that handles GIB ESU EKS service operations.

<a id="esu_service.ESUServis.__init__"></a>

#### \_\_init\_\_

```python
def __init__(_config: Optional[Dict[str, str | None]] = None) -> None
```

ESUServis constructor.

**Arguments**:

  _config (Optional[Dict[str, str  |  None]], optional):
  Dictionary or env file path to read the config from. Defaults to None.

<a id="esu_service.ESUServis.cihaz_kayit"></a>

#### cihaz\_kayit

```python
def cihaz_kayit(cihaz_bilgileri: Union[ESUKayitModel, ESU]) -> Yanit
```

Registers a charge point with the GIB ESU EKS system.

**Arguments**:

- `cihaz_bilgileri` _Union[ESUKayitModel, ESU]_ - Charge point information


**Returns**:

- `Yanit` - GIB ESU EKS service reponse

<a id="esu_service.ESUServis.mukellef_kayit"></a>

#### mukellef\_kayit

```python
def mukellef_kayit(mukellef_bilgileri: Union[ESUMukellefModel, Any] = None,
                   esu: Optional[Union[ESU, str]] = None,
                   lokasyon: Optional[Lokasyon] = None,
                   fatura: Optional[Fatura] = None,
                   mukellef: Optional[Mukellef] = None,
                   mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
                   sertifika: Optional[Sertifika] = None) -> Yanit
```

Registers tax payer information for a charge point identified by `esu`.

**Arguments**:

  mukellef_bilgileri (Union[ESUMukellefModel, Any], optional):
  Tax payer request model. Defaults to None.
  esu (Optional[Union[ESU, str]], optional):
  Charge point information. Defaults to None.
  lokasyon (Optional[Lokasyon], optional):
  Location information. Defaults to None.
  fatura (Optional[Fatura], optional):
  Invoice information. Defaults to None.
  mukellef (Optional[Mukellef], optional):
  Tax payer information. Defaults to None.
  mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
  Ownership information. Defaults to None.
  sertifika (Optional[Sertifika], optional):
  Certificate information. Defaults to None.


**Raises**:

- `ValueError` - When some information is missing to construct the request model


**Returns**:

- `Yanit` - GIB ESU EKS service reponse

<a id="esu_service.ESUServis.toplu_kayit"></a>

#### toplu\_kayit

```python
def toplu_kayit(giris_dosya_yolu: Optional[str] = None,
                csv_string: Optional[io.StringIO] = None,
                dosyaya_yaz: Optional[bool] = None,
                cikti_dosya_yolu: Optional[str] = None,
                paralel_calistir: Optional[bool] = None) -> dict[str, Any]
```

Batch registers charge points along with their tax payer information.

**Arguments**:

  giris_dosya_yolu (Optional[str], optional):
  Input csv file path. Defaults to None.
  csv_string (Optional[io.StringIO], optional):
  String data stream as alternative input. Defaults to None.
  dosyaya_yaz (Optional[bool], optional):
  Boolean flag to control whether report the results to a file.
  Defaults to None.
  cikti_dosya_yolu (Optional[str], optional):
  Output file path (if `dosyaya_yaz` is True). Defaults to None.
  paralel (Optional[bool], optional):
  Boolean flag to control multithreaded processing. Defaults to None.


**Returns**:

  dict[str, Any]: TopluKayitSonuc instance
  (which contains batch processing results) as a dictionary

<a id="esu_service.ESUServis.kayit_guncelle"></a>

#### kayit\_guncelle

```python
def kayit_guncelle(kayit_bilgileri: Union[ESUGuncellemeModel, Any] = None,
                   esu_seri_no: Optional[str] = None,
                   lokasyon: Optional[Lokasyon] = None,
                   fatura: Optional[Fatura] = None,
                   mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
                   sertifika: Optional[Sertifika] = None) -> Yanit
```

Updates a previously registered charge point's information.

**Arguments**:

  kayit_bilgileri (Union[ESUGuncellemeModel, Any], optional):
  Charge point update request model. Defaults to None.
  esu_seri_no (Optional[str], optional):
  Charge point serial number. Defaults to None.
  lokasyon (Optional[Lokasyon], optional):
  Location information. Defaults to None.
  fatura (Optional[Fatura], optional):
  Invoice information. Defaults to None.
  mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
  Ownership information. Defaults to None.
  sertifika (Optional[Sertifika], optional):
  Certificate information. Defaults to None.


**Raises**:

- `ValueError` - When some information is missing to construct the request model


**Returns**:

- `Yanit` - GIB ESU EKS service reponse

<a id="esu_service.ESUServis.toplu_guncelle"></a>

#### toplu\_guncelle

```python
def toplu_guncelle(giris_dosya_yolu: Optional[str] = None,
                   csv_string: Optional[io.StringIO] = None,
                   dosyaya_yaz: Optional[bool] = None,
                   cikti_dosya_yolu: Optional[str] = None,
                   paralel_calistir: Optional[bool] = None) -> dict[str, Any]
```

Batch updates previously registered charge points' information.

**Arguments**:

  giris_dosya_yolu (Optional[str], optional):
  Input csv file path. Defaults to None.
  csv_string (Optional[io.StringIO], optional):
  String data stream as alternative input. Defaults to None.
  dosyaya_yaz (Optional[bool], optional):
  Boolean flag to control whether report the results to a file.
  Defaults to None.
  cikti_dosya_yolu (Optional[str], optional):
  Output file path (if `dosyaya_yaz` is True). Defaults to None.
  paralel (Optional[bool], optional):
  Boolean flag to control multithreaded processing. Defaults to None.


**Returns**:

  dict[str, Any]: TopluGuncellemeSonuc instance
  (which contains batch update results) as a dictionary

<a id="esu_service.ESUServis.cihaz_kapatma"></a>

#### cihaz\_kapatma

```python
def cihaz_kapatma(cihaz_bilgisi: Optional[ESUKapatmaModel] = None,
                  esu_seri_no: Optional[str] = None) -> Yanit
```

Unregisters/delists a previously registered charge point.

**Arguments**:

  cihaz_bilgisi (Optional[ESUKapatmaModel], optional):
  Charge point delisting request model. Defaults to None.
  esu_seri_no (Optional[str], optional):
  Charge point serial number. Defaults to None.


**Raises**:

- `ValueError` - When none of the arguments are provided


**Returns**:

- `Yanit` - GIB ESU EKS service reponse

<a id="__init__"></a>

# \_\_init\_\_

<a id="py_utils"></a>

# py\_utils

<a id="py_utils.PyUtils"></a>

## PyUtils Objects

```python
class PyUtils()
```

Class encapsulating various python utility methods.

<a id="py_utils.PyUtils.read_csv"></a>

#### read\_csv

```python
@classmethod
def read_csv(
        cls, filepath_or_buffer: Union[str,
                                       io.StringIO]) -> List[Dict[str, str]]
```

Reads input data from a CSV file or string stream.

**Arguments**:

- `filepath_or_buffer` _Union[str, io.StringIO]_ - Path to a CSV file
  or a string stream containing CSV data.


**Returns**:

  List[Dict[str, str]]: A list of dictionaries representing rows in the CSV
  with all fields as strings.
