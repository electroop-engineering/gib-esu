# <a name='codedocumentation'></a>Code documentation

* [models/base\_model](#modelsbasemodel)


	* [CustomBaseModel](#custombasemodel)


* [models/service\_models](#modelsservicemodels)


	* [API](#api)


	* [APIParametreleri](#apiparametreleri)


	* [Durum](#durum)


	* [ESUKayitSonucu](#esukayitsonucu)


	* [ESUServisKonfigurasyonu](#esuserviskonfigurasyonu)


	* [ESUTopluGuncellemeSonucu](#esutopluguncellemesonucu)


	* [ESUTopluKayitSonucu](#esutoplukayitsonucu)


	* [EvetVeyaHayir](#evetveyahayir)


	* [MukellefKayitSonucu](#mukellefkayitsonucu)


	* [Sonuc](#sonuc)


	* [TopluGuncellemeSonuc](#topluguncellemesonuc)


	* [TopluKayitSonuc](#toplukayitsonuc)


	* [Yanit](#yanit)


* [models/api\_models](#modelsapimodels)


	* [CustomBaseModelWithValidator](#custombasemodelwithvalidator)


		* [CustomBaseModelWithValidator.\_enforce\_model\_constraints](#custombasemodelwithvalidatorenforcemodelconstraints)


	* [ESU](#esu)


	* [ESUGuncellemeBilgisi](#esuguncellemebilgisi)


	* [ESUGuncellemeModel](#esuguncellememodel)


		* [CustomBaseModelWithValidator.\_enforce\_model\_constraints](#custombasemodelwithvalidatorenforcemodelconstraints)


	* [ESUKapatmaModel](#esukapatmamodel)


	* [ESUKayitModel](#esukayitmodel)


		* [ESUKayitModel.\_enforce\_model\_constraints](#esukayitmodelenforcemodelconstraints)


	* [ESUMukellefBilgisi](#esumukellefbilgisi)


	* [ESUMukellefModel](#esumukellefmodel)


		* [CustomBaseModelWithValidator.\_enforce\_model\_constraints](#custombasemodelwithvalidatorenforcemodelconstraints)


	* [ESUSeriNo](#esuserino)


	* [ESUTipi](#esutipi)


	* [Fatura](#fatura)


	* [Firma](#firma)


	* [FirmaKodu](#firmakodu)


	* [Lokasyon](#lokasyon)


	* [Mukellef](#mukellef)


	* [MulkiyetSahibi](#mulkiyetsahibi)


	* [Sertifika](#sertifika)


	* [Soket](#soket)


	* [SoketTipi](#sokettipi)


	* [\_validate\_tax\_number](#validatetaxnumber)


	* [\_validate\_tax\_payer\_and\_update\_models](#validatetaxpayerandupdatemodels)


* [helpers/py\_utils](#helperspyutils)


	* [PyUtils](#pyutils)


* [services/esu\_service](#servicesesuservice)


	* [ESUServis](#esuservis)


		* [ESUServis.\_\_init\_\_](#esuservisinit)


		* [ESUServis.\_api\_isteği](#esuservisapiisteği)


		* [ESUServis.\_dosyaya\_yaz](#esuservisdosyayayaz)


		* [ESUServis.\_esu\_bilgisi\_hazirla](#esuservisesubilgisihazirla)


		* [ESUServis.\_guncelleme\_kaydi\_isle](#esuservisguncellemekaydiisle)


		* [ESUServis.\_kayit\_isle](#esuserviskayitisle)


		* [ESUServis.\_mukellef\_bilgisi\_hazirla](#esuservismukellefbilgisihazirla)


		* [ESUServis.cihaz\_kapatma](#esuserviscihazkapatma)


		* [ESUServis.cihaz\_kayit](#esuserviscihazkayit)


		* [ESUServis.kayit\_guncelle](#esuserviskayitguncelle)


		* [ESUServis.mukellef\_kayit](#esuservismukellefkayit)


		* [ESUServis.toplu\_guncelle](#esuservistopluguncelle)


		* [ESUServis.toplu\_kayit](#esuservistoplukayit)

## <a name='modelsbasemodel'></a>models/base\_model
&uparrow; Back to [code documentation index](#codedocumentation)

### <a name='classes'></a>Classes

* [CustomBaseModel](#custombasemodel)

#### <a name='custombasemodel'></a>CustomBaseModel
Custom base model that ignores extra fields.
## <a name='modelsservicemodels'></a>models/service\_models
&uparrow; Back to [code documentation index](#codedocumentation)

### <a name='classes'></a>Classes

* [API](#api)

* [APIParametreleri](#apiparametreleri)

* [Durum](#durum)

* [ESUKayitSonucu](#esukayitsonucu)

* [ESUServisKonfigurasyonu](#esuserviskonfigurasyonu)

* [ESUTopluGuncellemeSonucu](#esutopluguncellemesonucu)

* [ESUTopluKayitSonucu](#esutoplukayitsonucu)

* [EvetVeyaHayir](#evetveyahayir)

* [MukellefKayitSonucu](#mukellefkayitsonucu)

* [Sonuc](#sonuc)

* [TopluGuncellemeSonuc](#topluguncellemesonuc)

* [TopluKayitSonuc](#toplukayitsonuc)

* [Yanit](#yanit)

#### <a name='api'></a>API
Service model for API URLs.
#### <a name='apiparametreleri'></a>APIParametreleri
Service model for API parameters.
#### <a name='durum'></a>Durum
Enum for API response status codes.
#### <a name='esukayitsonucu'></a>ESUKayitSonucu
Charge point registration output model.
#### <a name='esuserviskonfigurasyonu'></a>ESUServisKonfigurasyonu
Service configuration model.
#### <a name='esutopluguncellemesonucu'></a>ESUTopluGuncellemeSonucu
Batch update output model for single charge point.
#### <a name='esutoplukayitsonucu'></a>ESUTopluKayitSonucu
Batch registration output model for single charge point.
#### <a name='evetveyahayir'></a>EvetVeyaHayir
Enum for boolean config parameters.
#### <a name='mukellefkayitsonucu'></a>MukellefKayitSonucu
Charge point tax payer registration model.
#### <a name='sonuc'></a>Sonuc
Api result model.
#### <a name='topluguncellemesonuc'></a>TopluGuncellemeSonuc
Charge point batch update output model.
#### <a name='toplukayitsonuc'></a>TopluKayitSonuc
Charge point batch registration output model.
#### <a name='yanit'></a>Yanit
Api response model.
## <a name='modelsapimodels'></a>models/api\_models
&uparrow; Back to [code documentation index](#codedocumentation)


### <a name='dependencies'></a>Dependencies
* re

### <a name='classes'></a>Classes

* [CustomBaseModelWithValidator](#custombasemodelwithvalidator)

* [ESU](#esu)

* [ESUGuncellemeBilgisi](#esuguncellemebilgisi)

* [ESUGuncellemeModel](#esuguncellememodel)

* [ESUKapatmaModel](#esukapatmamodel)

* [ESUKayitModel](#esukayitmodel)

* [ESUMukellefBilgisi](#esumukellefbilgisi)

* [ESUMukellefModel](#esumukellefmodel)

* [ESUSeriNo](#esuserino)

* [ESUTipi](#esutipi)

* [Fatura](#fatura)

* [Firma](#firma)

* [FirmaKodu](#firmakodu)

* [Lokasyon](#lokasyon)

* [Mukellef](#mukellef)

* [MulkiyetSahibi](#mulkiyetsahibi)

* [Sertifika](#sertifika)

* [Soket](#soket)

* [SoketTipi](#sokettipi)

#### <a name='custombasemodelwithvalidator'></a>CustomBaseModelWithValidator
Custom base model with a predefined model validator function.
##### <a name='functions'></a>Functions

* [CustomBaseModelWithValidator.\_enforce\_model\_constraints](#custombasemodelwithvalidatorenforcemodelconstraints)

###### <a name='custombasemodelwithvalidatorenforcemodelconstraints'></a>CustomBaseModelWithValidator.\_enforce\_model\_constraints
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#models/api_models)

&uparrow; Back to [class index](#CustomBaseModelWithValidator)

Validates the model according to the model constraints.
#### <a name='esu'></a>ESU
Charge point model.
#### <a name='esuguncellemebilgisi'></a>ESUGuncellemeBilgisi
Intermediary model that encapsulates charge point and ownership information.
#### <a name='esuguncellememodel'></a>ESUGuncellemeModel
Charge point update request model.
##### <a name='functions'></a>Functions

* [CustomBaseModelWithValidator.\_enforce\_model\_constraints](#custombasemodelwithvalidatorenforcemodelconstraints)

###### <a name='custombasemodelwithvalidatorenforcemodelconstraints'></a>CustomBaseModelWithValidator.\_enforce\_model\_constraints
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#models/api_models)

&uparrow; Back to [class index](#ESUGuncellemeModel)

Validates the model according to the model constraints.
#### <a name='esukapatmamodel'></a>ESUKapatmaModel
Charge point delisting request model.
#### <a name='esukayitmodel'></a>ESUKayitModel
Charge point registration request model.
##### <a name='functions'></a>Functions

* [ESUKayitModel.\_enforce\_model\_constraints](#esukayitmodelenforcemodelconstraints)

###### <a name='esukayitmodelenforcemodelconstraints'></a>ESUKayitModel.\_enforce\_model\_constraints
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#models/api_models)

&uparrow; Back to [class index](#ESUKayitModel)

Validates the model according to the model constraints.
#### <a name='esumukellefbilgisi'></a>ESUMukellefBilgisi
Intermediary model that encapsulates charge point and tax payer information.
#### <a name='esumukellefmodel'></a>ESUMukellefModel
Charge point tax payer info registration model.
##### <a name='functions'></a>Functions

* [CustomBaseModelWithValidator.\_enforce\_model\_constraints](#custombasemodelwithvalidatorenforcemodelconstraints)

###### <a name='custombasemodelwithvalidatorenforcemodelconstraints'></a>CustomBaseModelWithValidator.\_enforce\_model\_constraints
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#models/api_models)

&uparrow; Back to [class index](#ESUMukellefModel)

Validates the model according to the model constraints.
#### <a name='esuserino'></a>ESUSeriNo
Charge point's serial number.
#### <a name='esutipi'></a>ESUTipi
Charge point type enum.
#### <a name='fatura'></a>Fatura
Invoice model.
#### <a name='firma'></a>Firma
Company info model.
#### <a name='firmakodu'></a>FirmaKodu
Company code model.
#### <a name='lokasyon'></a>Lokasyon
EV charging location model.
#### <a name='mukellef'></a>Mukellef
Tax payer model.
#### <a name='mulkiyetsahibi'></a>MulkiyetSahibi
Charge point owner model.
#### <a name='sertifika'></a>Sertifika
Certificate model.
#### <a name='soket'></a>Soket
Charge point's connectors.
#### <a name='sokettipi'></a>SoketTipi
Socket type enum.
### <a name='functions'></a>Functions

* [\_validate\_tax\_number](#validatetaxnumber)

* [\_validate\_tax\_payer\_and\_update\_models](#validatetaxpayerandupdatemodels)

#### <a name='validatetaxnumber'></a>\_validate\_tax\_number
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#models/api_models)

Validates a given tax number.

    Args:
        tax_nr (str): Tax number to validate

    Raises:
        ValueError: In case tax_nr does not conform to tax number scheme

    Returns:
        str: Validated tax_nr

#### <a name='validatetaxpayerandupdatemodels'></a>\_validate\_tax\_payer\_and\_update\_models
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#models/api_models)

Validates both the tax payer registration and the charge point update models.
## <a name='helperspyutils'></a>helpers/py\_utils
&uparrow; Back to [code documentation index](#codedocumentation)


### <a name='dependencies'></a>Dependencies
* io

* pandas

### <a name='classes'></a>Classes

* [PyUtils](#pyutils)

#### <a name='pyutils'></a>PyUtils
Class encapsulating various python utility methods.
## <a name='servicesesuservice'></a>services/esu\_service
&uparrow; Back to [code documentation index](#codedocumentation)


### <a name='dependencies'></a>Dependencies
* base64

* concurrent

* io

* json

* os

* requests

### <a name='classes'></a>Classes

* [ESUServis](#esuservis)

#### <a name='esuservis'></a>ESUServis
Class that handles GIB ESU EKS service operations.
##### <a name='functions'></a>Functions

* [ESUServis.\_\_init\_\_](#esuservisinit)

* [ESUServis.\_api\_isteği](#esuservisapiisteği)

* [ESUServis.\_dosyaya\_yaz](#esuservisdosyayayaz)

* [ESUServis.\_esu\_bilgisi\_hazirla](#esuservisesubilgisihazirla)

* [ESUServis.\_guncelleme\_kaydi\_isle](#esuservisguncellemekaydiisle)

* [ESUServis.\_kayit\_isle](#esuserviskayitisle)

* [ESUServis.\_mukellef\_bilgisi\_hazirla](#esuservismukellefbilgisihazirla)

* [ESUServis.cihaz\_kapatma](#esuserviscihazkapatma)

* [ESUServis.cihaz\_kayit](#esuserviscihazkayit)

* [ESUServis.kayit\_guncelle](#esuserviskayitguncelle)

* [ESUServis.mukellef\_kayit](#esuservismukellefkayit)

* [ESUServis.toplu\_guncelle](#esuservistopluguncelle)

* [ESUServis.toplu\_kayit](#esuservistoplukayit)

###### <a name='esuservisinit'></a>ESUServis.\_\_init\_\_
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

ESUServis constructor.

        Args:
            _config (Optional[Dict[str, str  |  None]], optional):
            Dictionary or env file path to read the config from. Defaults to None.

###### <a name='esuservisapiisteği'></a>ESUServis.\_api\_isteği
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Internal method to perform API requests.

        Returns:
            Yanit: GIB ESU EKS service reponse

###### <a name='esuservisdosyayayaz'></a>ESUServis.\_dosyaya\_yaz
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Internal method to write the batch processing results to a file.

        Args:
            cikti_dosya_yolu (str): Output file path
            icerik (str): Data to write to the output file

###### <a name='esuservisesubilgisihazirla'></a>ESUServis.\_esu\_bilgisi\_hazirla
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)


        Internal method to construct a charge point registration request model instance.

        Args:
            kayit (dict): Dictionary to convert to an ESU instance.

        Returns:
            ESU: Constructed charge point registration request model instance.

###### <a name='esuservisguncellemekaydiisle'></a>ESUServis.\_guncelleme\_kaydi\_isle
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Internal method to update a previously registered charge point's information.

        Args:
            kayit (dict): Dictionary corresponding to a row read from csv input
            sonuc (TopluGuncellemeSonuc): Result model for processed update requests

###### <a name='esuserviskayitisle'></a>ESUServis.\_kayit\_isle
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Internal method to register both the charge point and the tax payer.

        Args:
            kayit (dict): Dictionary corresponding to a row read from csv input
            sonuc (TopluKayitSonuc): Result model for processed registration requests

###### <a name='esuservismukellefbilgisihazirla'></a>ESUServis.\_mukellef\_bilgisi\_hazirla
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Internal method to construct a tax payer registration request model instance.

        Args:
            kayit (dict): Dictionary to convert to an ESUMukellefModel instance
            esu (ESU): Charge point model instance

        Returns:
            ESUMukellefModel: Constructed tax payer registration request model instance.

###### <a name='esuserviscihazkapatma'></a>ESUServis.cihaz\_kapatma
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Unregisters/delists a previously registered charge point.

        Args:
            cihaz_bilgisi (Optional[ESUKapatmaModel], optional):
                Charge point delisting request model. Defaults to None.
            esu_seri_no (Optional[str], optional):
                Charge point serial number. Defaults to None.

        Raises:
            ValueError: When none of the arguments are provided

        Returns:
            Yanit: GIB ESU EKS service reponse

###### <a name='esuserviscihazkayit'></a>ESUServis.cihaz\_kayit
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Registers a charge point with the GIB ESU EKS system.

        Args:
            cihaz_bilgileri (Union[ESUKayitModel, ESU]): Charge point information

        Returns:
            Yanit: GIB ESU EKS service reponse

###### <a name='esuserviskayitguncelle'></a>ESUServis.kayit\_guncelle
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Updates a previously registered charge point's information.

        Args:
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

        Raises:
            ValueError: When some information is missing to construct the request model

        Returns:
            Yanit: GIB ESU EKS service reponse

###### <a name='esuservismukellefkayit'></a>ESUServis.mukellef\_kayit
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)

Registers tax payer information for a charge point identified by `esu`.

        Args:
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

        Raises:
            ValueError: When some information is missing to construct the request model

        Returns:
            Yanit: GIB ESU EKS service reponse

###### <a name='esuservistopluguncelle'></a>ESUServis.toplu\_guncelle
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)


        Batch updates previously registered charge points' information.

        Args:
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

        Returns:
            dict[str, Any]: TopluGuncellemeSonuc instance
            (which contains batch update results) as a dictionary

###### <a name='esuservistoplukayit'></a>ESUServis.toplu\_kayit
&uparrow; Back to [code documentation index](#codedocumentation)

&uparrow; Back to [module index](#services/esu_service)

&uparrow; Back to [class index](#ESUServis)


        Batch registers charge points along with their tax payer information.

        Args:
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

        Returns:
            dict[str, Any]: TopluKayitSonuc instance
            (which contains batch processing results) as a dictionary
