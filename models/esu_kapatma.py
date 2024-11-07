from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated, TypedDict

# numerical constants
MIN_FIRMA_KODU = MIN_SERI_NO = 3

# error messages
FIRMA_KODU_ERROR = f"firma_kodu en az {MIN_FIRMA_KODU} karakter uzunluğunda olmalı"
SERI_NO_ERROR = f"esu_seri_no en az {MIN_SERI_NO} karakter uzunluğunda olmalı"


class ESUKapatmaBilgisi(TypedDict):
    esu_seri_no: str


class ESUKapatmaModel(TypedDict):
    firma_kodu: str
    kapatma_bilgisi: ESUKapatmaBilgisi


def validate_model(model: ESUKapatmaModel) -> ESUKapatmaModel:
    firma_kodu = model["firma_kodu"]
    seri_no = model["kapatma_bilgisi"]["esu_seri_no"]

    # unconditionally check firma_kodu
    assert len(firma_kodu.strip()) >= MIN_FIRMA_KODU, FIRMA_KODU_ERROR

    # unconditionally check seri_no
    assert len(seri_no.strip()) >= MIN_SERI_NO, SERI_NO_ERROR

    return model


ESUKapatmaModelCandidate = Annotated[ESUKapatmaModel, AfterValidator(validate_model)]


class ESUKapatma(BaseModel):
    model: ESUKapatmaModelCandidate
