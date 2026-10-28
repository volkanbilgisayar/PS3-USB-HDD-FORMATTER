# 💽 FAT32 Pro Formatter
### 🎮 PS3 ve 500 GB+ USB / Harici Disk Hazırlama Aracı

<p align="center">
  <strong>Büyük kapasiteli diskleri FAT32 formatında hazırlayın, MBR bölüm tablosu oluşturun ve PS3 uyumlu bir disk yapısı oluşturmayı kolaylaştırın.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/Filesystem-FAT32-orange?style=for-the-badge" alt="FAT32">
  <img src="https://img.shields.io/badge/Partition-MBR-blue?style=for-the-badge" alt="MBR">
  <img src="https://img.shields.io/badge/Target-PlayStation%203-white?style=for-the-badge&logo=playstation" alt="PlayStation 3">
</p>

---

## 📌 Proje Hakkında

**FAT32 Pro Formatter**, Windows üzerinde büyük kapasiteli USB bellekleri, harici HDD'leri ve taşınabilir SSD'leri FAT32 dosya sisteminde biçimlendirmeyi ve PlayStation 3 (PS3) kullanımına hazırlamayı amaçlayan bir araçtır.

Windows'un standart biçimlendirme araçlarında bulunan FAT32 kapasite sınırlamalarını aşmaya yardımcı olmayı ve GUIFormat gibi araçlarla yaşanabilen disk algılama sorunlarını azaltmayı hedefler.

### 💡 Neden FAT32 Pro Formatter?

- 💾 **500 GB, 1 TB, 2 TB ve üzeri diskler:** Büyük kapasiteli depolama aygıtları için tasarlanmıştır.
- 🔍 **Fiziksel disk algılama:** Sürücü harfi atanmamış veya RAW durumundaki diskleri listelemeyi hedefler.
- 🔄 **MBR bölüm tablosu:** Tam disk hazırlığı seçeneğiyle diski MBR düzenine dönüştürmeyi amaçlar.
- 🧰 **Tek FAT32 bölümü:** Diskte tek bir birincil FAT32 bölümü oluşturulmasını sağlar.
- 🔤 **Sürücü harfi atama:** Biçimlendirme sonrasında Windows üzerinden erişimi kolaylaştırır.
- 🎮 **PS3 klasör yapısı:** İsteğe bağlı olarak konsol kullanımında yaygın olan klasörleri oluşturabilir.
- 🛡️ **Sistem diski koruması:** Windows'un kurulu olduğu sistem diskini yanlışlıkla silmeye karşı korumayı hedefler.

> ⚠️ Özelliklerin kullanılabilirliği uygulamanın gerçek sürümüne ve uygulanan koruma mekanizmalarına bağlıdır. Bu açıklamalar, yazılımın kaynak kodu ve test sonuçlarıyla doğrulanmalıdır.

---

## ✨ Öne Çıkan Özellikler

| Özellik | Açıklama |
|---|---|
| 🔎 Fiziksel disk listesi | USB ve harici diskleri algılamayı hedefler. |
| 🧹 Disk temizleme | Tam hazırlık modunda mevcut bölüm yapısını siler. |
| 🔄 MBR dönüşümü | GPT bölüm tablosunu MBR olarak yeniden oluşturur. |
| 💽 FAT32 biçimlendirme | Seçilen bölümü FAT32 olarak biçimlendirir. |
| 📦 Küme boyutu seçimi | Uygun küme boyutunu seçmeye olanak tanır. |
| 🏷️ Birim etiketi | Diske `PS3_USB` gibi bir ad atanabilir. |
| 📁 Otomatik klasör oluşturma | PS3 için yaygın klasörleri oluşturabilir. |
| 🔐 Yönetici yetkisi | Disk işlemleri için gerekli Windows izinleriyle çalışır. |

---

## 🛠️ GUIFormat Neden Diskleri Görmeyebilir?

GUIFormat (FAT32Format) gibi araçlarda bazı disklerde aşağıdaki sorunlarla karşılaşılabilir:

### 1. 🔄 GPT ve MBR bölüm tablosu

- Modern Windows sistemlerinde diskler GPT olarak yapılandırılmış olabilir.
- Bazı eski araçlar bölüm tablosunu değiştirmez; genellikle mevcut birim veya sürücü harfi üzerinden çalışır.
- Diskin MBR veya GPT olması tek başına PS3 uyumluluğunu belirlemez; dosya sistemi, bölüm yapısı ve diğer uyumluluk koşulları da önemlidir.

### 2. 💿 Sürücü harfi atanmamış diskler

- Yeni veya temizlenmiş disklerde sürücü harfi bulunmayabilir.
- Bu durum bazı biçimlendirme araçlarının diski listede göstermemesine neden olabilir.

### 3. 🧩 RAW veya tanınmayan bölümler

- RAW durumundaki bölümler Windows tarafından normal bir dosya sistemi olarak okunamaz.
- Bölüm yapısının yeniden oluşturulması gerekebilir.

### 4. 🔒 `GetLastError() = 32` hatası

Bu hata genellikle bir dosya veya aygıtın başka bir işlem tarafından kullanımda olduğunu gösterir.

- Windows Gezgini veya başka bir uygulama aygıtı kullanıyor olabilir.
- Arka plandaki işlemler diske erişimi engelleyebilir.
- Yönetici yetkileri ve aygıt erişim koşulları kontrol edilmelidir.

> ℹ️ FAT32 Pro Formatter bu sorunları azaltmayı hedefler. Her donanım, disk veya Windows yapılandırmasında hatasız çalışma garantisi verilemez.

---

## 🚀 Kurulum ve Kullanım

### 📥 1. Uygulamayı başlatın

Proje paketinde bulunan dosyalardan birini çalıştırın:

- `Baslat.bat`
- `FAT32_Pro_Format.exe`

Disk işlemleri için yönetici izinleri gerekebilir. Windows UAC penceresini yalnızca çalıştırdığınız uygulamanın kaynağına güveniyorsanız onaylayın.

### 🔍 2. Hazırlanacak diski seçin

Listeden USB belleğinizi veya harici diskinizi seçin.

Örnek:

`Disk 3 — 500 GB`

**Disk numarasını ve kapasitesini dikkatlice kontrol edin.** Yanlış diski seçmek veri kaybına neden olabilir.

### ⚙️ 3. Format seçeneklerini ayarlayın

Örnek yapılandırma:

| Ayar | Örnek değer |
|---|---|
| Disk hazırlama modu | Tam Disk Hazırlığı |
| Bölüm tablosu | MBR |
| Dosya sistemi | FAT32 |
| Birim etiketi | `PS3_USB` |
| Küme boyutu | 32 KB |

Kullanılan seçenekler, uygulamanın sunduğu gerçek ayarlara göre değişebilir.

### 📁 4. PS3 klasörlerini oluşturun

İsteğe bağlı klasör oluşturma özelliği etkinleştirildiğinde aşağıdaki dizinler hazırlanabilir:

```text
PS3_USB/
├── GAMES/
├── PS3ISO/
├── PKG/
└── PS3/
    └── UPDATE/
```

**Not:** Bu klasörler yaygın kullanım senaryolarına yöneliktir. Her klasör her PS3 kullanım yöntemi için gerekli değildir; içeriklerin yerleşimi kullanılan yazılıma ve yönteme göre değişebilir.

### ▶️ 5. Biçimlendirmeyi başlatın

**🚀 FAT32 FORMATI VE HAZIRLIĞI BAŞLAT** düğmesine basın ve işlem onayını dikkatlice okuyun.

İşlem tamamlandıktan sonra diskin Windows tarafından tanındığını kontrol edin.

---

## ⚠️ Önemli Uyarılar

> **🚨 DİKKAT: TAM DİSK HAZIRLIĞI VERİLERİ SİLER!**

- ❌ Seçilen diskteki mevcut bölümler ve veriler silinebilir.
- 💾 İşleme başlamadan önce önemli dosyalarınızı yedekleyin.
- 🔌 Biçimlendirme sırasında diskin bağlantısını kesmeyin.
- 🖥️ Windows'un kurulu olduğu disk üzerinde işlem yapmayın.
- 🔍 Sistem diski korumasının tek başına yeterli olduğunu varsaymayın; doğru fiziksel diski seçtiğinizi ayrıca doğrulayın.
- 📦 FAT32'de tek bir dosya en fazla yaklaşık **4 GiB eksi 1 bayt** boyutunda olabilir. Daha büyük dosyalar bu dosya sistemine kopyalanamaz.
- 🎮 FAT32 ve MBR kullanmak, her diskin veya her PS3 kullanım yönteminin kesinlikle çalışacağını garanti etmez.

---

## 🖥️ Sistem Gereksinimleri

- 💻 Windows işletim sistemi
- 🔐 Gerekli disk işlemleri için yönetici izinleri
- 🔌 USB bellek, harici HDD veya taşınabilir SSD
- 💾 Disk kapasitesine uygun boş alan ve çalışan bir USB bağlantısı

Desteklenen Windows sürümleri ve uygulamanın ek bağımlılıkları, projenin gerçek sürümünde doğrulanmalıdır.

---

## 🗂️ Proje Dosyaları

Örnek paket yapısı:

```text
FAT32-Pro-Formatter/
├── README.md
├── Baslat.bat
└── FAT32_Pro_Format.exe
```

> Bu yapı örnek olarak verilmiştir. Depoda bulunmayan dosyalar, projenin gerçek içeriğiymiş gibi değerlendirilmemelidir.

---

## 🤝 Katkıda Bulunma

Geliştirme önerileriniz ve hata bildirimleriniz için GitHub Issues bölümünü kullanabilirsiniz.

1. 🐛 Karşılaştığınız hatayı açıklayın.
2. 📝 Windows sürümünüzü ve disk yapılandırmanızı belirtin.
3. 📷 Varsa hata mesajının ekran görüntüsünü ekleyin.
4. 🔧 Çözüm önerilerinizi veya iyileştirmelerinizi paylaşın.

---

## 📜 Lisans

Bu projenin lisansı, depoda bulunan `LICENSE` dosyasına göre belirlenir. Henüz lisans eklenmediyse, kullanım ve dağıtım koşullarını açıklayan uygun bir lisans eklenmesi önerilir.

---

<p align="center">
  💽 <strong>FAT32 Pro Formatter</strong><br>
  <sub>Büyük diskler için pratik FAT32 hazırlığı. 🎮</sub>
</p>
