# Rastgele Sayı Üreteci (RNG) - Random Number Generator

Bitsel işlemler ve matematiksel mantık kullanarak sıfırdan yazılmış, akademik kalitede bir rastgele sayı üreteci.

## Özellikler

### 🔐 **Xorshift64* Algoritması**
- 64-bit state ile güçlü diffusion sağlar
- Bitsel XOR ve kaydırma işlemleri (12, 25, 27 bit)
- Magic constant ile istatistiksel dağılım iyileştirilir

### 🧹 **Von Neumann Whitening**
- Bias removal tekniği ile istatistiksel denge sağlar
- Ardışık bit çiftlerini analiz ederek (0,1) ve (1,0) çiftlerini seçer
- (0,0) ve (1,1) çiftlerini yoksayarak hiçbir bias kalmaz

### 📊 **Yüksek Kaliteli Çıktı**
- 0 ve 1'lerin sayısı ~%50'ye çok yakın dağılır
- Sayıların ortalama değeri ~127.5 (beklenen değer)
- Ardışık sayılar arasında yüksek bağımsızlık

## Kod Yapısı

```python
class XorshiftRNG:
    __init__(seed)           # RNG'yi başlat
    _xorshift64_raw()        # Ham Xorshift64* algoritması
    _extract_bit()           # Biti çıkar
    _fill_buffer()           # Von Neumann whitening ile buffer doldur
    generate_raw_bit()       # Whitening uygulanmış bit üret
    apply_whitening()        # n-bit whitening uygulanmış sayı üret
    get_random_number()      # 0-max_value arasında rastgele sayı üret
    get_random_bits()        # n adet rastgele bit üret
```

## Kullanım Örneği

```python
from rng import XorshiftRNG

# RNG'yi başlat
rng = XorshiftRNG(seed=42)

# Tek bit üret
bit = rng.generate_raw_bit()  # 0 veya 1

# 0-255 arasında rastgele sayı
number = rng.get_random_number(256)

# 10 adet rastgele sayı
numbers = [rng.get_random_number(256) for _ in range(10)]

# 64 adet rastgele bit
bits = rng.get_random_bits(64)
```

## Test Sonuçları (1000 sayı üretildi)

### Bit Seviyesi Analizi
- **0 sayısı:** 3937 (49.21%)
- **1 sayısı:** 4063 (50.79%)
- **İdeal:** %50 - %50

### Sayı Dağılımı
- **Ortalama:** 127.51
- **İdeal Ortalama:** 127.50
- **Minimum:** 0
- **Maksimum:** 255

### Frekans Dağılımı (8 aralık)
```
[  0- 31]:  12.90%
[ 32- 63]:  11.60%
[ 64- 95]:  14.00%
[ 96-127]:  11.70%
[128-159]:  11.80%
[160-191]:  12.80%
[192-223]:  11.80%
[224-255]:  13.40%
```

**İdeal:** Her aralık ~12.50%

### Ardışık Sayı Bağımsızlığı
- **Ortalama Fark:** 84.69
- **İdeal:** ~85.00

## Algoritma Açıklaması

### Xorshift64* Pseudocode
```
FUNCTION xorshift64_raw():
    x = state
    x = x XOR (x << 12)    // Sol kaydır 12, XOR
    x = x XOR (x >> 25)    // Sağ kaydır 25, XOR
    x = x XOR (x << 27)    // Sol kaydır 27, XOR
    state = x
    RETURN x * 2685821657736338717
END
```

### Von Neumann Whitening Pseudocode
```
FUNCTION von_neumann_whitening():
    WHILE buffer boş:
        raw = xorshift64_raw()
        FOR i = 0 TO 62 STEP 2:
            bit_pair = (raw[i], raw[i+1])
            IF bit_pair == (0, 1):
                buffer.append(0)
            ELSE IF bit_pair == (1, 0):
                buffer.append(1)
            ELSE:
                // (0,0) ve (1,1) yoksay
        END FOR
    END WHILE
    RETURN buffer.pop()
END
```

## Neden Hazır Kütüphane Kullanılmadı?

- **Tam Kontrol:** Bitsel işlemleri tamamen kontrol altında tutma
- **Eğitim:** Algoritmanın matematiksel mantığını öğrenme
- **Transparency:** Hiçbir gizli işlem yok, tüm adımlar açık

## Teknolojiler

- **Dil:** Python 3
- **Algoritmalar:** Xorshift64*, Von Neumann Whitening
- **Operasyonlar:** Bitwise (XOR, Shift), Modular Arithmetic

## Kaynaklar

1. **Xorshift** - Marsaglia, G. (2003)
2. **Von Neumann's Bias Removal** - Von Neumann, J. (1951)
3. **PCG Algoritması** - O'Neill, M. E. (2014)

## Lisans

MIT License

---

**Geliştirici:** Algoritma Mühendisi  
**Tarih:** 2 Ocak 2026
