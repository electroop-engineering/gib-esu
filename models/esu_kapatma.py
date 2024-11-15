from pydantic import BaseModel, Field

from .constants import MIN_FIRMA_KODU, MIN_SERI_NO


class ESUKapatmaBilgisi(BaseModel):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)


class ESUKapatmaModel(BaseModel):
    firma_kodu: str = Field(min_length=MIN_FIRMA_KODU)
    kapatma_bilgisi: ESUKapatmaBilgisi


class ESUKapatma(BaseModel):
    model: ESUKapatmaModel
