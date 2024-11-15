from time import time

from service.esu_service import ESUServis

if __name__ == "__main__":
    servis = ESUServis()  # girdi olarak resources/data/esu_list.csv dosyası kullanılır

    baslangic = time()
    sonuc = servis.toplu_kayit(
        paralel=True,
    )
    bitis = time()

    print(sonuc)
    sure = bitis - baslangic
    print(f"Süre: {sure:.2f} saniye")
