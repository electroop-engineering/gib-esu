from time import time

from services.esu_service import ESUServis

servis = ESUServis()

baslangic = time()

sonuc = servis.toplu_kayit(
    giris_dosya_yolu="input.csv",  # verilmezse "resources/data/esu_list.csv" varsayılır
    dosyaya_yaz=True,  # varsayılan değer False
    cikti_dosya_yolu="output.json",  # verilmezse "gonderim_raporu.json" kullanılır
    paralel=True,  # varsayılan değer False
)

bitis = time()

print(sonuc)

sure = bitis - baslangic
print(f"Süre: {sure:.2f} saniye")
