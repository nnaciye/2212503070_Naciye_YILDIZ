# Hayalet Ekran - Yüz Tanıma ve Güvenlik Sistemi

Bu proje, Python ve OpenCV kütüphaneleri kullanılarak geliştirilmiş bir yüz tanıma ve güvenlik sistemidir. Bilgisayar kamerasını kullanarak sahibini tanır, yabancı yüzleri tespit eder ve kullanıcı bilgisayar başında olmadığında ekranı otomatik olarak kilitler.

## Özellikler

* **Yüz Kaydı:** Sistemi başlatan kullanıcının yüzünü 3 farklı açıdan (ön, sağ, sol) kaydederek eğitir.
* **Kullanıcı Tanıma:** Kayıtlı kullanıcıyı algıladığında sistemi açık tutar.
* **Yabancı Tespiti:** Tanınmayan bir yüz algılandığında veya kullanıcının yanına başka biri geldiğinde "Casus Var" uyarısı verir.
* **Otomatik Kilit:** Kamera önünde kimse olmadığında belirli bir süre sonra sistemi kilitler.
* **Model İndirme:** Gerekli olan Caffe model dosyaları eksikse otomatik olarak internetten indirir.

## Gereksinimler

Projenin çalışması için Python yüklü olmalıdır. Ayrıca aşağıdaki kütüphanelerin kurulması gerekir:

* opencv-contrib-python (Yüz tanıma modülleri için gereklidir)
* numpy

## Kurulum

1. Bu projeyi bilgisayarınıza indirin veya klonlayın.
2. Terminali açın ve gerekli kütüphaneleri yükleyin:

pip install opencv-contrib-python numpy

## Kullanım

1. Terminalden projeyi çalıştırın:

python hayaletekran_v2.py

2. **Kayıt Aşaması:** Program açıldığında yüzünüzü tanıtmanız istenecektir.
   * Kameraya düz bakın ve **SPACE** tuşuna basın.
   * Sağa dönün ve **SPACE** tuşuna basın.
   * Sola dönün ve **SPACE** tuşuna basın.

3. **Çalışma Aşaması:** Kayıt tamamlandıktan sonra sistem devreye girer.
   * Siz varsanız ekran "GÜVENLİ" olur.
   * Başka biri gelirse "TEHLİKE" uyarısı verir.
   * Kamera önünden ayrılırsanız geri sayım başlar ve sistem kilitlenir.

4. **Çıkış:** Programı kapatmak için **q** tuşuna basabilirsiniz.

## Notlar

* Proje `deploy.prototxt` ve `res10_300x300_ssd_iter_140000.caffemodel` dosyalarını kullanır. Bu dosyalar klasörde yoksa ilk çalıştırıldığında otomatik olarak indirilecektir.
* Aydınlık bir ortamda çalıştırılması yüz tanıma doğruluğunu artırır.
