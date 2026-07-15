import os
import re
import ast
import token
import tokenize
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from io import BytesIO
from tkinter import Button, Label, Entry, Text, Tk, TOP, X, BOTH, LEFT, RIGHT, END, Scrollbar, Y, Frame, messagebox, filedialog, ttk

# =====================================================================
# THÔNG TIN PHIÊN BẢN TOÀN CỤC (GLOBAL VERSION CONTROL)
# =====================================================================
VERSION = "2.4.0"
APP_NAME = "Python developer helper lttp release"
AUTHOR_EMAIL = "tranthienphatle@gmail.com"

# Hàm lấy URL không bị dính cache của GitHub CDN (Cache Busting)
def get_anti_cache_url(base_url):
    return f"{base_url}?t={int(time.time())}"

GITHUB_README_BASE = "https://raw.githubusercontent.com/letranthienphat/Python-developer-helper-lttp-release/refs/heads/main/README.md"
GITHUB_LATEST_CODE_BASE = "https://raw.githubusercontent.com/letranthienphat/Python-developer-helper-lttp-release/refs/heads/main/latest.py"

# =====================================================================
# TỰ ĐỘNG KIỂM TRA VÀ CÀI ĐẶT THƯ VIỆN CHO CHÍNH NÓ (NẾU THIẾU)
# =====================================================================
def auto_install_required_libraries():
    required_libs = ["pyinstaller"]
    for lib in required_libs:
        try:
            if lib == "pyinstaller":
                import PyInstaller
        except ImportError:
            print(f"[System] Required library '{lib}' not found. Auto-installing...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)
                print(f"[Success] Installed '{lib}' successfully.")
            except Exception as e:
                print(f"[Failed] Could not auto-install '{lib}': {e}")

auto_install_required_libraries()

# =====================================================================
# BỘ TỪ ĐIỂN ĐA NGÔN NGỮ (DICTIONARY FOR MULTI-LANGUAGE)
# =====================================================================
LANGUAGES = {
    "vi": {
        "title": f"{APP_NAME} - v{VERSION}",
        "btn_exe": "1. Đóng gói EXE",
        "btn_lib": "2. Cài đặt thư viện",
        "btn_fix": "3. Sửa & Phục hồi File",
        "btn_paste": "4. Quét & Sửa Code Trực Tiếp",
        "btn_about": "5. Thông tin phần mềm",
        "btn_abort": "🛑 DỪNG KHẨN CẤP",
        "console_log": "Nhật ký hoạt động (Console Log):",
        "ready": "Hệ thống sẵn sàng. Đã sửa lỗi cache GitHub và thêm nút cập nhật thủ công.",
        "welcome": f"Chào mừng bạn đến với {APP_NAME}!\nHãy chọn một tính năng bên menu trái để bắt đầu.",
        "build_title": "ĐÓNG GÓI ỨNG DỤNG (PYTHON SANG EXE)",
        "select_script": "Chọn file script:",
        "browse": "Chọn file...",
        "pack_mode": "Chế độ đóng gói:",
        "console_mode": "Cửa sổ Console (Giao diện đen):",
        "btn_start_build": "BẮT ĐẦU ĐÓNG GÓI EXE",
        "lib_title": "QUẢN LÝ VÀ CÀI ĐẶT THƯ VIỆN PIP",
        "lib_auto": "🔍 Tự động quét file .py & Cài thư viện thiếu",
        "lib_req": "📄 Chọn file requirements.txt để cài đặt",
        "lib_manual_lbl": "Tự nhập tên thư viện cần cài (cách nhau bằng dấu cách):",
        "lib_manual_btn": "Cài đặt ngay",
        "fix_title": "BỘ SỬA LỖI & PHỤC HỒI MÃ NGUỒN AN TOÀN",
        "fix_desc": "Hệ thống quản lý file thông minh: Tự động tạo bản sao lưu trước khi sửa đổi, hỗ trợ rollback và khôi phục trạng thái code gốc từ file .bak chỉ với 1 click.",
        "fix_single": "📁 Chọn và sửa lỗi duy nhất 1 File .py",
        "fix_dir": "🗂️ Chọn và quét sửa lỗi Toàn Bộ Thư Mục",
        "fix_restore": "🔄 Khôi phục lại trạng thái cũ từ file .bak",
        "paste_title": "QUÉT & SỬA CODE PYTHON TRỰC TIẾP",
        "paste_lbl": "1. Dán mã Code cần sửa vào đây:",
        "paste_out": " ✨ Kết quả tối ưu & sửa lỗi sâu (Không mất Logic gốc):",
        "btn_copy": "📋 Sao chép (Copy)",
        "btn_download": "💾 Tải xuống (.py)",
        "btn_trigger_fix": "⚡ BẮT ĐẦU QUÉT & TỰ ĐỘNG SỬA CODE MẠNH MẼ",
        "abort_msg": "⚠️ [HỆ THỐNG] ĐÃ BẤM DỪNG KHẨN CẤP! Đang ngắt luồng xử lý...",
        "success": "Thành công",
        "warning": "Cảnh báo",
        "error": "Lỗi",
        "notice": "Thông báo",
        "about_title": "THÔNG TIN PHẦN MỀM & CẬP NHẬT",
        "about_desc": f"Phần mềm: {APP_NAME}\nPhiên bản hiện tại: {VERSION}\nTác giả: Lê Trần Thiên Phát\nEmail: {AUTHOR_EMAIL}\n\nCông cụ hỗ trợ nhà phát triển Python tối ưu hóa code, sửa lỗi nhanh, phục hồi dữ liệu từ file sao lưu, cài đặt thư viện tự động và đóng gói sản phẩm hoàn thiện.",
        "btn_manual_update": "🔄 KIỂM TRA & CẬP NHẬT NGAY",
        "checking_update": "Đang kết nối GitHub bypass cache để kiểm tra phiên bản...",
        "up_to_date": "Tuyệt vời! Bạn đang sử dụng phiên bản mới nhất trên GitHub!",
        "update_found": "Phát hiện phiên bản mới: {new_ver}!\nBạn có muốn tự động tải về và nâng cấp ngay lập tức không?",
        "updating": "Đang tiến hành tải bản cập nhật mới..."
    },
    "en": {
        "title": f"{APP_NAME} - v{VERSION}",
        "btn_exe": "1. Build EXE Package",
        "btn_lib": "2. Install Libraries",
        "btn_fix": "3. Fix & Restore File",
        "btn_paste": "4. Scan & Fix Code Directly",
        "btn_about": "5. About Software",
        "btn_abort": "🛑 EMERGENCY STOP",
        "console_log": "Activity Logs (Console Log):",
        "ready": "System ready. GitHub CDN cache bypass and manual update button integrated.",
        "welcome": f"Welcome to {APP_NAME}!\nPlease select a feature from the left menu to start.",
        "build_title": "APPLICATION PACKAGING (PYTHON TO EXE)",
        "select_script": "Select script file:",
        "browse": "Browse...",
        "pack_mode": "Packaging Mode:",
        "console_mode": "Console Window (Black CLI Window):",
        "btn_start_build": "START PACKING EXE",
        "lib_title": "PIP LIBRARY MANAGEMENT & INSTALLATION",
        "lib_auto": "🔍 Auto-scan .py file & Install missing libs",
        "lib_req": "📄 Select requirements.txt file to install",
        "lib_manual_lbl": "Manually enter library names (separated by space):",
        "lib_manual_btn": "Install Now",
        "fix_title": "CODE FIXER & SAFE SOURCE RESTORATION",
        "fix_desc": "Smart file management system: Auto-creates backups before modification, supports safe rollback, and restores original code from .bak files with 1 click.",
        "fix_single": "📁 Select and fix a Single .py File",
        "fix_dir": "🗂️ Select and scan/fix Entire Directory",
        "fix_restore": "🔄 Restore original code from .bak file",
        "paste_title": "SCAN & FIX PYTHON CODE DIRECTLY",
        "paste_lbl": "1. Paste your Python code here:",
        "paste_out": " ✨ Optimized & Deep-Fixed Code (Preserves Original Logic):",
        "btn_copy": "📋 Copy Code",
        "btn_download": "💾 Download (.py)",
        "btn_trigger_fix": "⚡ START DEEP SCAN & POWERFUL FIX",
        "abort_msg": "⚠️ [SYSTEM] EMERGENCY STOP TRIGGERED! Terminating processes...",
        "success": "Success",
        "warning": "Warning",
        "error": "Error",
        "notice": "Notice",
        "about_title": "SOFTWARE INFORMATION & UPDATE",
        "about_desc": f"Software: {APP_NAME}\nCurrent Version: {VERSION}\nAuthor: Le Tran Thien Phat\nEmail: {AUTHOR_EMAIL}\n\nA tool to help Python developers optimize code, debug instantly, manage dependencies, restore backups, and bundle applications.",
        "btn_manual_update": "🔄 CHECK & UPDATE NOW",
        "checking_update": "Connecting to GitHub bypassing cache to check for updates...",
        "up_to_date": "Great! You are running the latest version available on GitHub!",
        "update_found": "New update available: {new_ver}!\nWould you like to automatically download and upgrade now?",
        "updating": "Downloading update and applying changes automatically..."
    }
}

class PythonDeveloperToolGUI:
    def __init__(self, root):
        self.root = root
        self.current_lang = "vi"  # Mặc định tiếng Việt
        
        # Biến điều khiển đa luồng và cập nhật
        self.is_aborted = False
        self.current_thread = None
        
        self.init_ui()
        self.update_ui_language()
        
        # Khởi chạy luồng tự động kiểm tra cập nhật ngầm khi mở app
        threading.Thread(target=self.check_for_updates, args=(False,), daemon=True).start()

    def init_ui(self):
        try:
            if os.name == 'nt':
                self.root.state('zoomed')
            else:
                self.root.wm_attributes('-zoomed', True)
        except Exception:
            self.root.geometry("1024x768")
            
        self.root.minsize(950, 700)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # --- HEADER ROW ---
        self.title_frame = Frame(self.root, bg="#2c3e50")
        self.title_frame.pack(fill=X)
        
        self.title_label = Label(self.title_frame, text="", font=("Helvetica", 15, "bold"), fg="white", bg="#2c3e50", pady=10)
        self.title_label.pack(side=LEFT, padx=15)
        
        self.btn_lang_toggle = Button(self.title_frame, text="English 🌐", font=("Segoe UI", 9, "bold"), bg="#34495e", fg="white", bd=0, padx=12, pady=5, cursor="hand2", command=self.toggle_language)
        self.btn_lang_toggle.pack(side=RIGHT, padx=15, pady=8)

        # --- MAIN CONTAINER ---
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.left_menu = Frame(main_frame, width=230, bg="#ecf0f1", padx=5, pady=5)
        self.left_menu.pack(side=LEFT, fill=Y)
        self.left_menu.pack_propagate(False)
        
        self.right_content = Frame(main_frame, bg="white", padx=10, pady=5)
        self.right_content.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # --- LEFT MENU BUTTONS ---
        self.lbl_menu_header = Label(self.left_menu, text="CHỨC NĂNG / FEATURES", font=("Segoe UI", 10, "bold"), bg="#ecf0f1", fg="#2c3e50", pady=5)
        self.lbl_menu_header.pack(fill=X)
        
        self.btn_style = {"font": ("Segoe UI", 10), "bg": "#34495e", "fg": "white", "activebackground": "#2c3e50", "activeforeground": "white", "pady": 8, "bd": 0, "cursor": "hand2"}
        
        self.btn1 = Button(self.left_menu, text="", command=self.show_build_exe, **self.btn_style)
        self.btn1.pack(fill=X, pady=4)
        
        self.btn2 = Button(self.left_menu, text="", command=self.show_install_libs, **self.btn_style)
        self.btn2.pack(fill=X, pady=4)
        
        self.btn3 = Button(self.left_menu, text="", command=self.show_fix_code, **self.btn_style)
        self.btn3.pack(fill=X, pady=4)

        self.btn4 = Button(self.left_menu, text="", command=self.show_paste_code_fixer, **self.btn_style)
        self.btn4.pack(fill=X, pady=4)

        self.btn5 = Button(self.left_menu, text="", command=self.show_about_software, **self.btn_style)
        self.btn5.pack(fill=X, pady=4)
        
        # Đẩy nút dừng khẩn cấp xuống đáy menu
        lbl_space = Label(self.left_menu, bg="#ecf0f1")
        lbl_space.pack(fill=BOTH, expand=True)
        
        self.btn_abort = Button(self.left_menu, text="", font=("Segoe UI", 10, "bold"), bg="#7f8c8d", fg="white", activebackground="#c0392b", activeforeground="white", pady=12, bd=0, cursor="hand2", command=self.trigger_emergency_stop)
        self.btn_abort.pack(fill=X, pady=10)
        self.btn_abort.config(state="disabled")
        
        # --- BOTTOM CONSOLE LOG ---
        log_frame = Frame(self.root, padx=10, pady=5)
        log_frame.pack(fill=X, side=TOP)
        
        self.lbl_log = Label(log_frame, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_log.pack(anchor="w")
        
        self.log_text = Text(log_frame, height=6, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        scrollbar = Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.pack(fill=BOTH, expand=True)

    def toggle_language(self):
        if self.current_lang == "vi":
            self.current_lang = "en"
            self.btn_lang_toggle.config(text="Tiếng Việt 🌐")
        else:
            self.current_lang = "vi"
            self.btn_lang_toggle.config(text="English 🌐")
        
        self.update_ui_language()
        self.log(LANGUAGES[self.current_lang]["ready"])

    def update_ui_language(self):
        lang = LANGUAGES[self.current_lang]
        self.root.title(lang["title"])
        self.title_label.config(text=lang["title"])
        self.btn1.config(text=lang["btn_exe"])
        self.btn2.config(text=lang["btn_lib"])
        self.btn3.config(text=lang["btn_fix"])
        self.btn4.config(text=lang["btn_paste"])
        self.btn5.config(text=lang["btn_about"])
        self.btn_abort.config(text=lang["btn_abort"])
        self.lbl_log.config(text=lang["console_log"])
        self.show_welcome()

    def log(self, message):
        self.log_text.insert(END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(END)

    def start_task_thread(self, target_func, *args):
        self.is_aborted = False
        self.btn_abort.config(state="normal", bg="#e74c3c")
        self.current_thread = threading.Thread(target=target_func, args=args, daemon=True)
        self.current_thread.start()

    def end_task_status(self):
        self.btn_abort.config(state="disabled", bg="#7f8c8d")

    def trigger_emergency_stop(self):
        self.is_aborted = True
        self.log(LANGUAGES[self.current_lang]["abort_msg"])
        self.btn_abort.config(state="disabled")

    def clear_right_content(self):
        for widget in self.right_content.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_right_content()
        lbl = Label(self.right_content, text=LANGUAGES[self.current_lang]["welcome"], font=("Segoe UI", 12), bg="white", fg="#555", pady=50)
        lbl.pack(fill=BOTH, expand=True)

    # ==================== HỆ THỐNG TỰ ĐỘNG KIỂM TRA VÀ CẬP NHẬT (ANTI-CACHE) ====================
    def check_for_updates(self, is_manual=False):
        lang = LANGUAGES[self.current_lang]
        self.log(lang["checking_update"])
        
        try:
            # Bypass cache bằng cách chèn timestamp vào cuối URL
            anti_cache_url = get_anti_cache_url(GITHUB_README_BASE)
            req = urllib.request.Request(anti_cache_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=7) as response:
                html = response.read().decode('utf-8')
                
            match = re.search(r"Latest version:\s*([\d\.]+)", html, re.IGNORECASE)
            if match:
                latest_version = match.group(1).strip()
                self.log(f"[Update Checker] Local: {VERSION} | Live GitHub: {latest_version}")
                
                if self.is_newer_version(VERSION, latest_version):
                    self.log(f"New update found: {latest_version}")
                    self.root.after(100, lambda: self.ask_for_update(latest_version))
                else:
                    self.log(lang["up_to_date"])
                    if is_manual:
                        self.root.after(100, lambda: messagebox.showinfo(lang["notice"], lang["up_to_date"]))
            else:
                self.log("[Update Checker] Format 'Latest version: X.X.X' not found in README.")
                if is_manual:
                    messagebox.showwarning(lang["warning"], "Không tìm thấy thông tin phiên bản trên GitHub.")
        except Exception as e:
            self.log(f"[Update Checker] Connection failed: {e}")
            if is_manual:
                messagebox.showerror(lang["error"], f"Không thể kết nối đến GitHub: {e}")

    def is_newer_version(self, current, latest):
        c_parts = [int(x) for x in current.split(".")]
        l_parts = [int(x) for x in latest.split(".")]
        return l_parts > c_parts

    def ask_for_update(self, new_ver):
        lang = LANGUAGES[self.current_lang]
        ans = messagebox.askyesno(lang["notice"], lang["update_found"].format(new_ver=new_ver))
        if ans:
            self.log(lang["updating"])
            threading.Thread(target=self.apply_update, daemon=True).start()

    def apply_update(self):
        try:
            anti_cache_code_url = get_anti_cache_url(GITHUB_LATEST_CODE_BASE)
            req = urllib.request.Request(anti_cache_code_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as response:
                new_code = response.read().decode('utf-8')
                
            current_file_path = os.path.abspath(sys.argv[0])
            shutil.copy2(current_file_path, current_file_path + ".bak") # Sao lưu dự phòng an toàn trước
            
            with open(current_file_path, "w", encoding="utf-8") as f:
                f.write(new_code)
                
            self.log("[Update] Code updated successfully! Exiting application...")
            messagebox.showinfo("Update Done", "Cập nhật thành công! Chương trình sẽ tự đóng để làm mới cấu trúc.")
            self.root.quit()
            sys.exit(0)
        except Exception as e:
            self.log(f"[Update Error] Update failed: {e}")
            messagebox.showerror("Update Error", f"Cập nhật thất bại: {e}")

    # ==================== CHỨC NĂNG 5: THÔNG TIN PHẦN MỀM & NÚT CẬP NHẬT THỦ CÔNG ====================
    def show_about_software(self):
        self.clear_right_content()
        lang = LANGUAGES[self.current_lang]
        
        lbl_title = Label(self.right_content, text=lang["about_title"], font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50")
        lbl_title.pack(anchor="w", pady=10)
        
        lbl_desc = Label(self.right_content, text=lang["about_desc"], font=("Segoe UI", 11), justify=LEFT, bg="white", fg="#333", wraplength=550)
        lbl_desc.pack(anchor="w", pady=10)
        
        info_frame = Frame(self.right_content, bg="#f8f9fa", bd=1, relief="solid", padx=10, pady=10)
        info_frame.pack(fill=X, pady=10)
        
        Label(info_frame, text=f"Product Name: {APP_NAME}", font=("Consolas", 10, "bold"), bg="#f8f9fa").pack(anchor="w")
        Label(info_frame, text=f"Local Version: {VERSION}", font=("Consolas", 10), bg="#f8f9fa").pack(anchor="w")
        Label(info_frame, text=f"Author Email: {AUTHOR_EMAIL}", font=("Consolas", 10), bg="#f8f9fa").pack(anchor="w")

        # NÚT BẤM CẬP NHẬT THỦ CÔNG ĐƯỢC THÊM VÀO ĐÂY
        def trigger_manual_update_check():
            threading.Thread(target=self.check_for_updates, args=(True,), daemon=True).start()

        btn_update = Button(self.right_content, text=lang["btn_manual_update"], font=("Segoe UI", 11, "bold"), bg="#2980b9", fg="white", bd=0, pady=12, cursor="hand2", command=trigger_manual_update_check)
        btn_update.pack(fill=X, pady=15)

    # ==================== CHỨC NĂNG 1: ĐÓNG GÓI EXE ====================
    def show_build_exe(self):
        self.clear_right_content()
        lang = LANGUAGES[self.current_lang]
        
        lbl_title = Label(self.right_content, text=lang["build_title"], font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50")
        lbl_title.pack(anchor="w", pady=10)
        
        file_frame = Frame(self.right_content, bg="white")
        file_frame.pack(fill=X, pady=5)
        lbl_file = Label(file_frame, text=lang["select_script"], font=("Segoe UI", 10), bg="white")
        lbl_file.pack(side=LEFT)
        ent_file = Entry(file_frame, font=("Segoe UI", 10), width=40)
        ent_file.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        def browse():
            f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
            if f:
                ent_file.delete(0, END)
                ent_file.insert(0, f)
        
        btn_browse = Button(file_frame, text=lang["browse"], command=browse, bg="#e74c3c", fg="white", bd=0, padx=10)
        btn_browse.pack(side=LEFT)

        Label(self.right_content, text=lang["pack_mode"], font=("Segoe UI", 10, "bold"), bg="white", pady=5).pack(anchor="w")
        mode_var = ttk.Combobox(self.right_content, values=["One File (--onefile)", "One Folder (--onedir)"], state="readonly", width=40)
        mode_var.current(0)
        mode_var.pack(anchor="w", pady=5)
        
        Label(self.right_content, text=lang["console_mode"], font=("Segoe UI", 10, "bold"), bg="white", pady=5).pack(anchor="w")
        console_var = ttk.Combobox(self.right_content, values=["Show Console Window", "Hide Console Window (GUI Mode)"], state="readonly", width=40)
        console_var.current(0)
        console_var.pack(anchor="w", pady=5)
        
        def trigger_build():
            py_file = ent_file.get().strip()
            if not py_file or not os.path.exists(py_file):
                messagebox.showerror(lang["error"], "Invalid file path!")
                return
            self.start_task_thread(execute_build_thread, py_file, mode_var.get(), console_var.get())

        def execute_build_thread(py_file, mode, console):
            try:
                self.log(f"Starting packaging: {py_file}")
                cmd = ["pyinstaller"]
                cmd.append("--onedir" if "Folder" in mode else "--onefile")
                cmd.append("--noconsole" if "Hide" in console else "--console")
                cmd.append(py_file)
                
                res = subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                if self.is_aborted: return
                
                if res.returncode == 0:
                    self.log("[Success] App bundled inside 'dist' folder!")
                    messagebox.showinfo(lang["success"], "Done! Check 'dist' folder.")
                else:
                    messagebox.showerror(lang["error"], "Packaging failed.")
            finally:
                self.end_task_status()

        Button(self.right_content, text=lang["btn_start_build"], command=trigger_build, bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=10).pack(fill=X, pady=20)

    # ==================== CHỨC NĂNG 2: CÀI ĐẶT THƯ VIỆN ====================
    def show_install_libs(self):
        self.clear_right_content()
        lang = LANGUAGES[self.current_lang]
        
        Label(self.right_content, text=lang["lib_title"], font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=10)
        method_frame = Frame(self.right_content, bg="white")
        method_frame.pack(fill=X, pady=10)
        
        def run_auto_detect():
            f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
            if f: self.start_task_thread(auto_detect_thread, f)

        def auto_detect_thread(f):
            try:
                self.log(f"Scanning imports from: {f}")
                libs = self.get_imported_libraries(f)
                if self.is_aborted: return
                if libs:
                    subprocess.run([sys.executable, "-m", "pip", "install"] + libs)
                    messagebox.showinfo(lang["success"], f"Installed: {', '.join(libs)}")
                else:
                    messagebox.showinfo(lang["notice"], "No custom libraries detected.")
            finally: self.end_task_status()

        Button(method_frame, text=lang["lib_auto"], command=run_auto_detect, bg="#2980b9", fg="white", font=("Segoe UI", 10), bd=0, pady=8).pack(fill=X, pady=5)
        
        def run_req():
            f = filedialog.askopenfilename(filetypes=[("Requirements", "*.txt")])
            if f: self.start_task_thread(lambda: subprocess.run([sys.executable, "-m", "pip", "install", "-r", f]))
        
        Button(method_frame, text=lang["lib_req"], command=run_req, bg="#8e44ad", fg="white", font=("Segoe UI", 10), bd=0, pady=8).pack(fill=X, pady=5)
        
        manual_frame = Frame(self.right_content, bg="white")
        manual_frame.pack(fill=X, pady=10)
        Label(manual_frame, text=lang["lib_manual_lbl"], font=("Segoe UI", 10), bg="white").pack(anchor="w")
        ent_lib = Entry(manual_frame, font=("Segoe UI", 10))
        ent_lib.pack(fill=X, side=LEFT, expand=True, pady=5, padx=(0, 5))
        
        def run_manual():
            txt = ent_lib.get().strip()
            if txt: self.start_task_thread(lambda: subprocess.run([sys.executable, "-m", "pip", "install"] + txt.split()))

        Button(manual_frame, text=lang["lib_manual_btn"], command=run_manual, bg="#27ae60", fg="white", bd=0, padx=15, pady=4).pack(side=RIGHT)

    def get_imported_libraries(self, file_path):
        libraries = set()
        builtin_libs = {"os", "sys", "time", "math", "random", "json", "re", "subprocess", "datetime", "shutil", "tkinter", "ast"}
        content = ""
        for enc in ["utf-8", "latin-1"]:
            try:
                with open(file_path, "r", encoding=enc) as f: content = f.read(); break
            except: continue
        if not content: return []
        matches = re.findall(r"^\s*import\s+([\w\s,]+)", content, re.M) + re.findall(r"^\s*from\s+(\w+)", content, re.M)
        for match in matches:
            for item in match.split(","):
                lib = item.strip().split(".")[0].split()[0]
                if lib and lib not in builtin_libs: libraries.add(lib)
        return list(libraries)

    # ==================== CHỨC NĂNG 3: SỬA LỖI & PHỤC HỒI TỪ FILE .BAK ====================
    def show_fix_code(self):
        self.clear_right_content()
        lang = LANGUAGES[self.current_lang]
        
        Label(self.right_content, text=lang["fix_title"], font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=10)
        Label(self.right_content, text=lang["fix_desc"], font=("Segoe UI", 10), justify=LEFT, bg="white", fg="#666").pack(anchor="w", pady=5)

        def run_single():
            f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
            if f and os.path.abspath(f) != os.path.abspath(sys.argv[0]):
                self.start_task_thread(self.process_fix_file, f)

        Button(self.right_content, text=lang["fix_single"], command=run_single, bg="#d35400", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=12).pack(fill=X, pady=8)

        def run_dir():
            d = filedialog.askdirectory()
            if d: self.start_task_thread(self.process_fix_dir_thread, d)

        Button(self.right_content, text=lang["fix_dir"], command=run_dir, bg="#c0392b", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=12).pack(fill=X, pady=4)

        def run_restore_bak():
            bak_file = filedialog.askopenfilename(filetypes=[("Backup Files", "*.bak")])
            if bak_file:
                self.start_task_thread(self.execute_restore_bak_thread, bak_file)

        Button(self.right_content, text=lang["fix_restore"], command=run_restore_bak, bg="#2980b9", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=12).pack(fill=X, pady=4)

    def execute_restore_bak_thread(self, bak_file_path):
        try:
            lang = LANGUAGES[self.current_lang]
            self.log(f"Attempting restoration from backup: {os.path.basename(bak_file_path)}")
            
            if bak_file_path.endswith(".bak"):
                py_file_path = bak_file_path[:-4]
            else:
                py_file_path = bak_file_path + ".py"
            
            if not os.path.exists(bak_file_path):
                self.log(f"[Error] Backup file does not exist: {bak_file_path}")
                messagebox.showerror(lang["error"], "File backup không tồn tại!")
                return
                
            with open(bak_file_path, "r", encoding="utf-8", errors="ignore") as test_f:
                content = test_f.read()
                
            if not content.strip():
                self.log("[Warning] Selected backup file is empty. Restoration aborted.")
                messagebox.showwarning(lang["warning"], "File backup trống rỗng, không thể khôi phục!")
                return
                
            shutil.copy2(bak_file_path, py_file_path)
            self.log(f"[Success] Restored original script successfully -> {os.path.basename(py_file_path)}")
            messagebox.showinfo(lang["success"], f"Đã khôi phục file thành công về trạng thái cũ:\n{os.path.basename(py_file_path)}")
            
        except Exception as e:
            self.log(f"[Error] Restoration failed: {e}")
            messagebox.showerror(LANGUAGES[self.current_lang]["error"], f"Lỗi khôi phục: {e}")
        finally:
            self.end_task_status()

    def process_fix_dir_thread(self, dir_path):
        try:
            current_script = os.path.abspath(sys.argv[0])
            ignored = {".venv", "venv", "env", "__pycache__", ".git"}
            py_files = []
            for r, dirs, files in os.walk(dir_path):
                if self.is_aborted: return
                dirs[:] = [d for d in dirs if d not in ignored]
                for f in files:
                    if f.endswith(".py") and not f.endswith(".py.bak"):
                        path = os.path.abspath(os.path.join(r, f))
                        if path != current_script: py_files.append(path)
            
            for path in py_files:
                if self.is_aborted: return
                self.process_fix_file(path)
            self.log(f"[Finished] Processed {len(py_files)} files.")
        finally: self.end_task_status()

    def process_fix_file(self, py_file):
        lines = []
        for encoding in ["utf-8", "latin-1"]:
            try:
                with open(py_file, "r", encoding=encoding) as f: lines = f.readlines(); break
            except: continue
        if not lines: return
        
        try:
            shutil.copy2(py_file, py_file + ".bak")
        except:
            pass

        fixed, new_lines = self.core_fix_algorithm_advanced(lines)
        if fixed and not self.is_aborted:
            with open(py_file, "w", encoding="utf-8") as f: f.writelines(new_lines)
            self.log(f"Fixed & Backed up: {os.path.basename(py_file)}")

    # ==================== CHỨC NĂNG 4: QUÉT & SỬA CODE TRỰC TIẾP ====================
    def show_paste_code_fixer(self):
        self.clear_right_content()
        lang = LANGUAGES[self.current_lang]
        
        Label(self.right_content, text=lang["paste_title"], font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(anchor="w", pady=5)
        panels_frame = Frame(self.right_content, bg="white")
        panels_frame.pack(fill=BOTH, expand=True)
        
        left_panel = Frame(panels_frame, bg="white")
        left_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        Label(left_panel, text=lang["paste_lbl"], font=("Segoe UI", 10, "bold"), bg="white", fg="#d35400").pack(anchor="w", pady=2)
        self.txt_input_code = Text(left_panel, font=("Consolas", 10), bg="#fafafa", fg="#2c3e50", bd=1, relief="solid")
        self.txt_input_code.pack(fill=BOTH, expand=True)
        
        right_panel = Frame(panels_frame, bg="white")
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        toolbar = Frame(right_panel, bg="#f3f3f3", height=30)
        toolbar.pack(fill=X, side=TOP, pady=(0, 2))
        toolbar.pack_propagate(False)
        Label(toolbar, text=lang["paste_out"], font=("Segoe UI", 10, "bold"), bg="#f3f3f3", fg="#27ae60").pack(side=LEFT, padx=5, pady=3)
        
        Button(toolbar, text=lang["btn_copy"], font=("Segoe UI", 9), bg="#34495e", fg="white", bd=0, padx=10, command=self.copy_to_clipboard).pack(side=RIGHT, padx=2, pady=3)
        Button(toolbar, text=lang["btn_download"], font=("Segoe UI", 9), bg="#2980b9", fg="white", bd=0, padx=10, command=self.download_fixed_code).pack(side=RIGHT, padx=2, pady=3)
        
        self.txt_output_code = Text(right_panel, font=("Consolas", 10), bg="#2d2d2d", fg="#f8f8f2", bd=1, relief="solid")
        self.txt_output_code.pack(fill=BOTH, expand=True)
        
        Button(self.right_content, text=lang["btn_trigger_fix"], font=("Segoe UI", 11, "bold"), bg="#27ae60", fg="white", bd=0, pady=10, command=self.action_fix_pasted_code).pack(fill=X, pady=(10, 5))

    def action_fix_pasted_code(self):
        raw_code = self.txt_input_code.get("1.0", END)
        if not raw_code.strip(): return
        lines = raw_code.splitlines(keepends=True)
        
        fixed, fixed_lines = self.core_fix_algorithm_advanced(lines)
        self.txt_output_code.delete("1.0", END)
        self.txt_output_code.insert("1.0", "".join(fixed_lines))

    def copy_to_clipboard(self):
        content = self.txt_output_code.get("1.0", END).rstrip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Copied to clipboard!")

    def download_fixed_code(self):
        content = self.txt_output_code.get("1.0", END).rstrip()
        if not content: return
        f = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if f:
            with open(f, "w", encoding="utf-8") as file: file.write(content)

    # ==================== HYBRID DIAGNOSTIC ENGINE V2.2 (SỬA CODE LAI) ====================
    def core_fix_algorithm_advanced(self, lines):
        fixed, raw_fixed = self.first_pass_fix(lines)
        raw_fixed = self.fix_indentation_via_tokens(raw_fixed)
        
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            try:
                ast.parse("".join(raw_fixed))
                return True, raw_fixed
            except SyntaxError as e:
                attempts += 1
                err_idx = e.lineno - 1
                if 0 <= err_idx < len(raw_fixed):
                    bad_line = raw_fixed[err_idx]
                    indent = bad_line[:len(bad_line) - len(bad_line.lstrip())]
                    
                    if "expected an indented block" in e.msg.lower():
                        raw_fixed.insert(err_idx, f"{indent}    pass  # Injected to fix empty block\n")
                        fixed = True
                        continue
                    
                    if bad_line.strip().endswith(":"):
                        if err_idx + 1 < len(raw_fixed):
                            next_line = raw_fixed[err_idx + 1]
                            if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= len(indent):
                                space_type = "    " if "    " in "".join(raw_fixed) else "\t"
                                raw_fixed[err_idx + 1] = f"{indent}{space_type}{next_line.lstrip()}"
                                fixed = True
                                continue

                    raw_fixed[err_idx] = f"{indent}pass  # [Logic Preserved / Fix Failed] {bad_line.lstrip()}"
                    fixed = True
                else:
                    break
        
        return fixed, raw_fixed

    def fix_indentation_via_tokens(self, lines):
        try:
            code_bytes = "".join(lines).encode('utf-8')
            tokens = list(tokenize.tokenize(BytesIO(code_bytes).readline))
        except Exception:
            return lines

        new_lines = list(lines)
        for tok in tokens:
            if tok.type == token.NAME and tok.string in ("def", "class", "if", "for", "while", "with", "try"):
                line_idx = tok.start[0] - 1
                if line_idx < len(new_lines):
                    current_line = new_lines[line_idx]
                    if current_line.strip() and not current_line.strip().endswith(":") and not current_line.strip().endswith("\\") and "#" not in current_line:
                        new_lines[line_idx] = current_line.rstrip("\r\n") + ":\n"
        return new_lines

    def first_pass_fix(self, lines):
        fixed = False
        new_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
            
            if stripped.startswith(("if ", "elif ", "else", "for ", "while ", "def ", "class ", "try", "except")) and not stripped.endswith(":") and not stripped.endswith("\\"):
                if "#" not in stripped:
                    line = line.rstrip("\r\n") + ":\n"
                    fixed = True
                    stripped = line.strip()

            if stripped.startswith("if ") and "=" in stripped and "==" not in stripped and "!=" not in stripped and "<=" not in stripped and ">=" not in stripped:
                match = re.search(r"if\s+([a-zA-Z0-9_]+)\s*=\s*([^:]+):", line)
                if match:
                    var_name, val = match.group(1), match.group(2)
                    line = f"{line[:len(line)-len(line.lstrip())]}if {var_name} == {val}:\n"
                    fixed = True
                    stripped = line.strip()

            if stripped.startswith("print ") and not stripped.startswith("print("):
                content = stripped[6:].strip()
                line = f"{line[:len(line)-len(line.lstrip())]}print({content})\n"
                fixed = True
                stripped = line.strip()

            if stripped.startswith("except ") and "," in stripped and " as " not in stripped:
                match = re.search(r"except\s+([^,]+)\s*,\s*([^:]+):", line)
                if match:
                    err_type, err_var = match.group(1).strip(), match.group(2).strip()
                    line = f"{line[:len(line)-len(line.lstrip())]}except {err_type} as {err_var}:\n"
                    fixed = True
                    stripped = line.strip()

            stack = []
            bracket_map = {')': '(', ']': '[', '}': '{'}
            reverse_map = {'(': ')', '[': ']', '{': '}'}
            cleaned_line = []
            
            for char in stripped:
                if char in reverse_map:
                    stack.append(char)
                    cleaned_line.append(char)
                elif char in bracket_map:
                    if stack and stack[-1] == bracket_map[char]:
                        stack.pop()
                        cleaned_line.append(char)
                    else:
                        fixed = True
                else:
                    cleaned_line.append(char)
            
            if stack:
                missing_brackets = "".join([reverse_map[x] for x in reversed(stack)])
                line = f"{line[:len(line)-len(line.lstrip())]}{''.join(cleaned_line)}{missing_brackets}\n"
                fixed = True
            else:
                line = f"{line[:len(line)-len(line.lstrip())]}{''.join(cleaned_line)}\n"

            if (stripped.count('"') % 2 != 0) and not stripped.endswith('\\') and '"""' not in stripped:
                line = line.rstrip("\r\n") + '"\n'
                fixed = True
            elif (stripped.count("'") % 2 != 0) and not stripped.endswith('\\') and "'''" not in stripped:
                line = line.rstrip("\r\n") + "'\n"
                fixed = True

            new_lines.append(line)
            
        return fixed, new_lines

if __name__ == "__main__":
    root = Tk()
    app = PythonDeveloperToolGUI(root)
    root.mainloop()
