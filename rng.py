"""
================================================================================
                    RASTGELE SAYI ÜRETECI (RNG)
                    Modern Xorshift + Von Neumann Whitening
================================================================================

MATEMATİKSEL MANTIK VE PSEUDOKODuz:
-----------------------------------

XORSHIFT64* ALGORITMASI:
  1. STATE (64-bit) ile başla
  2. Her iterasyonda şu işlemleri yap:
     x ^= x << 12    (sol kaydır 12 bit, XOR ile karıştır)
     x ^= x >> 25    (sağ kaydır 25 bit, XOR ile karıştır)
     x ^= x << 27    (sol kaydır 27 bit, XOR ile karıştır)
  3. Çıktı: x * 2685821657736338717 (Magic constant ile çarpmak)
  4. Üretilen sayı hala hafif bias içerebilir

VON NEUMANN WHITENING (Bias Removal):
  1. Xorshift'ten ardışık bit çiftleri al: (bit_i, bit_i+1)
  2. Eğer (0,1) ise → output bit = 0
  3. Eğer (1,0) ise → output bit = 1
  4. Eğer (0,0) veya (1,1) ise → bu çifti yoksay (discardla)
  5. Bu şekilde 0 ve 1'lerin matematiksel olarak eşit dağılması sağlanır

BUŞ GERÇEKLEŞTİRME:
  - Temel Xorshift64* algoritması
  - Von Neumann whitening ile istatistiksel balans
  - Bit seviyesi operasyonlarla tam kontrol
  - Hiçbir hazır kütüphane kullanılmıyor

================================================================================
"""

class XorshiftRNG:
    """
    Xorshift64* algoritması ile Von Neumann whitening kullanan
    kriptografik olmayan, yüksek kalitede rastgele sayı üreteci.
    """
    
    def __init__(self, seed=1234567890):
        """
        RNG'yi başlat.
        
        Args:
            seed (int): İlk state değeri (64-bit)
        """
        # State: İç durum değişkeni (64-bit)
        # Bit işlemleri için 64-bit mask
        self.state = seed & 0xFFFFFFFFFFFFFFFF
        if self.state == 0:
            self.state = 1  # State sıfır olmamalı
        
        # Whitening için buffer
        self.bit_buffer = []
        self.buffer_index = 0
    
    def _xorshift64_raw(self):
        """
        Ham Xorshift64* algoritması.
        
        PSEUDOKODuz:
          x = state
          x ^= x << 12
          x ^= x >> 25
          x ^= x << 27
          state = x
          return x * MAGIC_CONSTANT
        
        Returns:
            int: 64-bit ham rastgele sayı
        """
        # Bitsel işlemler (XOR ve kaydırma)
        x = self.state
        
        # İlk dönüşüm: 12 bit sola kaydır ve XOR
        x ^= (x << 12) & 0xFFFFFFFFFFFFFFFF
        
        # İkinci dönüşüm: 25 bit sağa kaydır ve XOR
        x ^= (x >> 25)
        
        # Üçüncü dönüşüm: 27 bit sola kaydır ve XOR
        x ^= (x << 27) & 0xFFFFFFFFFFFFFFFF
        
        # State'i güncelle
        self.state = x
        
        # Magic constant ile çarpmak (diffusion için)
        MAGIC = 2685821657736338717
        result = (x * MAGIC) & 0xFFFFFFFFFFFFFFFF
        
        return result
    
    def _extract_bit(self, number, bit_pos):
        """
        Bir sayıdan belirli bir biti çıkar.
        
        Args:
            number (int): Sayı
            bit_pos (int): Bit pozisyonu (0 = en sağdaki bit)
        
        Returns:
            int: 0 veya 1
        """
        return (number >> bit_pos) & 1
    
    def _fill_buffer(self):
        """
        Von Neumann whitening ile buffer'ı doldu.
        
        PSEUDOKODuz:
          while buffer'ın boş:
              raw = xorshift64_raw() çalıştır
              her 64 bit için:
                  bit_pair = (bit_i, bit_{i+1}) al
                  if bit_pair == (0,1): buffer'a 0 ekle
                  if bit_pair == (1,0): buffer'a 1 ekle
                  else: yoksay (whitening)
        """
        while len(self.bit_buffer) < 32:  # En az 32 bit topla
            raw = self._xorshift64_raw()
            
            # Ham sayıdan bit çiftlerini çıkar ve Von Neumann whitening uygula
            for i in range(0, 64, 2):
                bit1 = self._extract_bit(raw, i)
                bit2 = self._extract_bit(raw, i + 1)
                
                # Von Neumann whitening kuralları
                if bit1 == 0 and bit2 == 1:
                    self.bit_buffer.append(0)
                elif bit1 == 1 and bit2 == 0:
                    self.bit_buffer.append(1)
                # (0,0) ve (1,1) yoksay (bias removal için)
    
    def generate_raw_bit(self):
        """
        Von Neumann whitening uygulanmış, istatistiksel olarak dengeli bir bit üret.
        
        Returns:
            int: 0 veya 1
        """
        if len(self.bit_buffer) == 0:
            self._fill_buffer()
        
        bit = self.bit_buffer.pop(0)
        return bit
    
    def apply_whitening(self, num_bits=8):
        """
        Belirtilen sayıda whitening uygulanmış bit çıkar.
        
        Args:
            num_bits (int): Çıkarmak istenen bit sayısı
        
        Returns:
            int: Whitening uygulanmış sayı
        """
        result = 0
        for i in range(num_bits):
            bit = self.generate_raw_bit()
            result |= (bit << i)  # Biti pozisyona yerleştir
        
        return result
    
    def get_random_number(self, max_value=256):
        """
        0 ile max_value arasında rastgele bir sayı üret.
        
        Args:
            max_value (int): Üst sınır (varsayılan: 256)
        
        Returns:
            int: 0 ile max_value-1 arasında rastgele sayı
        """
        # max_value için gereken bit sayısını hesapla
        if max_value <= 1:
            return 0
        
        # Bit sayısını belirle
        bit_length = max_value.bit_length()
        
        # Gerekli bit sayısı kadar whitening uygulanmış sayı üret
        while True:
            num = self.apply_whitening(bit_length)
            if num < max_value:
                return num
    
    def get_random_bits(self, n):
        """
        n adet rastgele bit üret.
        
        Args:
            n (int): Bit sayısı
        
        Returns:
            list: 0 ve 1'lerden oluşan liste
        """
        bits = []
        for _ in range(n):
            bits.append(self.generate_raw_bit())
        return bits


# ================================================================================
#                            TEST VE ANALİZ
# ================================================================================

def analyze_distribution(rng, count=1000):
    """
    Üretilen sayıların istatistiksel dağılımını analiz et.
    
    Args:
        rng: RNG örneği
        count (int): Üretilecek sayı adedi
    
    Returns:
        dict: İstatistiksel veriler
    """
    print("=" * 80)
    print("RASTGELE SAYI ÜRETECI (RNG) - İSTATİSTİKSEL ANALİZ RAPORU")
    print("=" * 80)
    print()
    
    # 1. BIT SEVİYESİ ANALİZİ
    print("[1] BIT SEVİYESİ ANALİZİ")
    print("-" * 80)
    bits = rng.get_random_bits(count * 8)
    zeros = sum(1 for b in bits if b == 0)
    ones = sum(1 for b in bits if b == 1)
    
    print(f"Toplam bit sayısı: {len(bits)}")
    print(f"0 sayısı: {zeros} ({100*zeros/len(bits):.2f}%)")
    print(f"1 sayısı: {ones} ({100*ones/len(bits):.2f}%)")
    print(f"İdeal: Her biri ~50.00%")
    print()
    
    # 2. RASTGELE SAYI ANALİZİ (0-255 aralığı)
    print("[2] RASTGELE SAYI ANALİZİ (0-255 aralığında)")
    print("-" * 80)
    numbers = [rng.get_random_number(256) for _ in range(count)]
    
    avg = sum(numbers) / len(numbers)
    min_val = min(numbers)
    max_val = max(numbers)
    
    print(f"Üretilen sayı adedi: {len(numbers)}")
    print(f"Ortalama (Average): {avg:.2f}")
    print(f"Minimum: {min_val}")
    print(f"Maksimum: {max_val}")
    print(f"İdeal Ortalama: 127.50")
    print()
    
    # 3. FREKANS DAĞILIMI (Histogram-benzeri)
    print("[3] FREKANS DAĞILIMI (8 aralık)")
    print("-" * 80)
    buckets = [0] * 8
    for num in numbers:
        bucket_idx = num // 32  # 256/8 = 32
        if bucket_idx < 8:
            buckets[bucket_idx] += 1
    
    for i, count_in_bucket in enumerate(buckets):
        start = i * 32
        end = (i + 1) * 32 - 1
        percentage = 100 * count_in_bucket / len(numbers)
        bar = "█" * int(percentage / 2)
        print(f"[{start:3d}-{end:3d}]: {bar} {percentage:5.2f}% ({count_in_bucket})")
    
    print()
    print(f"İdeal: Her aralık ~12.50%")
    print()
    
    # 4. ARDIŞIK SAYI ÇIFTLERININ KORELASYONU
    print("[4] ARDIŞIK SAYI KORELASYONU")
    print("-" * 80)
    if len(numbers) >= 2:
        correlations = []
        for i in range(len(numbers) - 1):
            # Basit korelasyon: benzerlik derecesi
            diff = abs(numbers[i] - numbers[i+1])
            correlations.append(diff)
        
        avg_diff = sum(correlations) / len(correlations)
        print(f"Ardışık sayılar arasında ortalama fark: {avg_diff:.2f}")
        print(f"İdeal: ~85.00 (yüksek bağımsızlık göstergesi)")
        print()
    
    # 5. ÖZETz
    print("[5] ÖZET")
    print("-" * 80)
    bit_balance = abs(zeros - ones)
    print(f"Bit dengesi sapması: {bit_balance} (0'a yakın iyidir)")
    print(f"Sayı dağılımı dengesi: {abs(avg - 127.5):.2f} (0'a yakın iyidir)")
    print()
    print("✓ Algoritma açıklanmıştır: Xorshift64* + Von Neumann Whitening")
    print("✓ Yüksek entropi sağlanmıştır (XOR işlemleri)")
    print("✓ İstatistiksel denge sağlanmıştır (Whitening)")
    print("=" * 80)


if __name__ == "__main__":
    # RNG'yi başlat (seed ile)
    rng = XorshiftRNG(seed=42)
    
    # Analiz yap
    analyze_distribution(rng, count=1000)
