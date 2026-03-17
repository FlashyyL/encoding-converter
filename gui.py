"""
File Encoding Converter - macOS Style GUI Module
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import json
from typing import Optional
from converter import EncodingConverter


class MacOSButton(tk.Canvas):
    """macOS style rounded button with subtle shadow and hover effect"""
    
    def __init__(self, parent, text, command=None, icon="",
                 bg_color="#007AFF", hover_color="#0051D5",
                 text_color="white", width=120, height=32,
                 font_size=13, is_secondary=False, **kwargs):
        # 添加阴影偏移
        self.shadow_offset = 2
        super().__init__(parent, width=width + self.shadow_offset, 
                        height=height + self.shadow_offset,
                        highlightthickness=0, relief=tk.FLAT, 
                        bg=parent.cget('bg'), **kwargs)
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.command = command
        self.is_secondary = is_secondary
        self.corner_radius = 6
        
        # 绘制阴影
        if not is_secondary:
            self.shadow_rect = self.create_rounded_rect(
                self.shadow_offset, self.shadow_offset,
                width + self.shadow_offset, height + self.shadow_offset,
                self.corner_radius, fill="#D1D1D6", outline=""
            )
        
        # 绘制按钮背景
        self.rect = self.create_rounded_rect(
            0, 0, width, height,
            self.corner_radius,
            fill=bg_color, outline=""
        )
        
        # 绘制文字
        display_text = f"{icon} {text}" if icon else text
        self.text_item = self.create_text(
            width // 2, height // 2,
            text=display_text,
            fill=text_color,
            font=("SF Pro Text", font_size) if self._has_sf_pro() else ("Helvetica Neue", font_size)
        )
        
        # 绑定事件
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.config(cursor="hand2")
    
    def _has_sf_pro(self):
        """Check if SF Pro font is available"""
        try:
            tk.Label(font=("SF Pro Text", 1)).destroy()
            return True
        except:
            return False
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
    
    def _on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)
    
    def _on_click(self, event):
        self.move(self.text_item, 0, 1)
        if hasattr(self, 'shadow_rect'):
            self.itemconfig(self.shadow_rect, fill="#E5E5EA")
    
    def _on_release(self, event):
        self.move(self.text_item, 0, -1)
        if hasattr(self, 'shadow_rect'):
            self.itemconfig(self.shadow_rect, fill="#D1D1D6")
        if self.command:
            self.command()


class MacOSSegmentedButton(tk.Frame):
    """macOS style segmented control"""
    
    def __init__(self, parent, options, command=None, **kwargs):
        super().__init__(parent, bg=parent.cget('bg'), **kwargs)
        
        self.options = options
        self.command = command
        self.selected_index = 0
        self.buttons = []
        
        # 外边框
        self.outer_frame = tk.Frame(self, bg="#C6C6C8", padx=1, pady=1)
        self.outer_frame.pack()
        
        self.inner_frame = tk.Frame(self.outer_frame, bg="#E5E5EA")
        self.inner_frame.pack()
        
        for i, option in enumerate(options):
            btn = tk.Label(
                self.inner_frame,
                text=option,
                bg="#FFFFFF" if i == 0 else "#E5E5EA",
                fg="#007AFF" if i == 0 else "#000000",
                font=("SF Pro Text", 12) if self._has_sf_pro() else ("Helvetica Neue", 12),
                padx=16, pady=6,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=1, pady=1)
            btn.bind("<Button-1>", lambda e, idx=i: self._select(idx))
            self.buttons.append(btn)
    
    def _has_sf_pro(self):
        try:
            tk.Label(font=("SF Pro Text", 1)).destroy()
            return True
        except:
            return False
    
    def _select(self, index):
        self.selected_index = index
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.config(bg="#FFFFFF", fg="#007AFF")
            else:
                btn.config(bg="#E5E5EA", fg="#000000")
        if self.command:
            self.command(index, self.options[index])


class MacOSSwitch(tk.Canvas):
    """macOS style toggle switch"""
    
    def __init__(self, parent, command=None, initial=False, **kwargs):
        self.width = 44
        self.height = 24
        super().__init__(parent, width=self.width, height=self.height,
                        highlightthickness=0, relief=tk.FLAT,
                        bg=parent.cget('bg'), **kwargs)
        
        self.command = command
        self.state = initial
        
        # 绘制背景轨道
        self.track = self.create_rounded_rect(
            0, 2, self.width, self.height - 2, 11,
            fill="#34C759" if initial else "#E5E5EA", outline=""
        )
        
        # 绘制圆形滑块
        self.knob = self.create_oval(
            2 if initial else self.width - 22, 1,
            22 if initial else self.width - 2, self.height - 1,
            fill="#FFFFFF", outline="#00000010"
        )
        
        self.bind("<Button-1>", self._toggle)
        self.config(cursor="hand2")
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _toggle(self, event=None):
        self.state = not self.state
        
        # 动画效果
        if self.state:
            self.itemconfig(self.track, fill="#34C759")
            self.coords(self.knob, self.width - 22, 1, self.width - 2, self.height - 1)
        else:
            self.itemconfig(self.track, fill="#E5E5EA")
            self.coords(self.knob, 2, 1, 22, self.height - 1)
        
        if self.command:
            self.command(self.state)
    
    def get(self):
        return self.state
    
    def set(self, value):
        if value != self.state:
            self._toggle()


class UIScaleDialog(tk.Toplevel):
    """UI Scale Settings Dialog - macOS style"""
    
    def __init__(self, parent, gui):
        super().__init__(parent)
        self.gui = gui
        self.title("界面设置")
        self.geometry("420x320")
        self.resizable(False, False)
        self.configure(bg="#F5F5F7")
        
        # 圆角窗口效果（模拟）
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
        # 居中
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets with macOS style"""
        # 标题
        tk.Label(self, text="界面设置",
                bg="#F5F5F7",
                fg="#1D1D1F",
                font=("SF Pro Display", 18, "bold") if self._has_sf_pro() else ("Helvetica Neue", 18, "bold")
                ).pack(pady=20)
        
        # 设置卡片
        card = tk.Frame(self, bg="#FFFFFF", padx=20, pady=20)
        card.pack(fill=tk.X, padx=20, pady=10)
        
        # 字体大小
        frame1 = tk.Frame(card, bg="#FFFFFF")
        frame1.pack(fill=tk.X, pady=8)
        
        tk.Label(frame1, text="字体大小",
                bg="#FFFFFF",
                fg="#1D1D1F",
                font=("SF Pro Text", 13) if self._has_sf_pro() else ("Helvetica Neue", 13)
                ).pack(side=tk.LEFT)
        
        self.font_var = tk.IntVar(value=self.gui.font_size)
        font_scale = tk.Scale(frame1, from_=10, to=20, orient=tk.HORIZONTAL,
                             variable=self.font_var,
                             bg="#FFFFFF",
                             fg="#1D1D1F",
                             highlightthickness=0,
                             troughcolor="#E5E5EA",
                             activebackground="#007AFF",
                             length=180,
                             showvalue=0)
        font_scale.pack(side=tk.RIGHT, padx=10)
        
        self.font_label = tk.Label(frame1, text=f"{self.gui.font_size}pt",
                                  bg="#FFFFFF",
                                  fg="#007AFF",
                                  font=("SF Pro Text", 13, "bold") if self._has_sf_pro() else ("Helvetica Neue", 13, "bold"))
        self.font_label.pack(side=tk.RIGHT, padx=5)
        
        font_scale.config(command=self._on_font_change)
        
        # 分隔线
        tk.Frame(card, bg="#E5E5EA", height=1).pack(fill=tk.X, pady=8)
        
        # UI 缩放
        frame2 = tk.Frame(card, bg="#FFFFFF")
        frame2.pack(fill=tk.X, pady=8)
        
        tk.Label(frame2, text="界面缩放",
                bg="#FFFFFF",
                fg="#1D1D1F",
                font=("SF Pro Text", 13) if self._has_sf_pro() else ("Helvetica Neue", 13)
                ).pack(side=tk.LEFT)
        
        self.scale_var = tk.IntVar(value=int(self.gui.ui_scale * 100))
        scale_slider = tk.Scale(frame2, from_=80, to=150, orient=tk.HORIZONTAL,
                               variable=self.scale_var,
                               bg="#FFFFFF",
                               fg="#1D1D1F",
                               highlightthickness=0,
                               troughcolor="#E5E5EA",
                               activebackground="#007AFF",
                               length=180,
                               showvalue=0)
        scale_slider.pack(side=tk.RIGHT, padx=10)
        
        self.scale_label = tk.Label(frame2, text=f"{int(self.gui.ui_scale * 100)}%",
                                   bg="#FFFFFF",
                                   fg="#007AFF",
                                   font=("SF Pro Text", 13, "bold") if self._has_sf_pro() else ("Helvetica Neue", 13, "bold"))
        self.scale_label.pack(side=tk.RIGHT, padx=5)
        
        scale_slider.config(command=self._on_scale_change)
        
        # 按钮区域
        btn_frame = tk.Frame(self, bg="#F5F5F7")
        btn_frame.pack(pady=20)
        
        MacOSButton(btn_frame, text="重置默认",
                   command=self._reset_default,
                   bg_color="#FF3B30",
                   hover_color="#D70015",
                   width=100, height=32,
                   font_size=12).pack(side=tk.LEFT, padx=8)
        
        MacOSButton(btn_frame, text="确定",
                   command=self._apply_and_close,
                   bg_color="#007AFF",
                   hover_color="#0051D5",
                   width=100, height=32,
                   font_size=12).pack(side=tk.LEFT, padx=8)
    
    def _has_sf_pro(self):
        try:
            tk.Label(font=("SF Pro Text", 1)).destroy()
            return True
        except:
            return False
    
    def _on_font_change(self, value):
        self.font_label.config(text=f"{value}pt")
        self.gui.font_size = int(value)
        self.gui._apply_ui_scale()
    
    def _on_scale_change(self, value):
        self.scale_label.config(text=f"{value}%")
        self.gui.ui_scale = int(value) / 100
        self.gui._apply_ui_scale()
    
    def _reset_default(self):
        self.font_var.set(14)
        self.scale_var.set(100)
        self.gui.font_size = 14
        self.gui.ui_scale = 1.0
        self.font_label.config(text="14pt")
        self.scale_label.config(text="100%")
        self.gui._apply_ui_scale()
    
    def _apply_and_close(self):
        self.gui._save_ui_config()
        self.destroy()


class EncodingConverterGUI:
    """macOS Style Encoding Converter GUI"""
    
    # macOS Color scheme
    COLORS = {
        'primary': '#007AFF',
        'primary_dark': '#0051D5',
        'success': '#34C759',
        'success_dark': '#248A3D',
        'warning': '#FF9500',
        'warning_dark': '#C93400',
        'error': '#FF3B30',
        'error_dark': '#D70015',
        'background': '#F5F5F7',
        'card_bg': '#FFFFFF',
        'text': '#1D1D1F',
        'text_secondary': '#86868B',
        'border': '#E5E5EA',
        'hover': '#F2F2F7',
        'separator': '#C6C6C8'
    }
    
    # SF Symbols style icons (using Unicode)
    ICONS = {
        'file': '📄',
        'folder': '📁',
        'detect': '🔍',
        'convert': '⏵',
        'clear': '🗑',
        'select_all': '☑',
        'deselect': '☐',
        'batch': '⚡',
        'log': '📝',
        'settings': '⚙',
        'help': '?',
        'info': 'ℹ',
        'success': '✓',
        'error': '✕',
        'warning': '⚠',
        'pending': '◌'
    }
    
    CONFIG_FILE = "ui_config.json"
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Default UI settings
        self.font_size = 14
        self.ui_scale = 1.0
        
        # Load saved config
        self._load_ui_config()
        
        self.root.title("文件编码转换工具")
        self.root.geometry(self._scale_size("1400x900"))
        self.root.minsize(*self._scale_size_tuple(1000, 650))
        self.root.configure(bg=self.COLORS['background'])
        
        # Initialize converter
        self.converter = EncodingConverter()
        
        # File list storage
        self.file_list = []
        self.selected_files = set()
        
        # Store widget references for scaling
        self.widgets = {}
        
        # Setup styles
        self._setup_styles()
        
        # Create UI
        self._create_header()
        self._create_toolbar()
        self._create_file_list()
        self._create_options_panel()
        self._create_log_panel()
        self._create_status_bar()
        
        # Bind shortcuts
        self._bind_shortcuts()
        
        # Apply initial scale
        self._apply_ui_scale()
    
    def _scale_size(self, size_str: str) -> str:
        """Scale size string"""
        if 'x' in size_str:
            w, h = map(int, size_str.split('x'))
            return f"{int(w * self.ui_scale)}x{int(h * self.ui_scale)}"
        return size_str
    
    def _scale_size_tuple(self, *sizes: int) -> tuple:
        """Scale size tuple"""
        return tuple(int(s * self.ui_scale) for s in sizes)
    
    def _scale_int(self, value: int) -> int:
        """Scale integer value"""
        return int(value * self.ui_scale)
    
    def _load_ui_config(self):
        """Load UI configuration"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.font_size = config.get('font_size', 14)
                    self.ui_scale = config.get('ui_scale', 1.0)
        except Exception as e:
            print(f"[WARNING] - Failed to load UI config: {e}")
    
    def _save_ui_config(self):
        """Save UI configuration"""
        try:
            config = {
                'font_size': self.font_size,
                'ui_scale': self.ui_scale
            }
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[WARNING] - Failed to save UI config: {e}")
    
    def _apply_ui_scale(self):
        """Apply UI scaling"""
        self._setup_styles()
        
        # Update header
        if 'header' in self.widgets:
            self.widgets['header'].config(height=self._scale_int(52))
        
        # Update title
        if 'title' in self.widgets:
            self.widgets['title'].config(font=self._get_font(15, "bold"))
        
        # Update toolbar
        if 'toolbar' in self.widgets:
            self.widgets['toolbar'].config(height=self._scale_int(140))
        
        # Update status bar
        if 'status_bar' in self.widgets:
            self.widgets['status_bar'].config(height=self._scale_int(28))
        
        # Refresh treeview
        if hasattr(self, 'tree'):
            self.tree.config(style="Custom.Treeview")
        
        self.root.update_idletasks()
    
    def _get_font(self, size, weight=""):
        """Get font with SF Pro or fallback"""
        try:
            font_name = "SF Pro Text" if weight != "bold" else "SF Pro Display"
            tk.Label(font=(font_name, 1)).destroy()
            return (font_name, self._scale_int(size), weight) if weight else (font_name, self._scale_int(size))
        except:
            return ("Helvetica Neue", self._scale_int(size), weight) if weight else ("Helvetica Neue", self._scale_int(size))
    
    def _setup_styles(self):
        """Setup macOS UI styles"""
        style = ttk.Style()
        
        # Configure Treeview - macOS style
        style.configure("Custom.Treeview",
                       background=self.COLORS['card_bg'],
                       foreground=self.COLORS['text'],
                       fieldbackground=self.COLORS['card_bg'],
                       rowheight=self._scale_int(36))
        style.configure("Custom.Treeview.Heading",
                       background=self.COLORS['background'],
                       foreground=self.COLORS['text'],
                       font=self._get_font(11, "bold"))
        style.map("Custom.Treeview",
                 background=[("selected", self.COLORS['primary'])],
                 foreground=[("selected", "white")])
        
        # Configure Combobox - macOS style
        style.configure("Custom.TCombobox",
                       fieldbackground=self.COLORS['card_bg'],
                       background=self.COLORS['primary'],
                       foreground=self.COLORS['text'])
        
        # Configure Checkbutton
        style.configure("Custom.TCheckbutton",
                       background=self.COLORS['card_bg'],
                       foreground=self.COLORS['text'])
        
        # Configure LabelFrame
        style.configure("Custom.TLabelframe",
                       background=self.COLORS['card_bg'],
                       foreground=self.COLORS['text'])
        style.configure("Custom.TLabelframe.Label",
                       background=self.COLORS['card_bg'],
                       foreground=self.COLORS['text_secondary'],
                       font=self._get_font(11, "bold"))
        
        # Configure Scrollbar
        style.configure("Custom.Vertical.TScrollbar",
                       background=self.COLORS['border'],
                       troughcolor=self.COLORS['card_bg'],
                       bordercolor=self.COLORS['border'])
    
    def _create_header(self):
        """Create macOS style header bar"""
        header = tk.Frame(self.root, bg=self.COLORS['background'], 
                         height=self._scale_int(52))
        header.pack(fill=tk.X, padx=self._scale_int(20), pady=self._scale_int(10))
        header.pack_propagate(False)
        self.widgets['header'] = header
        
        # Title with SF Pro style
        title = tk.Label(header, text="文件编码转换工具", 
                        bg=self.COLORS['background'],
                        fg=self.COLORS['text'],
                        font=self._get_font(15, "bold"))
        title.pack(side=tk.LEFT, pady=self._scale_int(10))
        self.widgets['title'] = title
        
        # Subtitle
        subtitle = tk.Label(header, text="Encoding Converter", 
                           bg=self.COLORS['background'],
                           fg=self.COLORS['text_secondary'],
                           font=self._get_font(11))
        subtitle.pack(side=tk.LEFT, padx=self._scale_int(8), pady=self._scale_int(10))
    
    def _create_toolbar(self):
        """Create macOS style toolbar with card layout"""
        # 主工具栏容器
        toolbar = tk.Frame(self.root, bg=self.COLORS['background'])
        toolbar.pack(fill=tk.X, padx=self._scale_int(20), pady=self._scale_int(5))
        self.widgets['toolbar'] = toolbar
        
        # 卡片容器
        card = tk.Frame(toolbar, bg=self.COLORS['card_bg'], 
                       padx=self._scale_int(16), pady=self._scale_int(12))
        card.pack(fill=tk.X)
        
        # 第一行：文件操作
        row1 = tk.Frame(card, bg=self.COLORS['card_bg'])
        row1.pack(fill=tk.X, pady=self._scale_int(4))
        
        tk.Label(row1, text="文件", bg=self.COLORS['card_bg'],
                fg=self.COLORS['text_secondary'],
                font=self._get_font(10, "bold")).pack(side=tk.LEFT)
        
        MacOSButton(row1, text="选择文件", icon=self.ICONS['file'],
                   command=self._select_files,
                   bg_color=self.COLORS['primary'],
                   hover_color=self.COLORS['primary_dark'],
                   width=self._scale_int(110), height=self._scale_int(28),
                   font_size=self.font_size).pack(side=tk.LEFT, padx=self._scale_int(12))
        
        MacOSButton(row1, text="选择文件夹", icon=self.ICONS['folder'],
                   command=self._select_directory,
                   bg_color=self.COLORS['primary'],
                   hover_color=self.COLORS['primary_dark'],
                   width=self._scale_int(120), height=self._scale_int(28),
                   font_size=self.font_size).pack(side=tk.LEFT, padx=self._scale_int(6))
        
        MacOSButton(row1, text="清空", icon=self.ICONS['clear'],
                   command=self._clear_list,
                   bg_color=self.COLORS['error'],
                   hover_color=self.COLORS['error_dark'],
                   width=self._scale_int(80), height=self._scale_int(28),
                   font_size=self.font_size).pack(side=tk.LEFT, padx=self._scale_int(6))
        
        # 分隔线
        tk.Frame(card, bg=self.COLORS['border'], height=1).pack(fill=tk.X, pady=self._scale_int(8))
        
        # 第二行：操作
        row2 = tk.Frame(card, bg=self.COLORS['card_bg'])
        row2.pack(fill=tk.X, pady=self._scale_int(4))
        
        tk.Label(row2, text="操作", bg=self.COLORS['card_bg'],
                fg=self.COLORS['text_secondary'],
                font=self._get_font(10, "bold")).pack(side=tk.LEFT)
        
        MacOSButton(row2, text="检测编码", icon=self.ICONS['detect'],
                   command=self._detect_selected,
                   bg_color=self.COLORS['success'],
                   hover_color=self.COLORS['success_dark'],
                   width=self._scale_int(110), height=self._scale_int(28),
                   font_size=self.font_size).pack(side=tk.LEFT, padx=self._scale_int(12))
        
        MacOSButton(row2, text="转换编码", icon=self.ICONS['convert'],
                   command=self._convert_selected,
                   bg_color=self.COLORS['success'],
                   hover_color=self.COLORS['success_dark'],
                   width=self._scale_int(110), height=self._scale_int(28),
                   font_size=self.font_size).pack(side=tk.LEFT, padx=self._scale_int(6))
        
        MacOSButton(row2, text="全选", icon=self.ICONS['select_all'],
                   command=self._select_all,
                   bg_color=self.COLORS['primary'],
                   hover_color=self.COLORS['primary_dark'],
                   width=self._scale_int(80), height=self._scale_int(28),
                   font_size=self.font_size, is_secondary=True).pack(side=tk.LEFT, padx=self._scale_int(20))
        
        MacOSButton(row2, text="取消", icon=self.ICONS['deselect'],
                   command=self._deselect_all,
                   bg_color=self.COLORS['primary'],
                   hover_color=self.COLORS['primary_dark'],
                   width=self._scale_int(80), height=self._scale_int(28),
                   font_size=self.font_size, is_secondary=True).pack(side=tk.LEFT, padx=self._scale_int(6))
        
        # 右侧设置和帮助按钮
        MacOSButton(row2, text="设置", icon=self.ICONS['settings'],
                   command=self._show_settings,
                   bg_color=self.COLORS['text_secondary'],
                   hover_color="#636366",
                   width=self._scale_int(80), height=self._scale_int(28),
                   font_size=self.font_size, is_secondary=True).pack(side=tk.RIGHT, padx=self._scale_int(4))
        
        MacOSButton(row2, text="帮助", icon=self.ICONS['help'],
                   command=self._show_help,
                   bg_color=self.COLORS['text_secondary'],
                   hover_color="#636366",
                   width=self._scale_int(80), height=self._scale_int(28),
                   font_size=self.font_size, is_secondary=True).pack(side=tk.RIGHT, padx=self._scale_int(4))
    
    def _show_settings(self):
        """Show settings dialog"""
        UIScaleDialog(self.root, self)
    
    def _create_file_list(self):
        """Create macOS style file list"""
        # 卡片容器
        list_card = tk.Frame(self.root, bg=self.COLORS['card_bg'],
                            padx=1, pady=1)
        list_card.pack(fill=tk.BOTH, expand=True, 
                      padx=self._scale_int(20), pady=self._scale_int(10))
        
        # 标题栏
        header_frame = tk.Frame(list_card, bg=self.COLORS['card_bg'],
                               height=self._scale_int(40))
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="文件列表", 
                bg=self.COLORS['card_bg'],
                fg=self.COLORS['text'],
                font=self._get_font(13, "bold")).pack(side=tk.LEFT, 
                                                      padx=self._scale_int(16),
                                                      pady=self._scale_int(8))
        
        # 分隔线
        tk.Frame(list_card, bg=self.COLORS['border'], height=1).pack(fill=tk.X)
        
        # 列表容器
        inner_frame = tk.Frame(list_card, bg=self.COLORS['card_bg'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Create Treeview
        columns = ('filename', 'filepath', 'encoding', 'confidence', 'size', 'status')
        self.tree = ttk.Treeview(inner_frame, columns=columns, show='headings', 
                                selectmode='extended', style="Custom.Treeview")
        
        # Set columns
        self.tree.heading('filename', text='文件名')
        self.tree.heading('filepath', text='路径')
        self.tree.heading('encoding', text='编码')
        self.tree.heading('confidence', text='置信度')
        self.tree.heading('size', text='大小')
        self.tree.heading('status', text='状态')
        
        self.tree.column('filename', width=self._scale_int(180), minwidth=self._scale_int(120))
        self.tree.column('filepath', width=self._scale_int(350), minwidth=self._scale_int(200))
        self.tree.column('encoding', width=self._scale_int(100), minwidth=self._scale_int(80))
        self.tree.column('confidence', width=self._scale_int(90), minwidth=self._scale_int(70))
        self.tree.column('size', width=self._scale_int(100), minwidth=self._scale_int(80))
        self.tree.column('status', width=self._scale_int(100), minwidth=self._scale_int(80))
        
        # Scrollbars
        vsb = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview,
                           style="Custom.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(inner_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        inner_frame.grid_rowconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # macOS style hover effect (no zebra striping)
        self.tree.tag_configure('hover', background=self.COLORS['hover'])
    
    def _create_options_panel(self):
        """Create macOS style options panel"""
        # 卡片容器
        options_card = tk.Frame(self.root, bg=self.COLORS['card_bg'])
        options_card.pack(fill=tk.X, padx=self._scale_int(20), pady=self._scale_int(5))
        
        # 内边距
        inner = tk.Frame(options_card, bg=self.COLORS['card_bg'],
                        padx=self._scale_int(16), pady=self._scale_int(12))
        inner.pack(fill=tk.X)
        
        # 目标编码
        tk.Label(inner, text="目标编码", 
                bg=self.COLORS['card_bg'],
                fg=self.COLORS['text_secondary'],
                font=self._get_font(10, "bold")).pack(side=tk.LEFT)
        
        self.target_encoding = tk.StringVar(value='UTF-8')
        encodings = self.converter.get_supported_encodings()
        encoding_combo = ttk.Combobox(inner, textvariable=self.target_encoding, 
                                     values=encodings, state='readonly', width=18,
                                     style="Custom.TCombobox",
                                     font=self._get_font(12))
        encoding_combo.pack(side=tk.LEFT, padx=self._scale_int(12))
        
        # 分隔线
        tk.Frame(inner, bg=self.COLORS['border'], width=1).pack(side=tk.LEFT, 
                                                                fill=tk.Y, 
                                                                padx=self._scale_int(16))
        
        # Options checkboxes with macOS style
        self.backup_var = tk.BooleanVar(value=True)
        self._create_checkbox(inner, " 备份原文件", self.backup_var)
        
        self.overwrite_var = tk.BooleanVar(value=True)
        self._create_checkbox(inner, " 覆盖原文件", self.overwrite_var)
        
        self.recursive_var = tk.BooleanVar(value=True)
        self._create_checkbox(inner, " 递归扫描子文件夹", self.recursive_var)
        
        # 批量转换按钮
        MacOSButton(inner, text="批量转换", icon=self.ICONS['batch'],
                   command=self._batch_convert,
                   bg_color=self.COLORS['warning'],
                   hover_color=self.COLORS['warning_dark'],
                   width=self._scale_int(120), height=self._scale_int(32),
                   font_size=self.font_size).pack(side=tk.RIGHT, padx=self._scale_int(8))
    
    def _create_checkbox(self, parent, text, variable):
        """Create macOS style checkbox"""
        cb_frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        cb_frame.pack(side=tk.LEFT, padx=self._scale_int(12))
        
        # 使用系统风格复选框
        cb = tk.Checkbutton(cb_frame, text=text, variable=variable,
                           bg=self.COLORS['card_bg'],
                           fg=self.COLORS['text'],
                           selectcolor=self.COLORS['card_bg'],
                           activebackground=self.COLORS['card_bg'],
                           font=self._get_font(12),
                           cursor="hand2")
        cb.pack()
        return cb
    
    def _create_log_panel(self):
        """Create macOS style log panel"""
        # 卡片容器
        log_card = tk.Frame(self.root, bg=self.COLORS['card_bg'])
        log_card.pack(fill=tk.BOTH, expand=False, 
                     padx=self._scale_int(20), pady=self._scale_int(10))
        
        # 标题栏
        header_frame = tk.Frame(log_card, bg=self.COLORS['card_bg'],
                               height=self._scale_int(36))
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="日志输出", 
                bg=self.COLORS['card_bg'],
                fg=self.COLORS['text'],
                font=self._get_font(12, "bold")).pack(side=tk.LEFT, 
                                                      padx=self._scale_int(16),
                                                      pady=self._scale_int(8))
        
        # 分隔线
        tk.Frame(log_card, bg=self.COLORS['border'], height=1).pack(fill=tk.X)
        
        # 日志文本区域
        inner_frame = tk.Frame(log_card, bg=self.COLORS['card_bg'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.log_text = scrolledtext.ScrolledText(inner_frame, height=6, wrap=tk.WORD,
                                                 bg=self.COLORS['card_bg'],
                                                 fg=self.COLORS['text'],
                                                 font=("SF Mono", self._scale_int(11)) if self._has_mono_font() else ("Consolas", self._scale_int(11)),
                                                 relief=tk.FLAT,
                                                 highlightthickness=0,
                                                 padx=8, pady=8)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=self._scale_int(8), pady=self._scale_int(8))
        self.log_text.config(state=tk.DISABLED)
        
        # Configure tags for colored text
        self.log_text.tag_configure("INFO", foreground=self.COLORS['primary'])
        self.log_text.tag_configure("SUCCESS", foreground=self.COLORS['success'])
        self.log_text.tag_configure("WARNING", foreground=self.COLORS['warning'])
        self.log_text.tag_configure("ERROR", foreground=self.COLORS['error'])
    
    def _has_mono_font(self):
        """Check if SF Mono font is available"""
        try:
            tk.Label(font=("SF Mono", 1)).destroy()
            return True
        except:
            return False
    
    def _create_status_bar(self):
        """Create macOS style status bar"""
        status_frame = tk.Frame(self.root, bg=self.COLORS['background'], 
                               height=self._scale_int(28))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        self.widgets['status_bar'] = status_frame
        
        # Status message
        self.status_var = tk.StringVar(value=f"{self.ICONS['info']} 就绪")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg=self.COLORS['background'],
                               fg=self.COLORS['text_secondary'],
                               font=self._get_font(11))
        status_label.pack(side=tk.LEFT, padx=self._scale_int(20))
        
        # Statistics
        self.stats_var = tk.StringVar(value="文件: 0 | 已选: 0")
        stats_label = tk.Label(status_frame, textvariable=self.stats_var,
                              bg=self.COLORS['background'],
                              fg=self.COLORS['text_secondary'],
                              font=self._get_font(11))
        stats_label.pack(side=tk.RIGHT, padx=self._scale_int(20))
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self._select_files())
        self.root.bind('<Control-d>', lambda e: self._select_directory())
        self.root.bind('<F5>', lambda e: self._detect_selected())
        self.root.bind('<F6>', lambda e: self._convert_selected())
        self.root.bind('<Control-a>', lambda e: self._select_all())
    
    def _log(self, message: str, level: str = "INFO"):
        """Add log message with icon and color"""
        self.log_text.config(state=tk.NORMAL)
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add icon based on level
        icon = self.ICONS.get(level.lower(), self.ICONS['info'])
        
        # Insert with tag for coloring
        log_line = f"[{timestamp}] {icon} {message}\n"
        self.log_text.insert(tk.END, log_line, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _update_status(self, message: str, icon="info"):
        """Update status bar with icon"""
        icon_symbol = self.ICONS.get(icon, self.ICONS['info'])
        self.status_var.set(f"{icon_symbol} {message}")
        self.root.update_idletasks()
    
    def _update_stats(self):
        """Update statistics"""
        total = len(self.file_list)
        selected = len(self.selected_files)
        self.stats_var.set(f"文件: {total} | 已选: {selected}")
    
    def _select_files(self):
        """Select files"""
        files = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("文本文件", "*.txt"),
                ("Python文件", "*.py"),
                ("代码文件", "*.c;*.cpp;*.h;*.java;*.js;*.ts"),
                ("网页文件", "*.html;*.htm;*.css"),
                ("配置文件", "*.xml;*.json;*.yaml;*.ini"),
            ]
        )
        
        if files:
            for file_path in files:
                self._add_file(file_path)
            self._log(f"已添加 {len(files)} 个文件", "SUCCESS")
            self._update_stats()
    
    def _select_directory(self):
        """Select directory"""
        directory = filedialog.askdirectory(title="选择文件夹")
        
        if directory:
            self._update_status("正在扫描文件夹...", "pending")
            self._log(f"正在扫描文件夹: {directory}")
            
            # Scan in background thread
            def scan():
                files = self.converter.scan_directory(
                    directory, 
                    recursive=self.recursive_var.get(),
                    include_binary=False
                )
                
                # Update UI in main thread
                self.root.after(0, lambda: self._add_files_from_scan(files))
            
            threading.Thread(target=scan, daemon=True).start()
    
    def _add_files_from_scan(self, files: list):
        """Add scanned files"""
        for file_info in files:
            self._add_file_info(file_info)
        
        self._update_status(f"扫描完成，找到 {len(files)} 个文件", "success")
        self._log(f"文件夹扫描完成，找到 {len(files)} 个文本文件", "SUCCESS")
        self._update_stats()
    
    def _add_file(self, file_path: str):
        """Add single file"""
        # Check if already exists
        for item in self.file_list:
            if item['path'] == file_path:
                return
        
        # Detect encoding
        encoding, confidence = self.converter.detect_encoding(file_path)
        
        file_info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'encoding': encoding,
            'confidence': confidence,
            'size': os.path.getsize(file_path),
            'status': '待处理'
        }
        
        self._add_file_info(file_info)
    
    def _add_file_info(self, file_info: dict):
        """Add file info to list"""
        self.file_list.append(file_info)
        
        # Format file size
        size_str = self._format_size(file_info['size'])
        
        # Format confidence
        confidence_str = f"{file_info['confidence']*100:.1f}%" if file_info['confidence'] > 0 else "N/A"
        
        # Insert into Treeview (no zebra striping for macOS style)
        item_id = self.tree.insert('', tk.END, values=(
            file_info['name'],
            file_info['path'],
            file_info['encoding'],
            confidence_str,
            size_str,
            file_info.get('status', '待处理')
        ))
        
        file_info['item_id'] = item_id
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _clear_list(self):
        """Clear list"""
        self.file_list.clear()
        self.selected_files.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._update_stats()
        self._log("已清空文件列表", "WARNING")
    
    def _on_select(self, event=None):
        """Selection event handler"""
        selection = self.tree.selection()
        self.selected_files = set()
        
        for item_id in selection:
            # Find corresponding file index
            for i, file_info in enumerate(self.file_list):
                if file_info.get('item_id') == item_id:
                    self.selected_files.add(i)
                    break
        
        self._update_stats()
    
    def _on_double_click(self, event=None):
        """Double click event handler"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values:
                self._log(f"查看文件: {values[1]}")
    
    def _select_all(self):
        """Select all"""
        self.tree.selection_set(self.tree.get_children())
        self._on_select()
    
    def _deselect_all(self):
        """Deselect all"""
        self.tree.selection_remove(self.tree.get_children())
        self._on_select()
    
    def _detect_selected(self):
        """Detect encoding for selected files"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请选择要检测的文件")
            return
        
        self._update_status("正在检测编码...", "pending")
        
        def detect():
            for idx in list(self.selected_files):
                file_info = self.file_list[idx]
                encoding, confidence = self.converter.detect_encoding(file_info['path'])
                
                # Update data
                file_info['encoding'] = encoding
                file_info['confidence'] = confidence
                file_info['status'] = '已检测'
                
                # Update UI
                self.root.after(0, lambda i=idx, e=encoding, c=confidence: 
                    self._update_file_item(i, e, c))
            
            self.root.after(0, lambda: self._update_status("编码检测完成", "success"))
            self.root.after(0, lambda: self._log("编码检测完成", "SUCCESS"))
        
        threading.Thread(target=detect, daemon=True).start()
    
    def _update_file_item(self, idx: int, encoding: str, confidence: float):
        """Update file list item"""
        if idx < len(self.file_list):
            file_info = self.file_list[idx]
            item_id = file_info['item_id']
            
            confidence_str = f"{confidence*100:.1f}%" if confidence > 0 else "N/A"
            
            self.tree.item(item_id, values=(
                file_info['name'],
                file_info['path'],
                encoding,
                confidence_str,
                self._format_size(file_info['size']),
                '已检测'
            ))
    
    def _convert_selected(self):
        """Convert encoding for selected files"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请选择要转换的文件")
            return
        
        target = self.target_encoding.get()
        backup = self.backup_var.get()
        overwrite = self.overwrite_var.get()
        
        # Confirm dialog
        count = len(self.selected_files)
        if not messagebox.askyesno("确认", f"是否将 {count} 个文件转换为 {target} 编码?"):
            return
        
        self._update_status("正在转换...", "pending")
        self._log(f"正在转换 {count} 个文件到 {target} 编码...")
        
        def convert():
            success_count = 0
            fail_count = 0
            
            for idx in list(self.selected_files):
                file_info = self.file_list[idx]
                
                success, message = self.converter.convert_file(
                    file_info['path'],
                    target,
                    backup=backup,
                    overwrite=overwrite
                )
                
                if success:
                    success_count += 1
                    file_info['status'] = '已转换'
                    level = "SUCCESS"
                else:
                    fail_count += 1
                    file_info['status'] = '失败'
                    level = "ERROR"
                
                # Update UI
                self.root.after(0, lambda m=message, l=level: self._log(m, l))
                self.root.after(0, lambda i=idx, s=file_info['status']: 
                    self._update_file_status(i, s))
            
            # Completion message
            final_msg = f"转换完成: {success_count} 成功, {fail_count} 失败"
            self.root.after(0, lambda: self._update_status(final_msg, "success" if fail_count == 0 else "warning"))
            self.root.after(0, lambda: self._log(final_msg, "SUCCESS" if fail_count == 0 else "WARNING"))
            self.root.after(0, lambda: messagebox.showinfo("完成", final_msg))
        
        threading.Thread(target=convert, daemon=True).start()
    
    def _update_file_status(self, idx: int, status: str):
        """Update file status"""
        if idx < len(self.file_list):
            file_info = self.file_list[idx]
            item_id = file_info['item_id']
            
            confidence_str = f"{file_info['confidence']*100:.1f}%" if file_info['confidence'] > 0 else "N/A"
            
            self.tree.item(item_id, values=(
                file_info['name'],
                file_info['path'],
                file_info['encoding'],
                confidence_str,
                self._format_size(file_info['size']),
                status
            ))
    
    def _batch_convert(self):
        """Batch convert all files"""
        if not self.file_list:
            messagebox.showwarning("警告", "文件列表为空")
            return
        
        target = self.target_encoding.get()
        backup = self.backup_var.get()
        overwrite = self.overwrite_var.get()
        
        # Confirm dialog
        count = len(self.file_list)
        if not messagebox.askyesno("确认", f"是否将所有 {count} 个文件转换为 {target} 编码?"):
            return
        
        self._update_status("正在批量转换...", "pending")
        self._log(f"正在批量转换 {count} 个文件到 {target} 编码...")
        
        def convert_all():
            success_count = 0
            fail_count = 0
            
            for idx, file_info in enumerate(self.file_list):
                success, message = self.converter.convert_file(
                    file_info['path'],
                    target,
                    backup=backup,
                    overwrite=overwrite
                )
                
                if success:
                    success_count += 1
                    file_info['status'] = '已转换'
                    level = "SUCCESS"
                else:
                    fail_count += 1
                    file_info['status'] = '失败'
                    level = "ERROR"
                
                # Update UI
                self.root.after(0, lambda m=message, l=level: self._log(m, l))
                self.root.after(0, lambda i=idx, s=file_info['status']: 
                    self._update_file_status(i, s))
            
            # Completion message
            final_msg = f"批量转换完成: {success_count} 成功, {fail_count} 失败"
            self.root.after(0, lambda: self._update_status(final_msg, "success" if fail_count == 0 else "warning"))
            self.root.after(0, lambda: self._log(final_msg, "SUCCESS" if fail_count == 0 else "WARNING"))
            self.root.after(0, lambda: messagebox.showinfo("完成", final_msg))
        
        threading.Thread(target=convert_all, daemon=True).start()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """文件编码转换工具 - 使用帮助

功能特性:
1. 文件选择
   - 选择文件: 选择一个或多个文件
   - 选择文件夹: 扫描文件夹中的所有文本文件

2. 编码检测
   - 自动检测文件编码
   - 显示检测置信度

3. 编码转换
   - 转换为多种编码格式
   - 备份原文件
   - 覆盖或创建新文件

支持的目标编码:
- UTF-8 / UTF-8-SIG (带BOM)
- GBK / GB2312 / GB18030 (中文编码)
- BIG5 (繁体中文)
- UTF-16 / UTF-32 (各种字节序)
- ISO-8859-1 / WINDOWS-1252
- SHIFT_JIS / EUC-JP / EUC-KR

快捷键:
- Ctrl+O: 选择文件
- Ctrl+D: 选择文件夹
- F5: 检测编码
- F6: 转换编码
- Ctrl+A: 全选

界面设置:
- 点击工具栏"设置"按钮
- 可调节字体大小(10-20pt)
- 可调节界面缩放(80%-150%)
- 设置自动保存

注意事项:
1. 转换前建议备份重要文件
2. 程序会自动过滤二进制文件
3. 确保目标编码支持文件内容
"""
        messagebox.showinfo("帮助", help_text)


def main():
    """Main function"""
    root = tk.Tk()
    app = EncodingConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
