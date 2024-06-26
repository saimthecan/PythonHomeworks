import random

def sayi_tahmin_oyunu():
    hedef_sayi = random.randint(1, 100) 
    while True:
        try:
            tahmin = int(input("Tahmininizi girin: "))
            if tahmin < 1 or tahmin > 100:
                print("Lütfen 1 ile 100 arasında bir sayı girin.")
                continue

            if tahmin == hedef_sayi:
                print("Tebrikler! Doğru tahmin ettiniz.")
                break
            elif tahmin > hedef_sayi:
                print("Daha küçük bir sayı girin.")
            else:
                print("Daha büyük bir sayı girin.")

        except ValueError:
            print("Lütfen geçerli bir sayı girin.")

# Oyunu başlat
sayi_tahmin_oyunu()
