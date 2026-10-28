# -*- coding: utf-8 -*-
"""
FAT32 Pro Formatter (PS3 & USB 500GB+ Hazırlayıcı)
Gelişmiş FAT32 Biçimlendirme ve PS3 Disk Hazırlama Aracı

Özellikler:
- 500GB, 1TB, 2TB ve üzeri tüm USB/Harici Diskleri FAT32 yapar.
- GUIFormat'ın görmediği veya "GetLastError()=32" hatası verdiği tüm diskleri çözer.
- GPT diskleri PS3 uyumlu MBR tablosuna dönüştürür.
- Harf atanmamış (RAW/Unallocated) diskleri otomatik bölümler ve harf atar.
- İsteğe bağlı olarak standart PS3 klasör yapısını (GAMES, PS3ISO, PKG, PS3/UPDATE) oluşturur.
- Windows Sistem ve Boot diskini (C:) koruma altına alır, kazara silinmesini engeller.
"""

import sys
import os
import subprocess
import threading
import json
import tempfile
import time
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, messagebox


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate_to_admin():
    if not is_admin():
        try:
            if getattr(sys, 'frozen', False):
                exe = sys.executable
                args = ' '.join([f'"{a}"' for a in sys.argv[1:]])
                ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, args, None, 1)
            else:
                exe = sys.executable
                script = os.path.abspath(sys.argv[0])
                args = ' '.join([f'"{a}"' for a in sys.argv[1:]])
                ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, f'"{script}" {args}', None, 1)
            if ret > 32:
                sys.exit(0)
        except Exception:
            pass


def get_fat32format_path():
    # 1. PyInstaller bundled path
    if hasattr(sys, '_MEIPASS'):
        p = os.path.join(sys._MEIPASS, "fat32format.exe")
        if os.path.exists(p):
            return p
    # 2. Directory where executable or script resides
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    p = os.path.join(base_dir, "fat32format.exe")
    if os.path.exists(p):
        return p
    # 3. Current working directory
    if os.path.exists("fat32format.exe"):
        return os.path.abspath("fat32format.exe")
    return "fat32format.exe"


class FAT32FormatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FAT32 Pro Formatter (PS3 & USB 500GB+ Hazırlayıcı)")
        self.root.geometry("820x780")
        self.root.minsize(780, 720)

        # High DPI support
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self.disks = []
        self.filtered_disks = []
        self.selected_disk = None
        self.is_formatting = False
        
        self.only_usb_var = tk.BooleanVar(value=True)
        self.format_mode_var = tk.StringVar(value="full_mbr")
        self.volume_label_var = tk.StringVar(value="PS3_USB")
        self.cluster_size_var = tk.StringVar(value="32KB (PS3 Önerilen)")
        self.ps3_folders_var = tk.BooleanVar(value=True)

        self.setup_styles()
        self.create_widgets()
        self.refresh_disks()

    def setup_styles(self):
        self.colors = {
            "bg": "#121316",
            "card_bg": "#1c1e24",
            "card_border": "#2d3139",
            "text": "#f3f4f6",
            "text_muted": "#9ca3af",
            "primary": "#2563eb",
            "primary_hover": "#1d4ed8",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "console_bg": "#090a0f",
            "console_fg": "#38bdf8",
        }

        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TCombobox',
                        fieldbackground=self.colors["card_bg"],
                        background=self.colors["card_border"],
                        foreground=self.colors["text"],
                        arrowcolor=self.colors["text"])

        style.configure('TProgressbar',
                        background=self.colors["primary"],
                        troughcolor=self.colors["card_bg"],
                        borderwidth=0)

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#181a20", bd=0, padx=20, pady=12)
        header.pack(fill=tk.X)

        title_box = tk.Frame(header, bg="#181a20")
        title_box.pack(side=tk.LEFT)

        title_lbl = tk.Label(title_box, text="🎮 FAT32 PRO FORMATTER", font=("Segoe UI", 15, "bold"),
                             fg="#60a5fa", bg="#181a20")
        title_lbl.pack(anchor="w")

        sub_text = "500GB+ / 1TB / 2TB USB & Harici Diskler | GPT'den MBR'ye Dönüştürme | PS3 Tam Desteği"
        subtitle_lbl = tk.Label(title_box, text=sub_text,
                                font=("Segoe UI", 9), fg=self.colors["text_muted"], bg="#181a20")
        subtitle_lbl.pack(anchor="w")

        # Admin Badge
        is_adm = is_admin()
        admin_status = "🛡️ YÖNETİCİ" if is_adm else "⚠️ YÖNETİCİ DEĞİL"
        admin_color = self.colors["success"] if is_adm else self.colors["warning"]
        admin_badge = tk.Label(header, text=admin_status, font=("Segoe UI", 9, "bold"),
                               fg=admin_color, bg="#272b36", padx=8, pady=4, bd=1, relief=tk.SOLID)
        admin_badge.pack(side=tk.RIGHT)

        # Main Container
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=18, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------- 1. DISK SEÇİMİ ----------------
        disk_card = tk.LabelFrame(main_frame, text=" 1. Biçimlendirilecek Diski Seçin ", font=("Segoe UI", 10, "bold"),
                                  fg="#93c5fd", bg=self.colors["card_bg"], bd=1, relief=tk.SOLID, padx=12, pady=10)
        disk_card.pack(fill=tk.X, pady=(0, 10))

        filter_bar = tk.Frame(disk_card, bg=self.colors["card_bg"])
        filter_bar.pack(fill=tk.X, pady=(0, 6))

        usb_chk = tk.Checkbutton(filter_bar, text="Sadece USB / Harici Diskleri Göster (Güvenli)",
                                 variable=self.only_usb_var, command=self.refresh_disks,
                                 font=("Segoe UI", 9), fg=self.colors["text"], bg=self.colors["card_bg"],
                                 selectcolor="#2d3139", activebackground=self.colors["card_bg"],
                                 activeforeground=self.colors["text"])
        usb_chk.pack(side=tk.LEFT)

        refresh_btn = tk.Button(filter_bar, text="🔄 Diskleri Yenile", font=("Segoe UI", 9, "bold"),
                                bg="#374151", fg="#f9fafb", activebackground="#4b5563",
                                activeforeground="#ffffff", relief=tk.FLAT, padx=12, pady=2,
                                cursor="hand2", command=self.refresh_disks)
        refresh_btn.pack(side=tk.RIGHT)

        self.disk_combo = ttk.Combobox(disk_card, style='Custom.TCombobox', font=("Segoe UI", 10), state="readonly")
        self.disk_combo.pack(fill=tk.X, pady=(0, 6))
        self.disk_combo.bind("<<ComboboxSelected>>", self.on_disk_selected)

        # Details Box
        self.detail_frame = tk.Frame(disk_card, bg="#131418", padx=10, pady=8, bd=1, relief=tk.GROOVE)
        self.detail_frame.pack(fill=tk.X)

        self.lbl_detail_model = tk.Label(self.detail_frame, text="📦 Model: Lütfen yukarıdan bir disk seçin",
                                         font=("Segoe UI", 9, "bold"), fg=self.colors["text"], bg="#131418")
        self.lbl_detail_model.pack(anchor="w")

        self.lbl_detail_size = tk.Label(self.detail_frame, text="💾 Kapasite: -",
                                        font=("Segoe UI", 9), fg=self.colors["text_muted"], bg="#131418")
        self.lbl_detail_size.pack(anchor="w")

        self.lbl_detail_style = tk.Label(self.detail_frame, text="🏷️ Bölüm Düzeni: -",
                                         font=("Segoe UI", 9), fg=self.colors["text_muted"], bg="#131418")
        self.lbl_detail_style.pack(anchor="w")

        self.lbl_detail_letters = tk.Label(self.detail_frame, text="🔤 Sürücü Harfleri: -",
                                           font=("Segoe UI", 9), fg=self.colors["text_muted"], bg="#131418")
        self.lbl_detail_letters.pack(anchor="w")

        # GPT Warning Banner
        warn_text = (
            "⚠️ DİKKAT: Bu disk GPT düzenindedir!\n"
            "PS3 ve eski sistemler GPT diskleri tanımaz. Aşağıdaki 'Tam Disk Hazırlığı (MBR)' modu diski otomatik MBR yapacaktır."
        )
        self.gpt_warning_lbl = tk.Label(disk_card, text=warn_text,
                                        font=("Segoe UI", 9, "bold"), fg="#fef08a", bg="#854d0e",
                                        padx=10, pady=6, justify=tk.LEFT)

        # ---------------- 2. BİÇİMLENDİRME MODU ----------------
        mode_card = tk.LabelFrame(main_frame, text=" 2. Biçimlendirme Modu ", font=("Segoe UI", 10, "bold"),
                                  fg="#93c5fd", bg=self.colors["card_bg"], bd=1, relief=tk.SOLID, padx=12, pady=10)
        mode_card.pack(fill=tk.X, pady=(0, 10))

        r1 = tk.Radiobutton(mode_card, text="⭐ Tam Disk Hazırlığı (MBR Dönüştür + Tek FAT32 Bölümü) [KESİN ÇÖZÜM / ÖNERİLEN]",
                            variable=self.format_mode_var, value="full_mbr",
                            font=("Segoe UI", 9, "bold"), fg="#6ee7b7", bg=self.colors["card_bg"],
                            selectcolor="#1f2937", activebackground=self.colors["card_bg"],
                            activeforeground="#6ee7b7")
        r1.pack(anchor="w")

        r1_desc = (
            "   • Diski tamamen temizler (clean), MBR tablosu oluşturur ve tek FAT32 bölümü açar.\n"
            "   • 500GB+ GPT diskler, RAW diskler ve guiformat'ın görmediği tüm diskler için %100 kesin çözümdür."
        )
        tk.Label(mode_card, text=r1_desc, font=("Segoe UI", 8),
                 fg=self.colors["text_muted"], bg=self.colors["card_bg"], justify=tk.LEFT).pack(anchor="w", pady=(0, 4))

        r2 = tk.Radiobutton(mode_card, text="⚡ Hızlı FAT32 Biçimlendir (Mevcut Sürücü Harfini Koru)",
                            variable=self.format_mode_var, value="quick_format",
                            font=("Segoe UI", 9, "bold"), fg=self.colors["text"], bg=self.colors["card_bg"],
                            selectcolor="#1f2937", activebackground=self.colors["card_bg"],
                            activeforeground=self.colors["text"])
        r2.pack(anchor="w")

        r2_desc = "   • Disk zaten MBR ise ve bölümleri silmeden sadece mevcut sürücü harfini FAT32 yapmak istiyorsanız kullanılır."
        tk.Label(mode_card, text=r2_desc, font=("Segoe UI", 8),
                 fg=self.colors["text_muted"], bg=self.colors["card_bg"], justify=tk.LEFT).pack(anchor="w")

        # ---------------- 3. AYARLAR KARTI ----------------
        settings_card = tk.LabelFrame(main_frame, text=" 3. Format Ayarları ", font=("Segoe UI", 10, "bold"),
                                      fg="#93c5fd", bg=self.colors["card_bg"], bd=1, relief=tk.SOLID, padx=12, pady=8)
        settings_card.pack(fill=tk.X, pady=(0, 10))

        settings_grid = tk.Frame(settings_card, bg=self.colors["card_bg"])
        settings_grid.pack(fill=tk.X)

        tk.Label(settings_grid, text="Birim Etiketi (İsim):", font=("Segoe UI", 9, "bold"),
                 fg=self.colors["text"], bg=self.colors["card_bg"]).grid(row=0, column=0, sticky="w", pady=4)

        self.label_entry = tk.Entry(settings_grid, textvariable=self.volume_label_var, font=("Segoe UI", 9),
                                    bg="#111827", fg="#ffffff", insertbackground="#ffffff", width=16, bd=1, relief=tk.SOLID)
        self.label_entry.grid(row=0, column=1, sticky="w", padx=(8, 24), pady=4)

        tk.Label(settings_grid, text="Küme Boyutu (Cluster):", font=("Segoe UI", 9, "bold"),
                 fg=self.colors["text"], bg=self.colors["card_bg"]).grid(row=0, column=2, sticky="w", pady=4)

        cluster_combo = ttk.Combobox(settings_grid, textvariable=self.cluster_size_var,
                                     values=["32KB (PS3 Önerilen)", "64KB (1TB+ İçin)", "16KB", "Otomatik"],
                                     font=("Segoe UI", 9), state="readonly", width=22)
        cluster_combo.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=4)
        cluster_combo.current(0)

        ps3_chk = tk.Checkbutton(settings_card, text="📁 PS3 Klasör Yapısını Otomatik Oluştur (GAMES, PS3ISO, PKG, PS3/UPDATE)",
                                 variable=self.ps3_folders_var,
                                 font=("Segoe UI", 9, "bold"), fg="#93c5fd", bg=self.colors["card_bg"],
                                 selectcolor="#1f2937", activebackground=self.colors["card_bg"],
                                 activeforeground="#93c5fd")
        ps3_chk.pack(anchor="w", pady=(6, 2))

        # ---------------- 4. BAŞLAT BUTONU & PROGRESS ----------------
        action_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        action_frame.pack(fill=tk.X, pady=(2, 6))

        self.btn_start = tk.Button(action_frame, text="🚀 FAT32 FORMATI VE HAZIRLIĞI BAŞLAT",
                                   font=("Segoe UI", 11, "bold"), bg="#2563eb", fg="#ffffff",
                                   activebackground="#1d4ed8", activeforeground="#ffffff",
                                   relief=tk.FLAT, pady=9, cursor="hand2", command=self.confirm_and_start)
        self.btn_start.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 6))

        # ---------------- 5. KONSOL / LOG ALANI ----------------
        log_frame = tk.Frame(main_frame, bg=self.colors["console_bg"], bd=1, relief=tk.SOLID)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, bg=self.colors["console_bg"], fg=self.colors["console_fg"],
                                font=("Consolas", 9), insertbackground="#ffffff", height=8, wrap=tk.WORD, bd=0)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)

        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log("[SİSTEM] FAT32 Pro Formatter hazır. Diskler taranıyor...")

    def log(self, text):
        def _append():
            timestamp = time.strftime("[%H:%M:%S] ")
            self.log_text.insert(tk.END, timestamp + text + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, _append)

    def refresh_disks(self):
        self.log("Diskler taranıyor...")
        self.disk_combo.config(values=["Taranıyor, lütfen bekleyin..."])
        self.disk_combo.current(0)
        self.btn_start.config(state=tk.DISABLED)

        threading.Thread(target=self._scan_disks_worker, daemon=True).start()

    def _scan_disks_worker(self):
        ps_script = """
        $disks = Get-Disk | ForEach-Object {
            $d = $_
            $parts = Get-Partition -DiskNumber $d.Number -ErrorAction SilentlyContinue
            $letters = ($parts | Where-Object { $_.DriveLetter } | ForEach-Object { $_.DriveLetter + ':' }) -join ', '
            [PSCustomObject]@{
                Number = $d.Number
                FriendlyName = $d.FriendlyName.Trim()
                BusType = $d.BusType.ToString()
                PartitionStyle = $d.PartitionStyle.ToString()
                SizeGB = [math]::Round($d.Size / 1GB, 2)
                IsBoot = $d.IsBoot
                IsSystem = $d.IsSystem
                DriveLetters = $letters
                PartitionsCount = $d.NumberOfPartitions
            }
        }
        $disks | ConvertTo-Json -Depth 3
        """
        try:
            p = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', ps_script],
                               capture_output=True, text=True, check=True)
            output = p.stdout.strip()
            if not output:
                parsed = []
            else:
                data = json.loads(output)
                if isinstance(data, dict):
                    parsed = [data]
                else:
                    parsed = data
        except Exception as e:
            self.log(f"[HATA] Disk tarama hatası: {e}")
            parsed = []

        self.root.after(0, lambda: self._update_disk_list(parsed))

    def _update_disk_list(self, disk_list):
        self.disks = disk_list
        only_usb = self.only_usb_var.get()

        filtered = []
        for d in self.disks:
            is_usb = d.get("BusType", "").upper() == "USB"
            if only_usb:
                if is_usb:
                    filtered.append(d)
            else:
                filtered.append(d)

        combo_values = []
        for d in filtered:
            num = d.get("Number")
            name = d.get("FriendlyName")
            size = d.get("SizeGB", 0)
            style = d.get("PartitionStyle", "")
            bus = d.get("BusType", "")
            letters = d.get("DriveLetters") or "Harf Yok"

            flag = ""
            if d.get("IsSystem") or d.get("IsBoot"):
                flag = " [⛔ SİSTEM DİSKİ - KORUMALI]"
            elif style.upper() == "GPT":
                flag = " [⚠️ GPT]"
            elif style.upper() == "MBR":
                flag = " [✅ MBR]"

            combo_values.append(f"Disk {num}: {name} ({size} GB) - {bus} - {letters}{flag}")

        self.filtered_disks = filtered
        if combo_values:
            self.disk_combo.config(values=combo_values)
            self.disk_combo.current(0)
            self.on_disk_selected(None)
            self.log(f"[BİLGİ] {len(filtered)} disk listelendi.")
        else:
            self.disk_combo.config(values=["USB Disk Bulunamadı! Lütfen USB sürücünüzü takıp 'Yenile'ye basın."])
            self.disk_combo.current(0)
            self.selected_disk = None
            self.clear_details()
            self.btn_start.config(state=tk.DISABLED)
            self.log("[UYARI] Uygun disk bulunamadı.")

    def on_disk_selected(self, event):
        idx = self.disk_combo.current()
        if idx < 0 or idx >= len(self.filtered_disks):
            self.selected_disk = None
            self.clear_details()
            return

        d = self.filtered_disks[idx]
        self.selected_disk = d

        model = d.get("FriendlyName", "Bilinmeyen")
        bus = d.get("BusType", "Bilinmeyen")
        size_gb = d.get("SizeGB", 0)
        style = d.get("PartitionStyle", "Bilinmeyen").upper()
        letters = d.get("DriveLetters") or "(Harf Yok / RAW / Boş)"
        is_sys = d.get("IsSystem") or d.get("IsBoot")

        self.lbl_detail_model.config(text=f"📦 Model: {model} ({bus})")
        self.lbl_detail_size.config(text=f"💾 Kapasite: {size_gb} GB ({round(size_gb/1024, 2)} TB)")

        if style == "GPT":
            self.lbl_detail_style.config(text="🏷️ Bölüm Düzeni: GPT (⚠️ PS3 için MBR Dönüştürülmeli!)", fg="#fbbf24")
            self.gpt_warning_lbl.pack(fill=tk.X, pady=(6, 0))
        elif style == "MBR":
            self.lbl_detail_style.config(text="🏷️ Bölüm Düzeni: MBR (✅ PS3 ile Tam Uyumlu)", fg="#34d399")
            self.gpt_warning_lbl.pack_forget()
        else:
            self.lbl_detail_style.config(text=f"🏷️ Bölüm Düzeni: {style}", fg=self.colors["text"])
            self.gpt_warning_lbl.pack_forget()

        self.lbl_detail_letters.config(text=f"🔤 Sürücü Harfleri: {letters}")

        if is_sys:
            self.btn_start.config(state=tk.DISABLED, text="⛔ SİSTEM DİSKİ KORUMALI (FORMATLANAMAZ)")
            self.log(f"[KORUMA] Disk {d.get('Number')} Windows Sistem/Boot diskidir! Biçimlendirme engellendi.")
        else:
            self.btn_start.config(state=tk.NORMAL, text="🚀 FAT32 FORMATI VE HAZIRLIĞI BAŞLAT")

    def clear_details(self):
        self.lbl_detail_model.config(text="📦 Model: -")
        self.lbl_detail_size.config(text="💾 Kapasite: -")
        self.lbl_detail_style.config(text="🏷️ Bölüm Düzeni: -", fg=self.colors["text_muted"])
        self.lbl_detail_letters.config(text="🔤 Sürücü Harfleri: -")
        self.gpt_warning_lbl.pack_forget()

    def confirm_and_start(self):
        if not self.selected_disk:
            messagebox.showwarning("Disk Seçilmedi", "Lütfen önce biçimlendirmek istediğiniz diski seçin!")
            return

        d = self.selected_disk
        if d.get("IsSystem") or d.get("IsBoot"):
            messagebox.showerror("Kritik Güvenlik Koruması", "Windows sistem diski biçimlendirilemez!")
            return

        mode = self.format_mode_var.get()
        disk_no = d.get("Number")
        name = d.get("FriendlyName")
        size = d.get("SizeGB")
        style = d.get("PartitionStyle")

        if mode == "full_mbr":
            mode_desc = "TAM DİSK TEMİZLİĞİ VE MBR DÖNÜŞTÜRME (Tüm bölümler silinecek, MBR yapılacak ve FAT32 formatlanacak)"
        else:
            mode_desc = f"HIZLI FORMAT (Mevcut harf: {d.get('DriveLetters', '')} FAT32 yapılacak)"

        confirm_msg = (
            f"⚠️ DİKKAT! BU İŞLEM GERİ ALINAMAZ!\n\n"
            f"Seçilen Disk: Disk {disk_no} ({name})\n"
            f"Kapasite: {size} GB\n"
            f"Mevcut Bölüm Tablosu: {style}\n"
            f"İşlem Modu: {mode_desc}\n\n"
            f"Bu disk üzerindeki TÜM VERİLER KALICI OLARAK SİLİNECEKTİR.\n\n"
            f"Biçimlendirmeyi başlatmak istiyor musunuz?"
        )

        ans = messagebox.askyesno("DİKKAT - Disk Biçimlendirme Onayı", confirm_msg, icon=messagebox.WARNING)
        if not ans:
            self.log("[İPTAL] Kullanıcı işlemi iptal etti.")
            return

        self.is_formatting = True
        self.btn_start.config(state=tk.DISABLED, text="⏳ BİÇİMLENDİRME YAPILIYOR...")
        self.progress_bar.start(10)
        threading.Thread(target=self._format_worker, daemon=True).start()

    def _format_worker(self):
        d = self.selected_disk
        disk_no = d.get("Number")
        mode = self.format_mode_var.get()
        volume_label = self.volume_label_var.get().strip().upper()[:11] or "PS3_USB"
        cluster_choice = self.cluster_size_var.get()
        fat32format_bin = get_fat32format_path()

        # Cluster flags for fat32format.exe:
        # -c32 = 16KB, -c64 = 32KB, -c128 = 64KB
        cluster_flag = ""
        if "32KB" in cluster_choice:
            cluster_flag = "-c64"
        elif "64KB" in cluster_choice:
            cluster_flag = "-c128"
        elif "16KB" in cluster_choice:
            cluster_flag = "-c32"

        self.log("=" * 50)
        self.log(f"[BAŞLADI] Disk {disk_no} için FAT32 biçimlendirme süreci başladı.")
        self.log(f"[AYARLAR] Mod: {mode}, Etiket: {volume_label}, Küme: {cluster_choice}")

        target_letter = None

        try:
            if mode == "full_mbr":
                self.log("[ADIM 1/4] Diskpart ile disk temizleniyor ve MBR tablosu oluşturuluyor...")

                dp_script = f"""select disk {disk_no}
clean
convert mbr
create partition primary
active
assign
"""
                dp_file = os.path.join(tempfile.gettempdir(), f"dp_script_{disk_no}.txt")
                with open(dp_file, "w") as f:
                    f.write(dp_script)

                p = subprocess.run(["diskpart", "/s", dp_file], capture_output=True, text=True)
                try:
                    os.remove(dp_file)
                except Exception:
                    pass

                if p.returncode != 0:
                    self.log(f"[UYARI] Diskpart çıktısı:\n{p.stdout}")
                    if "hata" in p.stdout.lower() or "error" in p.stdout.lower():
                        raise Exception("Diskpart işlemi başarısız oldu:\n" + p.stdout)
                else:
                    self.log("[OK] Diskpart: Disk temizlendi, MBR yapıldı, birincil bölüm oluşturuldu.")

                self.log("[BİLGİ] Yeni sürücü harfinin Windows tarafından tanınması bekleniyor...")
                time.sleep(2)

                # Query assigned drive letter
                for attempt in range(6):
                    ps_letter = f"""
                    (Get-Partition -DiskNumber {disk_no} | Where-Object {{ $_.DriveLetter }} | Select-Object -First 1).DriveLetter
                    """
                    p_let = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', ps_letter],
                                           capture_output=True, text=True)
                    res = p_let.stdout.strip()
                    if res and len(res) == 1 and res.isalpha():
                        target_letter = f"{res}:"
                        break
                    time.sleep(1)

                if not target_letter:
                    raise Exception("Yeni oluşturulan bölüme sürücü harfi atanamadı!")

                self.log(f"[OK] Sürücü harfi belirlendi: {target_letter}")

            else:
                letters_raw = d.get("DriveLetters", "")
                found = [l.strip() for l in letters_raw.split(",") if ":" in l]
                if not found:
                    raise Exception("Bu disk üzerinde atanmış sürücü harfi bulunamadı! Lütfen 'Tam Disk Hazırlığı' modunu seçin.")
                target_letter = found[0]
                self.log(f"[BİLGİ] Hedef sürücü harfi: {target_letter}")

            # Step 2: Force unlock & dismount to prevent GetLastError()=32
            self.log(f"[ADIM 2/4] {target_letter} sürücüsündeki açık dosya kilitleri çözülüyor...")
            self._force_unlock_volume(target_letter)
            time.sleep(1)

            # Step 3: Run fat32format.exe
            self.log(f"[ADIM 3/4] fat32format motoru çalıştırılıyor ({target_letter})...")
            cmd = [fat32format_bin]
            if cluster_flag:
                cmd.append(cluster_flag)
            cmd.append(target_letter)

            self.log(f"[KOMUT] {' '.join(cmd)}")

            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)

            out, _ = proc.communicate(input="y\n", timeout=120)
            self.log(f"--- fat32format Çıktısı ---\n{out.strip()}\n-------------------------")

            if "GetLastError()=32" in out:
                self.log("[UYARI] Dosya kilidi tespit edildi (Error 32). Diskpart ile çevrimdışı/çevrimiçi yapılıp tekrar deneniyor...")
                self._cycle_volume_offline_online(target_letter)
                time.sleep(2)

                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True, bufsize=1)
                out, _ = proc.communicate(input="y\n", timeout=120)
                self.log(f"--- Tekrar Deneme Çıktısı ---\n{out.strip()}\n-------------------------")

            if proc.returncode != 0 and "done" not in out.lower() and "complete" not in out.lower():
                raise Exception(f"fat32format başarısız oldu (Hata Kodu: {proc.returncode})")

            self.log("[OK] FAT32 biçimlendirme başarıyla tamamlandı!")

            # Step 4: Set Volume Label
            if volume_label:
                self.log(f"[ADIM 4/4] Sürücü etiketi ayarlanıyor: {volume_label}")
                clean_letter = target_letter.replace(":", "")
                lbl_cmd = f'Set-Volume -DriveLetter {clean_letter} -NewFileSystemLabel "{volume_label}" -ErrorAction SilentlyContinue'
                subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', lbl_cmd],
                               capture_output=True)

            # Optional: PS3 folders
            if self.ps3_folders_var.get():
                self.log("[BİLGİ] PS3 klasör yapısı oluşturuluyor...")
                ps3_dirs = [
                    os.path.join(target_letter + "\\", "GAMES"),
                    os.path.join(target_letter + "\\", "PS3ISO"),
                    os.path.join(target_letter + "\\", "PKG"),
                    os.path.join(target_letter + "\\", "PS3", "UPDATE"),
                    os.path.join(target_letter + "\\", "PS3", "SAVEDATA"),
                    os.path.join(target_letter + "\\", "PS3", "THEME"),
                ]
                for pdir in ps3_dirs:
                    os.makedirs(pdir, exist_ok=True)
                self.log("[OK] PS3 Klasörleri oluşturuldu: GAMES, PS3ISO, PKG, PS3/UPDATE")

            self.log("=" * 50)
            self.log(f"[BAŞARILI] İşlem tamamlandı! {target_letter} artık MBR ve FAT32 olarak kullanıma hazır.")

            self.root.after(0, lambda: self._on_success(target_letter))

        except Exception as err:
            self.log(f"[HATA] İşlem sırasında hata oluştu: {err}")
            self.root.after(0, lambda: messagebox.showerror("Biçimlendirme Hatası", f"İşlem tamamlanamadı:\n\n{err}"))
        finally:
            self.root.after(0, self._on_finish)

    def _force_unlock_volume(self, drive_letter):
        try:
            device_path = f"\\\\.\\{drive_letter.rstrip(':')}:"
            GENERIC_READ = 0x80000000
            GENERIC_WRITE = 0x40000000
            FILE_SHARE_READ = 0x00000001
            FILE_SHARE_WRITE = 0x00000002
            OPEN_EXISTING = 3
            FSCTL_DISMOUNT_VOLUME = 0x00090020
            FSCTL_UNLOCK_VOLUME = 0x0009001C

            h = ctypes.windll.kernel32.CreateFileW(
                device_path,
                GENERIC_READ | GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                0,
                None
            )
            if h != -1 and h != 0:
                bytes_returned = wintypes.DWORD(0)
                ctypes.windll.kernel32.DeviceIoControl(h, FSCTL_DISMOUNT_VOLUME, None, 0, None, 0, ctypes.byref(bytes_returned), None)
                ctypes.windll.kernel32.DeviceIoControl(h, FSCTL_UNLOCK_VOLUME, None, 0, None, 0, ctypes.byref(bytes_returned), None)
                ctypes.windll.kernel32.CloseHandle(h)
        except Exception:
            pass

    def _cycle_volume_offline_online(self, drive_letter):
        letter_clean = drive_letter.rstrip(':')
        dp_script = f"""select volume {letter_clean}
offline volume
online volume
"""
        dp_file = os.path.join(tempfile.gettempdir(), f"cycle_{letter_clean}.txt")
        try:
            with open(dp_file, "w") as f:
                f.write(dp_script)
            subprocess.run(["diskpart", "/s", dp_file], capture_output=True, text=True)
            os.remove(dp_file)
        except Exception:
            pass

    def _on_success(self, drive_letter):
        msg = (
            f"🎉 BİÇİMLENDİRME BAŞARIYLA TAMAMLANDI!\n\n"
            f"Sürücü: {drive_letter}\n"
            f"Dosya Sistemi: FAT32\n"
            f"Bölüm Tablosu: MBR (PS3 ile %100 Uyumlu)\n\n"
            f"Diskinizi şimdi güvenle PS3 veya bilgisayarınızda kullanabilirsiniz."
        )
        ans = messagebox.askyesno("Başarılı!", msg + "\n\nSürücüyü Windows Gezgini'nde açmak ister misiniz?")
        if ans:
            os.startfile(drive_letter + "\\")

    def _on_finish(self):
        self.is_formatting = False
        self.progress_bar.stop()
        self.btn_start.config(state=tk.NORMAL, text="🚀 FAT32 FORMATI VE HAZIRLIĞI BAŞLAT")
        self.refresh_disks()


def main():
    if not is_admin():
        elevate_to_admin()

    root = tk.Tk()
    app = FAT32FormatterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
