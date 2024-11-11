from service.esu_service import ESUServis

if __name__ == "__main__":
    servis = ESUServis()  # girdi olarak resources/data/esu_list.csv dosyası kullanılır
    sonuc = servis.toplu_kayit()  # çıktı olarak gonderim_raporu dosyası kullanılır
    print(sonuc)
