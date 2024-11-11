from pydantic import BaseModel, Field

# numerical constants
MIN_FIRMA_KODU = MIN_SERI_NO = 3


class ESUKapatmaBilgisi(BaseModel):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)


class ESUKapatmaModel(BaseModel):
    firma_kodu: str = Field(min_length=MIN_FIRMA_KODU)
    kapatma_bilgisi: ESUKapatmaBilgisi


class ESUKapatma(BaseModel):
    model: ESUKapatmaModel
