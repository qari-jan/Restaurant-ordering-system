import sys
import datetime
import os
import glob
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QScrollArea, QFrame, QDialog, QMessageBox,
    QHeaderView, QGraphicsDropShadowEffect, QSizePolicy, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import (
    QPalette, QColor, QPixmap, QPainter, QLinearGradient,
    QBrush, QPen, QRadialGradient, QFont
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Person import Person
from Food_Item import FoodItem
from Order import Order
from Bill_Splitter import BillSplitter

# ═══════════════════════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════════════════════
DARK       = "#080810"
PANEL      = "rgba(8, 8, 18, 0.82)"
CARD       = "rgba(12, 12, 24, 0.88)"
GOLD       = "#C9A84C"
GOLD_LT    = "#E8C97A"
GOLD_DK    = "#7A5C18"
CREAM      = "#F0E6CC"
MUTED      = "#7A7A9A"
BORDER     = "#252538"
DANGER     = "#C0392B"
PURPLE     = "#3A3060"

# ── find first JPG in script folder ────────────────────────────────
def _find_local_jpg():
    base = os.path.dirname(os.path.abspath(__file__))
    for ext in ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.PNG"):
        hits = glob.glob(os.path.join(base, ext))
        if hits:
            return hits[0]
    return None


# ═══════════════════════════════════════════════════════════════════
#  BACKGROUND  — local JPG + cinematic overlay
# ═══════════════════════════════════════════════════════════════════
class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._px = QPixmap()
        path = _find_local_jpg()
        if path:
            self._px.load(path)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        w, h = self.width(), self.height()

        # 1 ── photo (cover)
        if not self._px.isNull():
            scaled = self._px.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            ox = (scaled.width()  - w) // 2
            oy = (scaled.height() - h) // 2
            p.drawPixmap(-ox, -oy, scaled)
        else:
            p.fillRect(0, 0, w, h, QColor(DARK))

        # 2 ── deep cinematic vignette: left + right edges
        for x0, x1 in [(0, w // 3), (w * 2 // 3, w)]:
            side = QLinearGradient(x0, 0, x1, 0)
            side.setColorAt(0.0 if x0 == 0 else 1.0, QColor(5, 4, 14, 200))
            side.setColorAt(1.0 if x0 == 0 else 0.0, QColor(5, 4, 14,   0))
            p.fillRect(x0, 0, x1 - x0, h, QBrush(side))

        # 3 ── top bar darkener
        top = QLinearGradient(0, 0, 0, 90)
        top.setColorAt(0.0, QColor(4, 4, 12, 220))
        top.setColorAt(1.0, QColor(4, 4, 12,   0))
        p.fillRect(0, 0, w, 90, QBrush(top))

        # 4 ── bottom bar darkener
        bot = QLinearGradient(0, h - 50, 0, h)
        bot.setColorAt(0.0, QColor(4, 4, 12,   0))
        bot.setColorAt(1.0, QColor(4, 4, 12, 200))
        p.fillRect(0, h - 50, w, 50, QBrush(bot))

        # 5 ── overall tint so panels read cleanly
        p.fillRect(0, 0, w, h, QColor(6, 5, 16, 110))

        # 6 ── faint centre gold glow
        glow = QRadialGradient(w * 0.5, h * 0.46, h * 0.55)
        glow.setColorAt(0.0, QColor(201, 168, 76, 22))
        glow.setColorAt(1.0, QColor(201, 168, 76,  0))
        p.fillRect(0, 0, w, h, QBrush(glow))

        p.end()


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════
def _shadow(w, r=22, dx=0, dy=5, color=QColor(0, 0, 0, 160)):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(r); fx.setOffset(dx, dy); fx.setColor(color)
    w.setGraphicsEffect(fx)

def _gold_shadow(w, r=18):
    _shadow(w, r, 0, 3, QColor(201, 168, 76, 70))


class Divider(QFrame):
    def __init__(self, p=None):
        super().__init__(p)
        self.setFixedHeight(1)
        self.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 transparent,stop:0.25 {GOLD_DK},stop:0.75 {GOLD_DK},stop:1 transparent);"
        )


class Card(QFrame):
    """Frosted-glass dark card."""
    def __init__(self, p=None, radius=10):
        super().__init__(p)
        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: {radius}px;
            }}
        """)
        _shadow(self, r=28, dy=6)


class GoldBtn(QPushButton):
    def __init__(self, text, variant="filled", p=None):
        super().__init__(text, p)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        if variant == "filled":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                        stop:0 {GOLD_LT}, stop:1 {GOLD_DK});
                    color: #0A0810;
                    font-family: Georgia, serif;
                    font-size: 12px; font-weight: bold;
                    letter-spacing: 1.4px;
                    border: none; border-radius: 6px;
                    padding: 0 26px;
                }}
                QPushButton:hover  {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #FFE8A0,stop:1 {GOLD}); }}
                QPushButton:pressed {{ background: {GOLD_DK}; }}
            """)
        else:  # outline
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {GOLD};
                    font-family: Georgia, serif;
                    font-size: 12px; letter-spacing: 1.2px;
                    border: 1px solid {GOLD_DK};
                    border-radius: 6px; padding: 0 20px;
                }}
                QPushButton:hover  {{ border-color: {GOLD}; color: {GOLD_LT}; background: rgba(201,168,76,0.08); }}
                QPushButton:pressed {{ background: rgba(201,168,76,0.18); }}
            """)
        _gold_shadow(self)


class Field(QLineEdit):
    def __init__(self, hint="", p=None):
        super().__init__(p)
        self.setPlaceholderText(hint)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(14,12,28,0.80);
                color: {CREAM};
                font-family: Georgia, serif; font-size: 13px;
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 0 12px;
                selection-background-color: {GOLD};
            }}
            QLineEdit:focus {{ border-color: {GOLD_DK}; background: rgba(18,16,34,0.92); }}
        """)


class Combo(QComboBox):
    def __init__(self, p=None):
        super().__init__(p)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QComboBox {{
                background: rgba(14,12,28,0.80);
                color: {CREAM};
                font-family: Georgia, serif; font-size: 13px;
                border: 1px solid {BORDER}; border-radius: 6px;
                padding: 0 12px;
            }}
            QComboBox:focus {{ border-color: {GOLD_DK}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {GOLD};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: #0E0C1E;
                color: {CREAM};
                border: 1px solid {GOLD_DK};
                selection-background-color: {GOLD_DK};
                selection-color: #0A0810;
                outline: none;
            }}
        """)


def _lbl(text, size=12, color=CREAM, bold=False, spacing=0):
    l = QLabel(text)
    w = "bold" if bold else "normal"
    l.setStyleSheet(
        f"color:{color};font-family:Georgia,serif;font-size:{size}px;"
        f"font-weight:{w};letter-spacing:{spacing}px;background:transparent;"
    )
    return l


def _table_style():
    return f"""
        QTableWidget {{
            background: rgba(8,8,18,0.55);
            color: {CREAM};
            font-family: Georgia, serif; font-size: 12px;
            border: 1px solid {BORDER}; border-radius: 6px;
            gridline-color: {BORDER};
        }}
        QHeaderView::section {{
            background: rgba(58,48,96,0.85);
            color: {GOLD};
            font-family: Georgia, serif; font-size: 11px;
            letter-spacing: 1px; padding: 7px 6px; border: none;
        }}
        QTableWidget::item {{ padding: 5px 6px; }}
        QTableWidget::item:alternate {{ background: rgba(22,20,44,0.45); }}
        QTableWidget::item:selected  {{ background: rgba(201,168,76,0.18); color: {GOLD_LT}; }}
        QScrollBar:vertical {{
            background: rgba(8,8,18,0.4); width: 6px; border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {GOLD_DK}; border-radius: 3px; min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """


# ═══════════════════════════════════════════════════════════════════
#  MEMBER ORDER CARD
# ═══════════════════════════════════════════════════════════════════
class MemberCard(Card):
    def __init__(self, num, menu, p=None):
        super().__init__(p, radius=8)
        self.num = num
        self.menu = menu
        self._items = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # ── header: badge + name + remove ──────────────────────
        hdr = QHBoxLayout(); hdr.setSpacing(10)

        badge = QLabel(f" {self.num} ")
        badge.setFixedSize(30, 30)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {GOLD_LT},stop:1 {GOLD_DK});
            color: #080810; font-family: Georgia,serif; font-size: 13px;
            font-weight: bold; border-radius: 15px;
        """)
        hdr.addWidget(badge)

        self.name_field = Field(f"Guest {self.num} — Enter Name")
        hdr.addWidget(self.name_field, 1)

        rm = QPushButton("✕")
        rm.setFixedSize(30, 30)
        rm.setCursor(Qt.CursorShape.PointingHandCursor)
        rm.setStyleSheet(f"""
            QPushButton {{ background: rgba({int(DANGER[1:3],16)},{int(DANGER[3:5],16)},{int(DANGER[5:],16)},0.20);
                color: {DANGER}; font-size: 13px; border: 1px solid rgba(192,57,43,0.35);
                border-radius: 15px; font-weight: bold; }}
            QPushButton:hover  {{ background: {DANGER}; color: white; }}
            QPushButton:pressed {{ background: #922B21; }}
        """)
        rm.clicked.connect(self._remove)
        hdr.addWidget(rm)
        root.addLayout(hdr)

        root.addWidget(Divider())

        # ── item selector ───────────────────────────────────────
        sel = QHBoxLayout(); sel.setSpacing(8)
        self.combo = Combo()
        for name, price in self.menu.items():
            self.combo.addItem(f"{name}  ·  Rs. {price}", (name, price))
        sel.addWidget(self.combo, 1)

        add_btn = GoldBtn("＋ Add", "outline")
        add_btn.setFixedWidth(82)
        add_btn.clicked.connect(self._add)
        sel.addWidget(add_btn)
        root.addLayout(sel)

        # ── ordered items table ─────────────────────────────────
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["#", "Item", "Price"])
        self.tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(0, 32)
        self.tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(2, 88)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl.setStyleSheet(_table_style())
        self.tbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        root.addWidget(self.tbl)

        # ── subtotal ────────────────────────────────────────────
        self.sub_lbl = _lbl("Subtotal:  Rs. 0", 12, GOLD)
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(self.sub_lbl)

    # ── slots ───────────────────────────────────────────────────────
    def _add(self):
        data = self.combo.currentData()
        if not data: return
        name, price = data
        self._items.append((name, price))
        r = self.tbl.rowCount()
        self.tbl.insertRow(r)
        n_cell = QTableWidgetItem(str(r + 1))
        n_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        n_cell.setForeground(QColor(MUTED))
        i_cell = QTableWidgetItem(name)
        p_cell = QTableWidgetItem(f"Rs. {price}")
        p_cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        p_cell.setForeground(QColor(GOLD_LT))
        self.tbl.setItem(r, 0, n_cell)
        self.tbl.setItem(r, 1, i_cell)
        self.tbl.setItem(r, 2, p_cell)
        self._fit()
        total = sum(x[1] for x in self._items)
        self.sub_lbl.setText(f"Subtotal:  Rs. {total}")

    def _fit(self):
        hh = self.tbl.horizontalHeader().height()
        rh = sum(self.tbl.rowHeight(i) for i in range(self.tbl.rowCount()))
        self.tbl.setFixedHeight(hh + rh + 4)

    def _remove(self):
        pa = self.parent()
        if pa and hasattr(pa, "remove_card"):
            pa.remove_card(self)

    def guest_name(self):
        return self.name_field.text().strip() or f"Guest {self.num}"

    def ordered(self):
        return list(self._items)


# ═══════════════════════════════════════════════════════════════════
#  MEMBERS SCROLL AREA
# ═══════════════════════════════════════════════════════════════════
class MembersArea(QWidget):
    def __init__(self, menu, p=None):
        super().__init__(p)
        self.menu = menu
        self.cards = []
        self._ctr = 0
        self.setStyleSheet("background: transparent;")
        self._lay = QVBoxLayout(self)
        self._lay.setSpacing(12)
        self._lay.setContentsMargins(2, 2, 2, 2)
        self._lay.addStretch()

    def add_card(self):
        self._ctr += 1
        c = MemberCard(self._ctr, self.menu, self)
        self.cards.append(c)
        self._lay.insertWidget(self._lay.count() - 1, c)

    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
            self._lay.removeWidget(card)
            card.deleteLater()


# ═══════════════════════════════════════════════════════════════════
#  BILL REPORT DIALOG
# ═══════════════════════════════════════════════════════════════════
class BillDialog(QDialog):
    def __init__(self, shares, persons_data, total, mode, p=None):
        super().__init__(p)
        self.setWindowTitle("Grand Café — Bill Report")
        self.setMinimumSize(700, 520)
        self.setStyleSheet(f"background: #08080E; color: {CREAM};")
        self._build(shares, persons_data, total, mode)
        self._save(shares, persons_data, total, mode)

    def _build(self, shares, persons_data, total, mode):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(36, 30, 36, 30)
        lay.setSpacing(16)

        # title
        t = _lbl("BILL  REPORT", 22, GOLD, bold=True, spacing=5)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)

        ts = datetime.datetime.now().strftime("%d %B %Y  ·  %I:%M %p")
        sub = _lbl(f"{ts}   ·   Split: {mode.upper()}", 11, MUTED)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)
        lay.addWidget(Divider())

        # table
        tbl = QTableWidget(len(persons_data), 3)
        tbl.setHorizontalHeaderLabels(["Guest", "Items Ordered", "Amount"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        tbl.setColumnWidth(0, 140)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        tbl.setColumnWidth(2, 110)
        tbl.verticalHeader().setVisible(False)
        tbl.setAlternatingRowColors(True)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setStyleSheet(_table_style())

        for i, (name, items) in enumerate(persons_data):
            items_str = "  ·  ".join(x[0] for x in items) or "—"
            amt = shares.get(name, 0)
            n_cell = QTableWidgetItem(name)
            n_cell.setForeground(QColor(CREAM))
            i_cell = QTableWidgetItem(items_str)
            i_cell.setForeground(QColor(MUTED))
            a_cell = QTableWidgetItem(f"Rs. {amt:.0f}")
            a_cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            a_cell.setForeground(QColor(GOLD_LT))
            tbl.setItem(i, 0, n_cell)
            tbl.setItem(i, 1, i_cell)
            tbl.setItem(i, 2, a_cell)

        tbl.resizeRowsToContents()
        lay.addWidget(tbl, 1)
        lay.addWidget(Divider())

        # total row
        tot_row = QHBoxLayout()
        tot_row.addStretch()
        tot_lbl = _lbl(f"GRAND TOTAL    Rs. {total:.0f}", 18, GOLD_LT, bold=True, spacing=2)
        tot_row.addWidget(tot_lbl)
        lay.addLayout(tot_row)

        # close
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = GoldBtn("Close", "filled")
        close_btn.setFixedWidth(130)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)

    def _save(self, shares, persons_data, total, mode):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("bill.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{'═'*52}\n")
            f.write(f"  Session: {ts}  |  Mode: {mode.upper()}\n")
            f.write(f"{'─'*52}\n")
            f.write(f"  {'Guest':<18} {'Items':<22} Amount\n")
            f.write(f"{'─'*52}\n")
            for name, items in persons_data:
                items_str = ", ".join(x[0] for x in items)
                f.write(f"  {name:<18} {items_str:<22} Rs.{shares.get(name,0):.0f}\n")
            f.write(f"{'─'*52}\n")
            f.write(f"  Grand Total: Rs.{total:.0f}\n")
            f.write(f"{'═'*52}\n")


# ═══════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════
class GrandCafe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.menu = self._load_menu()
        self.setWindowTitle("Grand Café — Luxury Ordering System")
        self.setMinimumSize(1040, 720)
        self.resize(1180, 820)
        self._build()

    # ── menu loader ─────────────────────────────────────────────────
    def _load_menu(self):
        menu = {}
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.txt")
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        try: menu[parts[0].strip()] = int(parts[1].strip())
                        except ValueError: pass
        except FileNotFoundError:
            menu = {"Burger":350,"Pizza":550,"Pasta":400,"Sandwich":250,
                    "Coffee":150,"Tea":100,"Juice":200,"Salad":300,
                    "Steak":900,"Soup":200,"Dessert":250,"Water":50}
        return menu

    # ── UI ──────────────────────────────────────────────────────────
    def _build(self):
        # background
        self.bg = BackgroundWidget(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())

        central = QWidget(self)
        central.setStyleSheet("background: transparent;")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOP BAR ─────────────────────────────────────────────────
        bar = QWidget()
        bar.setFixedHeight(68)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(4,3,12,0.97), stop:0.5 rgba(10,8,24,0.93), stop:1 rgba(4,3,12,0.97));
            border-bottom: 1px solid {GOLD_DK};
        """)
        bar_lay = QHBoxLayout(bar)
        bar_lay.setContentsMargins(28, 0, 28, 0)

        # left: logo block
        logo_block = QHBoxLayout(); logo_block.setSpacing(10)
        crown = _lbl("♛", 26, GOLD)
        logo_block.addWidget(crown)
        name_block = QVBoxLayout(); name_block.setSpacing(0)
        name_block.addWidget(_lbl("GRAND  CAFÉ", 17, GOLD_LT, bold=True, spacing=5))
        name_block.addWidget(_lbl("Fine Dining & Ordering", 9, MUTED, spacing=2))
        logo_block.addLayout(name_block)
        bar_lay.addLayout(logo_block)

        bar_lay.addStretch()

        # centre: image source indicator
        jpg_path = _find_local_jpg()
        img_note = os.path.basename(jpg_path) if jpg_path else "No image found in folder"
        bar_lay.addWidget(_lbl(f"🖼  {img_note}", 10, MUTED))

        bar_lay.addStretch()

        # right: clock
        self.clock = _lbl("", 12, GOLD)
        bar_lay.addWidget(self.clock)
        t = QTimer(self); t.timeout.connect(self._tick); t.start(1000); self._tick()

        root.addWidget(bar)

        # ── BODY ────────────────────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(22, 18, 22, 14)
        body.setSpacing(18)

        # ── LEFT PANEL ──────────────────────────────────────────────
        left = Card(); left.setFixedWidth(255)
        ll = QVBoxLayout(left); ll.setContentsMargins(16, 16, 16, 16); ll.setSpacing(12)

        ll.addWidget(_lbl("M E N U", 13, GOLD, bold=True, spacing=4))
        ll.addWidget(Divider())

        mt = QTableWidget(len(self.menu), 2)
        mt.setHorizontalHeaderLabels(["Item", "Rs."])
        mt.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        mt.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        mt.setColumnWidth(1, 60)
        mt.verticalHeader().setVisible(False)
        mt.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        mt.setAlternatingRowColors(True)
        mt.setStyleSheet(_table_style())
        for i, (itm, prc) in enumerate(self.menu.items()):
            ic = QTableWidgetItem(itm); ic.setForeground(QColor(CREAM))
            pc = QTableWidgetItem(str(prc))
            pc.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            pc.setForeground(QColor(GOLD_LT))
            mt.setItem(i, 0, ic); mt.setItem(i, 1, pc)
        ll.addWidget(mt, 1)

        ll.addWidget(Divider())
        ll.addWidget(_lbl("Bill Split", 10, MUTED, spacing=1))
        self.mode_cb = Combo()
        self.mode_cb.addItem("Custom  —  each pays their own", "custom")
        self.mode_cb.addItem("Equal   —  split evenly", "equal")
        ll.addWidget(self.mode_cb)

        gen = GoldBtn("Generate Bill", "filled")
        gen.clicked.connect(self._gen_bill)
        ll.addWidget(gen)

        body.addWidget(left)

        # ── RIGHT PANEL ─────────────────────────────────────────────
        right = QVBoxLayout(); right.setSpacing(12)

        # title row
        tr = QHBoxLayout()
        tr.addWidget(_lbl("ORDER  MANAGEMENT", 16, CREAM, bold=True, spacing=3))
        tr.addStretch()
        self.guest_count_lbl = _lbl("0 guests", 11, MUTED)
        tr.addWidget(self.guest_count_lbl)
        tr.addSpacing(12)
        add_btn = GoldBtn("＋  Add Guest", "outline")
        add_btn.clicked.connect(self._add_guest)
        tr.addWidget(add_btn)
        right.addLayout(tr)
        right.addWidget(Divider())

        # scrollable cards
        self.area = MembersArea(self.menu)
        scroll = QScrollArea()
        scroll.setWidget(self.area)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                background: rgba(8,8,18,0.4); width: 7px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {GOLD_DK}; border-radius: 3px; min-height: 24px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        right.addWidget(scroll, 1)
        body.addLayout(right, 1)
        root.addLayout(body, 1)

        # ── STATUS BAR ──────────────────────────────────────────────
        sb = QWidget(); sb.setFixedHeight(32)
        sb.setStyleSheet(f"""
            background: rgba(4,3,12,0.96);
            border-top: 1px solid {GOLD_DK};
        """)
        sl = QHBoxLayout(sb); sl.setContentsMargins(22, 0, 22, 0)
        self.status = _lbl("Welcome — add guests and start ordering.", 10, MUTED)
        sl.addWidget(self.status)
        sl.addStretch()
        sl.addWidget(_lbl("Grand Café  ·  Professional Edition", 10, GOLD_DK))
        root.addWidget(sb)

        self._add_guest()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.bg.setGeometry(0, 0, self.width(), self.height())

    def _tick(self):
        self.clock.setText(datetime.datetime.now().strftime("%I:%M %p   %d %b %Y"))

    def _add_guest(self):
        self.area.add_card()
        n = len(self.area.cards)
        self.guest_count_lbl.setText(f"{n} guest{'s' if n != 1 else ''}")
        self.status.setText(f"{n} guest{'s' if n != 1 else ''} in session.")

    def _gen_bill(self):
        if not self.area.cards:
            QMessageBox.warning(self, "No Guests", "Add at least one guest first.")
            return

        persons_data, order_obj, persons = [], Order(), []
        for card in self.area.cards:
            items = card.ordered()
            if not items: continue
            p = Person(card.guest_name())
            for nm, pr in items:
                fi = FoodItem(nm, pr)
                p.add_item(fi)
                order_obj.add_order(p, fi)
            persons.append(p)
            persons_data.append((card.guest_name(), items))

        if not persons:
            QMessageBox.information(self, "No Items", "No items ordered yet.")
            return

        total = order_obj.calculate_total()
        bs = BillSplitter({
            p.name: [i.get_name() for i in order_obj.get_orders()[p.name]]
            for p in persons
        })
        mode = self.mode_cb.currentData()
        shares = bs.choose_split(self.menu, mode)

        dlg = BillDialog(shares, persons_data, total, mode, self)
        dlg.exec()
        self.status.setText(
            f"Bill generated  ·  Total: Rs. {total:.0f}  ·  Saved to bill.txt"
        )


# ═══════════════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor(DARK))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(CREAM))
    pal.setColor(QPalette.ColorRole.Base,            QColor("#0C0C18"))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor("#101020"))
    pal.setColor(QPalette.ColorRole.Text,            QColor(CREAM))
    pal.setColor(QPalette.ColorRole.Button,          QColor("#0C0C18"))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(CREAM))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor(GOLD))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(DARK))
    app.setPalette(pal)

    w = GrandCafe()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()