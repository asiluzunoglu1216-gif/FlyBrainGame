# 🪰 FlyBrainGame: 166.700 Nöronlu Biyolojik Konektom Simülasyonu

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Connectome](https://img.shields.io/badge/Connectome-Janelia%20MaleCNS%20v1.0-green.svg)](https://janelia.org)
[![Engine](https://img.shields.io/badge/3D%20Engine-Panda3D-orange.svg)](https://www.panda3d.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**FlyBrainGame**, gerçek bir yetişkin erkek meyve sineğinin (*Drosophila melanogaster*) tüm merkezi sinir sistemini (Janelia Research Campus **MaleCNS v1.0**) simüle eden, 3 boyutlu yaşayan ekosistem oyunudur.

Bu simülasyonda sineğin kararları önceden programlanmış kural tabanlı bir yapay zeka veya sezgisel kod parçaları tarafından **yönetilmez**. Sineğin her kanat çırpışı, yönelimi, konması, yürümesi, besin araması ve tehlikeden kaçışı; **166.700 biyolojik nöron ve 25.6 milyon sinaptik bağlantıdan oluşan Leaky Integrate-and-Fire (LIF) spiking sinir ağı** tarafından üretilir.

---

## 📑 İçindekiler

- [Öne Çıkan Özellikler](#-öne-çıkan-özellikler)
- [100% Saf Nöral Kontrol (Pure Connectome Control)](#-100-saf-nöral-kontrol-pure-connectome-control)
- [Biyolojik Mimari ve Devreler](#-biyolojik-mimari-ve-devreler)
  - [1. Görsel Algı Sistemi (Visual Looming & Optic Flow)](#1-görsel-algı-sistemi-visual-looming--optic-flow)
  - [2. Koku Algısı ve Yayılım Fiziği (3D Olfactory System)](#2-koku-algısı-ve-yayılım-fiziği-3d-olfactory-system)
  - [3. Tat Duyusu ve Proboscis Refleksi (Gustation & PER)](#3-tat-duyusu-ve-proboscis-refleksi-gustation--per)
  - [4. Mantar Cisimciği ve Çağrışımsal Öğrenme (Mushroom Body Plasticity)](#4-mantar-cisimciği-ve-çağrışımsal-öğrenme-mushroom-body-plasticity)
  - [5. İç Durum ve Fizyoloji (Hunger, Hydration, Energy)](#5-iç-durum-ve-fizyoloji-hunger-hydration-energy)
  - [6. Avcı Kurbağa ve Dil Fırlatma Mekaniği (Frog Predator AI)](#6-avcı-kurbağa-ve-dil-fırlatma-mekaniği-frog-predator-ai)
- [Kurulum](#-kurulum)
- [Oyunu Başlatma ve Kontroller](#-oyunu-başlatma-ve-kontroller)
- [Ekran Göstergeleri (HUD)](#-ekran-göstergeleri-hud)
- [Test ve Bilimsel Doğrulama](#-test-ve-bilimsel-doğrulama)
- [MaleCNS 166.700 Nöron Sınır Denetimi](#-malecns-166700-nöron-sınır-denetimi)
- [Lisans ve Teşekkür](#-lisans-ve-teşekkür)

---

## 🌟 Öne Çıkan Özellikler

- 🧠 **166.700 Nöron, 25.582.938 Sinaps**: Janelia MaleCNS v1.0 tam konnektom grafiği üzerinde Numba JIT çok çekirdekli LIF spiking simülasyonu.
- 🎯 **Sıfır Hileli Fizik**: Sinek asla "otomatik ileri gitme" komutuyla hareket etmez. Sıfır nöron ateşlemesi = Sıfır hız ($v = 0.0\text{ m/s}$).
- 👁️ **Gelişmiş Görsel Yollar**: LC4, LPLC2 tehlike/looming dedektörleri, LC10a küçük hedef izleme devreleri.
- 👃 **Gerçekçi 3D Koku Yayılımı**: Rüzgar sürüklenmesi, mesafe ters-kare düşüşü ve çift antenli konsantrasyon farkı ile yön bulma (tropotaksis).
- 👅 **Tarsal ve Labellar Tat Algısı**: Bacak ve hortum kemoreseptörleri ile besinle fiziksel temas anında tat algılama ve Proboscis Uzatma Refleksi (PER).
- 🍄 **Mantar Cisimciği (Mushroom Body) Belleği**: PAM (ödül) ve PPL1 (ceza) nöromodülatör dopamin devreleriyle yönetilen çağrışımsal sinaptik esneklik; oturumlar ve ölümler arası kalıcı hafıza (`fly_memory_mb.npz`).
- ⚡ **Fiziksel Proboscis Temasıyla Beslenme**: Keyfi yarıçap kontrolleri yerine 3D hortum çarpışma kutusu (collider) besine değdiğinde gerçekleşen gerçek beslenme döngüsü.
- 🐸 **Dinamik Avcı Kurbağalar**: İzleme (`WATCH`) $\to$ Nişan Alma (`AIM`) $\to$ Dil Fırlatma (`TONGUE_STRIKE`, 14 m/s) $\to$ Yakalayıp Çekme (`CATCH_PULL`) fazlarına sahip fiziksel avcı simülasyonu.
- 🎮 **Tam Kamera ve HUD Denetimi**: 3. şahıs takip kamerası ve 6-eksenli serbest seyirci kamerası (Spectator), detaylı nöral telemetri paneli.

---

## 🔬 100% Saf Nöral Kontrol (Pure Connectome Control)

Bu simülasyonun en temel ilkesi **biyolojik dürüstlüktür**:

```
[Dünya / Çevre] ──> [Biyolojik Reseptörler] ──> [166.700 MaleCNS Spiking Ağı] ──> [İnen Motor Nöronlar (DN)] ──> [Fizik Motoru]
```

1. **Hiçbir Kural Tabanlı Yönlendirme Yoktur**: Kod içinde `if hungry: go_to_food()` veya `if frog_near: flee()` gibi yönlendirici mantıklar bulunmaz.
2. **Taban Hız (Cruise Speed) Yoktur**: Sinek motonöronları uyarılmadığı sürece hareket edemez.
3. **Kalkış Saflığı (Takeoff Purity)**: Yerde yürürken belirli bir hıza ulaşıldığı için otomatik uçuşa geçilmez; yalnızca tergotrochanteral motor nöron (TDT / Giant Fiber kalkış devresi) ateşlendiğinde kalkış gerçekleşir.
4. **Matematiksel Doğrulama**: `tests/test_neural_control.py` testi, konektom durdurulduğunda tüm hareketin anında durduğunu ve motor çıkışların tam nedensellikle nöral ateşlemeye bağlı olduğunu kanıtlar.

---

## 🧬 Biyolojik Mimari ve Devreler

### 1. Görsel Algı Sistemi (Visual Looming & Optic Flow)
- **LC4 (Lobula Columna 4)**: Hızla yaklaşan tehditleri (looming) tespit eder; ani kaçış manevrasını tetikler.
- **LPLC2 (Lobula Plate / Lobula Columnar 2)**: Görsel alanda genişleyen nesnelerin optik akışını kodlar.
- **LC10a / LC10b / LC10c**: Hareketli küçük hedefleri (besinler, diğer sinekler) izlemek için yönelim girdisi sağlar.

### 2. Koku Algısı ve Yayılım Fiziği (3D Olfactory System)
- **3D Gauss Plume Modeli**: Besin kaynaklarından çıkan kokular rüzgar vektörü doğrultusunda yayılır ve türbülanslı konsantrasyon gradyanı oluşturur.
- **ORN (Koku Reseptör Nöronları)**: `ORN_DM1` ile `ORN_DM5` popülasyonları uyarılır. Sol ve sağ antenler arasındaki mikroskobik mesafe sayesinde sinek koku kaynağının tarafını algılar ve gradyan boyunca yönelir.

### 3. Tat Duyusu ve Proboscis Refleksi (Gustation & PER)
- **Bacak (Tarsal) Kemoreseptörleri**: Yere konan sinek, bacakları besine temas ettiğinde şekeri (Sweet) veya acıyı (Bitter) algılar.
- **Yürüme Durması (Walking Arrest)**: Şeker algılandığında inen yürüme komutları baskılanır ve sinek yerinde sabitlenir.
- **Proboscis Extension Reflex (PER)**: `MN_Proboscis` motor nöronları ateşlenir ve hortum besine doğru uzanır.
- **Fiziksel Çarpışma ile Beslenme**: Hortum ucu besin yüzeyiyle temas ettiğinde tüketim başlar, açlık azalır ve enerji yenilenir.

### 4. Mantar Cisimciği ve Çağrışımsal Öğrenme (Mushroom Body Plasticity)
- **Kenyon Hücreleri (KC)**: Koku kombinasyonlarını seyrek (sparse) olarak kodlar (~2.000 nöron).
- **MBON (Mushroom Body Output Neurons)**: Yaklaşma veya kaçınma davranışlarını yöneten çıkış yolları.
- **Dopaminerjik Modülasyon**:
  - `PAM`: Besin ve şeker ödülüyle ateşlenir; pozitif çağrışım oluşturur.
  - `PPL1`: Tehdit, kurbağa atağı veya acı tat ile ateşlenir; kaçınma refleksini pekiştirir.
- **Kalıcı Bellek**: Sinaptik ağırlık değişimleri oturumlar arasında `fly_memory_mb.npz` dosyasına kaydedilir. Sineğin yeni doğan reenkarnasyonu önceki deneyimlerini hatırlar.

### 5. İç Durum ve Fizyoloji (Hunger, Hydration, Energy)
- Sineğin açlık (`hunger`), enerji (`energy`) ve susuzluk (`hydration`) seviyeleri sürekli simüle edilir.
- Açlık arttığında koku ve tat duyusal nöronlarının kazancı (gain) yükselir (yiyecek arama motivasyonu artar).
- Enerji tükendiğinde uçuş itki gücü zayıflar ve sinek dinlenmek üzere yüzeylere konmaya zorlanır.

### 6. Avcı Kurbağa ve Dil Fırlatma Mekaniği (Frog Predator AI)
- Gölet ve sulak alan çevresinde konumlanmış avcı kurbağalar gerçekçi bir biyolojik avlanma döngüsüne sahiptir:
  1. **WATCH**: Sineğin varlığını tespit eder, gözlerini ve gövdesini sineğe çevirir.
  2. **AIM**: Dil fırlatma açısını ve mesafesini hesaplar.
  3. **TONGUE_STRIKE**: Dilini 14 m/s hızla sineğe doğru fırlatır.
  4. **CATCH_PULL**: Dil sineğe fiziksel olarak çarparsa sinek yakalanır ve kurbağanın ağzına çekilir.
  5. **FLY EATEN**: Avlanma tamamlanır ve yaşam özeti ekranı açılır.
- Sinek görsel alanda kurbağanın dilini veya ani hareketini tespit ederse, `DNp01` Giant Fiber kaçış refleksiyle son anda havalanıp kurtulabilir.

---

## 💻 Kurulum

### Sistem Gereksinimleri
- **İşletim Sistemi**: Windows 10/11, Linux veya macOS
- **Python Sürümü**: Python 3.12 (Panda3D ve Numba JIT için kararlı sürüm)
- **Donanım**: Özel GPU zorunlu değildir. Intel Iris Xe ve standart çok çekirdekli modern işlemcilerde akıcı 60 FPS grafik ve ~30-50 Hz konektom çözünürlüğü elde edilir.

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/asiluzunoglu1216-gif/FlyBrainGame.git
cd FlyBrainGame
```

### 2. Sanal Ortamı Oluşturun ve Etkinleştirin
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
pip install panda3d numba numpy scipy
```

*Not: İlk çalıştırmada ~260 MB boyutundaki derlenmiş Janelia MaleCNS konektom dosyaları (`brain.npz` ve `weights.npz`) otomatik olarak algılanır.*

---

## 🎮 Oyunu Başlatma ve Kontroller

Simülasyonu başlatmak için:

```powershell
.\.venv\Scripts\python.exe run_game.py
```

### Tuş Takımı

| Tuş | Kategori | İşlev |
|:---:|:---|:---|
| **F** | Kamera | **Kamera Modu Değiştir**: 3. Şahıs Takip (Chase) $\leftrightarrow$ Serbest Seyirci (Spectator) |
| **W, A, S, D** | Spectator | İleri, Sola, Geri, Sağa serbest kamera hareketi |
| **Space** | Karma | *Chase:* Sineği güvenli alana sıfırlar. *Spectator:* Kamerayı yükseltir. |
| **Shift / Ctrl** | Spectator | Kamerayı aşağı alçaltır |
| **Fare Hareketi** | Spectator | Serbest kamera bakış açısı (Pitch & Yaw) |
| **Fare Tekerleği** | Spectator | Kamera hareket hızını ayarlar (5 – 70 birim/sn) |
| **F1** | Kontrol Modu | **Connectome Control (Varsayılan)**: Sineği gerçek 166.700 nöronlu MaleCNS yönetir |
| **F2** | Kontrol Modu | **Scripted Baseline Bot**: Karşılaştırma amaçlı klasik yapay zeka |
| **F3** | Duyu Modu | `FEATURE_MODE` ve deneysel `EYE_MODE` arasında geçiş |
| **R** | Yaşam | **Reincarnation (Yeniden Doğuş)**: Bellekleri koruyarak yeni bir sinek hayatı başlatır |
| **Esc** | Sistem | Simülasyonu kapatır ve telemetriyi kaydeder |

---

## 📊 Ekran Göstergeleri (HUD)

- **Render FPS**: Grafik motorunun saniyedeki kare hızı (~60 FPS).
- **Brain Step Hz**: Konektom ağının saniyede işlenen adım frekansı.
- **Latency (ms)**: 166.700 nöronun çözülme adım süresi (~25-38 ms).
- **Life Stats**:
  - `ALIVE`: Hayatta kalınan süre (saniye).
  - `FOOD`: Tüketilen meyve sayısı.
  - `DIST`: Katedilen toplam mesafe.
  - `LANDINGS`: Yüzeylere iniş sayısı.
  - `THREATS / ESCAPES`: Karşılaşılan kurbağa saldırıları ve başarılı kaçışlar.
- **Physiology**:
  - `HUNGER`: Açlık yüzdesi.
  - `ENERGY`: Kalan uçuş enerjisi.
  - `PROBOSCIS`: Hortumun uzama oranı (%0 - %100).
- **Nöral Ateşleme Frekansları**:
  - `DNp01 (L/R)`: Giant Fiber kaçış ateşlemesi.
  - `DNa02 (L/R)`: Dönüş ve yönlendirme motonöronları.
  - `DNg100`: İleri itki ateşlemesi.
  - `MDN`: Geri çekilme ve frenleme.

---

## 🧪 Test ve Bilimsel Doğrulama

Konektom bütünlüğünü, nöral saflığı ve biyolojik mekanizmaları test etmek için hazır test takımları:

```powershell
# 1. Biyolojik Devre Doğrulama Testi (LC4/LPLC2 -> DNp01, LC10a -> DNa02)
.\.venv\Scripts\python.exe -m unittest tests/test_circuits.py -v

# 2. Nöral Nedensellik ve Hile Karşıtı Test (0 spike -> 0 hız doğrulaması)
.\.venv\Scripts\python.exe -m unittest tests/test_neural_control.py -v

# 3. Beslenme, Proboscis ve Kalkış Saflığı Doğrulaması
.\.venv\Scripts\python.exe -m unittest tests/test_feeding_takeoff_purity.py -v

# 4. Kurbağa Avcısı ve Fiziksel Dil Teması Doğrulaması
.\.venv\Scripts\python.exe -m unittest tests/test_frog_fair_live.py -v

# 5. Mantar Cisimciği Çağrışımsal Öğrenme ve Kalıcılık Testi
.\.venv\Scripts\python.exe -m unittest tests/test_memory_plasticity.py -v

# 6. 10 Tohumlu Tam Yaşam Ekosistem Benchmark'ı
.\.venv\Scripts\python.exe tests/run_10_seed_foraging_benchmark.py
```

---

## 📋 MaleCNS 166.700 Nöron Sınır Denetimi

Janelia MaleCNS v1.0 veri tabanındaki tüm **166.700 nöron** simülasyon grafiğinde aktif olarak yer almaktadır:

- **Toplam Hücre Tipi**: 11.863
- **Doğrulanmış Duyusal Giriş Tipleri**: Optik lob projeksiyonları (`LC4`, `LPLC2`, `LC9`, `LC10a-c`), Antenal koku nöronları (`ORN_DM1-5`), Bacak ve hortum tat nöronları (`BM_Taste`), Halter ve Johnston organı mekanoreseptörleri.
- **Doğrulanmış Motor Çıkış Tipleri**: Giant Fiber (`DNp01`), Yönlendirme (`DNa02`), İleri itki (`DNg100`), Geri çekilme (`MDN`), Yürüme (`DNp09`), Proboscis (`MN_Proboscis`), Kalkış (`MN_Takeoff`).
- **Ayrıntılı Denetim Raporu**: `reports/full_166700_neuron_interface_audit.json` ve `reports/biological_evidence.md` dosyalarında tüm nöron sınıflarının literatür karşılıkları belgelenmiştir.

---

## 📄 Lisans ve Teşekkür

- **Konektom Verisi**: [Janelia Research Campus](https://www.janelia.org) - FlyEM Project (MaleCNS v1.0).
- **LIF Simülasyon Çekirdeği**: `alextitonis/fly.ai` ve Ornata Fly64 temeli üzerine geliştirilmiştir.
- **Geliştirici**: [asiluzunoglu1216-gif](https://github.com/asiluzunoglu1216-gif)

Bu proje MIT Lisansı altında sunulmaktadır.
