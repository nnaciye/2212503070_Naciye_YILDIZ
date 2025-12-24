import cv2
import numpy as np
import os
import urllib.request


proto_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
model_url = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
proto_file = "deploy.prototxt"
model_file = "res10_300x300_ssd_iter_140000.caffemodel"

if not os.path.exists(proto_file):
    print("Proto dosyası indiriliyor...")
    urllib.request.urlretrieve(proto_url, proto_file)
if not os.path.exists(model_file):
    print("Model dosyası indiriliyor...")
    urllib.request.urlretrieve(model_url, model_file)


net = cv2.dnn.readNetFromCaffe(proto_file, model_file)
cap = cv2.VideoCapture(0)

window_name = 'Hayalet Ekran - Yuz Tanima'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

KAYIP_LIMITI = 120
CASUS_TEYIT_LIMITI = 15
CONFIDENCE_LIMIT = 0.5
TANIMA_ESIGI = 80 


RENK_YESIL = (50, 205, 50)
RENK_KIRMIZI = (0, 0, 200)
RENK_SARI = (0, 255, 255)
RENK_BEYAZ = (255, 255, 255)
RENK_SIYAH = (0, 0, 0)

kayip_sayac = 0
casus_sayac = 0
sistem_kilitli = False


kayit_asamasi = 0  
kayitli_yuzler = []
face_recognizer = None


def yuz_algila(frame):
    """DNN ile yüz algıla, koordinatları döndür"""
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    
    yuzler = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_LIMIT:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            
            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(w, endX)
            endY = min(h, endY)
            
            face_width = endX - startX
            if face_width > 50:
                yuzler.append((startX, startY, endX, endY))
    
    return yuzler


def yuz_hazirla(frame, coords):
    """Yüz bölgesini gri tonlamaya çevirip boyutlandır"""
    startX, startY, endX, endY = coords
    face = frame[startY:endY, startX:endX]
    if face.size == 0:
        return None
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (100, 100))
    gray = cv2.equalizeHist(gray)
    return gray


def yuz_cercevesi_ciz(frame, coords, renk):
    startX, startY, endX, endY = coords
    l = 30
    t = 3
    cv2.line(frame, (startX, startY), (startX + l, startY), renk, t)
    cv2.line(frame, (startX, startY), (startX, startY + l), renk, t)
    cv2.line(frame, (endX, startY), (endX - l, startY), renk, t)
    cv2.line(frame, (endX, startY), (endX, startY + l), renk, t)
    cv2.line(frame, (startX, endY), (startX + l, endY), renk, t)
    cv2.line(frame, (startX, endY), (startX, endY - l), renk, t)
    cv2.line(frame, (endX, endY), (endX - l, endY), renk, t)
    cv2.line(frame, (endX, endY), (endX, endY - l), renk, t)


def estetik_yazi_yaz(img, metin, alt_metin=""):
    h, w = img.shape[:2]
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    alpha = 0.7
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    
    font = cv2.FONT_HERSHEY_DUPLEX
    scale = 2.0
    thickness = 3
    
    text_size = cv2.getTextSize(metin, font, scale, thickness)[0]
    text_x = (w - text_size[0]) // 2
    text_y = (h + text_size[1]) // 2
    
    cv2.putText(img, metin, (text_x + 4, text_y + 4), font, scale, RENK_SIYAH, thickness + 2)
    yazi_rengi = RENK_KIRMIZI if "KILITLI" in metin or "TEHLIKE" in metin else RENK_BEYAZ
    cv2.putText(img, metin, (text_x, text_y), font, scale, yazi_rengi, thickness)
    
    if alt_metin:
        sub_scale = 1.0
        sub_size = cv2.getTextSize(alt_metin, font, sub_scale, 2)[0]
        sub_x = (w - sub_size[0]) // 2
        cv2.putText(img, alt_metin, (sub_x, text_y + 60), font, sub_scale, (200, 200, 200), 1)
    
    return img


def kayit_ekrani_ciz(frame, asama, yuz_var):
    h, w = frame.shape[:2]
    
    mesajlar = {
        1: "DUZ BAKIN",
        2: "SAGA DONUN", 
        3: "SOLA DONUN"
    }
    
    alt_mesaj = "SPACE tusuna basin" if yuz_var else "Yuz algilanmiyor..."
    
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
    
    cv2.putText(frame, f"KAYIT {asama}/3: {mesajlar[asama]}", (30, 50), 
                cv2.FONT_HERSHEY_DUPLEX, 1.2, RENK_SARI, 2)
    cv2.putText(frame, alt_mesaj, (30, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, RENK_BEYAZ, 1)
    
    return frame


def yuz_tanimaci_egit(yuzler):
    global face_recognizer
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    labels = [0] * len(yuzler) 
    face_recognizer.train(yuzler, np.array(labels))
    print(f"Yüz tanıma eğitildi! {len(yuzler)} görüntü kullanıldı.")


def yuz_tani(face_gray):
    """Yüzü tanımaya çalış. Kayıtlı kullanıcı mı?"""
    if face_recognizer is None:
        return False, 0
    
    label, confidence = face_recognizer.predict(face_gray)
    
    return confidence < TANIMA_ESIGI, confidence

print("=" * 50)
print("HAYALET EKRAN - YÜZ TANIMA SİSTEMİ")
print("=" * 50)
print("Yüzünüzü 3 açıdan kaydedeceğiz:")
print("1. Düz bakın → SPACE")
print("2. Sağa dönün → SPACE")
print("3. Sola dönün → SPACE")
print("Çıkış için 'q' tuşuna basın.")
print("=" * 50)

kayit_asamasi = 1 

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    (h, w) = frame.shape[:2]
    
    yuzler = yuz_algila(frame)
    kisi_sayisi = len(yuzler)
    
    key = cv2.waitKey(1) & 0xFF
    
    
    if kayit_asamasi >= 1 and kayit_asamasi <= 3:
        if kisi_sayisi == 1:
            yuz_cercevesi_ciz(frame, yuzler[0], RENK_SARI)
            
            if key == ord(' '):  
                face_gray = yuz_hazirla(frame, yuzler[0])
                if face_gray is not None:
                    kayitli_yuzler.append(face_gray)
                    print(f"Kayıt {kayit_asamasi}/3 tamamlandı!")
                    kayit_asamasi += 1
                    
                    if kayit_asamasi == 4:
                        yuz_tanimaci_egit(kayitli_yuzler)
                        print("\n✓ TÜM KAYITLAR TAMAMLANDI!")
                        print("Artık sistem sizi tanıyacak.\n")
        
        if kayit_asamasi <= 3:
            frame = kayit_ekrani_ciz(frame, kayit_asamasi, kisi_sayisi == 1)
    
    
    elif kayit_asamasi == 4:
        
        
        for coords in yuzler:
            face_gray = yuz_hazirla(frame, coords)
            if face_gray is not None:
                tanindi, conf = yuz_tani(face_gray)
                if tanindi:
                    yuz_cercevesi_ciz(frame, coords, RENK_YESIL)
                    cv2.putText(frame, f"Kullanici", (coords[0], coords[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, RENK_YESIL, 2)
                else:
                    yuz_cercevesi_ciz(frame, coords, RENK_KIRMIZI)
                    cv2.putText(frame, f"Yabanci", (coords[0], coords[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, RENK_KIRMIZI, 2)
        
        
        kullanici_var = False
        yabanci_var = False
        
        for coords in yuzler:
            face_gray = yuz_hazirla(frame, coords)
            if face_gray is not None:
                tanindi, _ = yuz_tani(face_gray)
                if tanindi:
                    kullanici_var = True
                else:
                    yabanci_var = True
        
        
        
        if kisi_sayisi > 1 and yabanci_var:
           
            casus_sayac += 1
            if casus_sayac > CASUS_TEYIT_LIMITI:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                frame = estetik_yazi_yaz(frame, "TEHLIKE! CASUS VAR", "Gizlilik ihlali tespit edildi.")
                kayip_sayac = 0
        
        elif sistem_kilitli:
            
            if kullanici_var and not yabanci_var:
                
                sistem_kilitli = False
                kayip_sayac = 0
                casus_sayac = 0
                print("Kullanıcı tanındı - Kilit açıldı!")
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            else:
                
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                frame = estetik_yazi_yaz(frame, "SISTEM KILITLI", "Yetkisiz erisim engellendi.")
        
        elif kullanici_var and not yabanci_var:
            
            kayip_sayac = 0
            casus_sayac = 0
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.putText(frame, "SISTEM GUVENLI", (30, 50), cv2.FONT_HERSHEY_DUPLEX, 0.8, RENK_YESIL, 2)
            cv2.putText(frame, "Kullanici Dogrulandi", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        elif kisi_sayisi == 0:
            
            casus_sayac = 0
            kayip_sayac += 1
            
            if kayip_sayac > KAYIP_LIMITI:
                sistem_kilitli = True
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                frame = estetik_yazi_yaz(frame, "SISTEM KILITLENDI", "Kullanici tespit edilemedi.")
            else:
                kalan = int((KAYIP_LIMITI - kayip_sayac) / 30)
                cv2.putText(frame, f"Otomatik Kilit: {kalan}", (w - 250, h - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, RENK_SARI, 2)
        
        else:
            
            if not sistem_kilitli:
                kayip_sayac += 1
                if kayip_sayac > KAYIP_LIMITI:
                    sistem_kilitli = True
    
    cv2.imshow(window_name, frame)
    
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nProgram kapatıldı.")
