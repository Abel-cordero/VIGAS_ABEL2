import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QButtonGroup, QMessageBox,
    QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
import mplcursors

# Tabla de diámetros y áreas (cm²) para barras de refuerzo
BAR_DATA = {
    '6mm': 0.28,
    '8mm': 0.50,
    '3/8"': 0.71,
    '12mm': 1.13,
    '1/2"': 1.29,
    '5/8"': 1.99,
    '3/4"': 2.84,
    '1"': 5.10,
}

# Diámetros equivalentes en centímetros para las mismas claves que BAR_DATA
DIAM_CM = {
    '6mm': 0.6,
    '8mm': 0.8,
    '3/8"': 0.95,
    '12mm': 1.2,
    '1/2"': 1.27,
    '5/8"': 1.59,
    '3/4"': 1.91,
    '1"': 2.54,
}

class MomentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parte 1 – Momentos y Diagramas (NTP E.060)")
        self.mn_corr = None
        self.mp_corr = None
        self._build_ui()
        self.resize(1200, 800)
        self.show()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)

        # Ajustes de márgenes y alineación a la izquierda
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(10)
        layout.setColumnStretch(6, 1)

        # ── Entradas de momentos ──────────────────────────────
        self.m_neg_edits, self.m_pos_edits = [], []
        for row, labels in enumerate(
            [("M1–", "M2–", "M3–"), ("M1+", "M2+", "M3+")]
        ):
            for i, text in enumerate(labels):
                layout.addWidget(QLabel(text), row, 2*i)
                ed = QLineEdit("0.0")
                ed.setAlignment(Qt.AlignRight)
                ed.setFixedWidth(80)
                layout.addWidget(ed, row, 2*i+1)
                if row == 0:
                    self.m_neg_edits.append(ed)
                else:
                    self.m_pos_edits.append(ed)

        # ── Selector de sistema ────────────────────────────
        self.rb_dual1 = QRadioButton("Dual 1")
        self.rb_dual2 = QRadioButton("Dual 2")
        self.rb_dual2.setChecked(True)
        bg = QButtonGroup(self)
        bg.addButton(self.rb_dual1)
        bg.addButton(self.rb_dual2)
        layout.addWidget(QLabel("Sistema:"), 2, 0)
        layout.addWidget(self.rb_dual1, 2, 1)
        layout.addWidget(self.rb_dual2, 2, 2)

        # ── Botones ────────────────────────────────────
        btn_calc    = QPushButton("Calcular Diagramas")
        btn_next    = QPushButton("Ir a Diseño de Acero")
        btn_capture = QPushButton("Capturar Diagramas")
        btn_calc.clicked.connect(self.on_calculate)
        btn_next.clicked.connect(self.on_next)
        btn_capture.clicked.connect(self._capture_diagram)
        layout.addWidget(btn_calc,    2, 3)
        layout.addWidget(btn_next,    2, 4)
        layout.addWidget(btn_capture, 2, 5)

        # ── Canvas con diagramas ─────────────────────────
        self.fig, (self.ax1, self.ax2) = plt.subplots(
            2, 1, figsize=(6, 5), constrained_layout=True
        )
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, 3, 0, 1, 6)

        self.plot_original()

    def get_moments(self):
        try:
            mn = np.array([float(ed.text()) for ed in self.m_neg_edits])
            mp = np.array([float(ed.text()) for ed in self.m_pos_edits])
            return mn, mp
        except ValueError:
            QMessageBox.warning(
                self, "Error", "Ingrese valores numéricos válidos."
            )
            raise

    def plot_original(self):
        mn, mp = self.get_moments()
        L = 1.0
        x_ctrl = np.array([0, 0.5, 1.0])
        xs = np.linspace(0, L, 200)
        csn = CubicSpline(x_ctrl, mn)
        csp = CubicSpline(x_ctrl, -mp)

        self.ax1.clear()
        self.ax2.clear()
        for ax in (self.ax1, self.ax2):
            ax.plot([0, L], [0, 0], 'k-', lw=6)

        self.ax1.plot(xs, csn(xs), 'b-', label='Neg original')
        self.ax1.plot(xs, csp(xs), 'r-', label='Pos original')
        self._draw_verticals(self.ax1, csn, csp, x_ctrl)
        self._label_points(self.ax1, csn, csp, x_ctrl)
        self._enable_hover(self.ax1, csn, csp)
        self._format(self.ax1)
        self.canvas.draw()

    def plot_corrected(self, mn_corr, mp_corr):
        L = 1.0
        x_ctrl = np.array([0, 0.5, 1.0])
        xs = np.linspace(0, L, 200)
        csn = CubicSpline(x_ctrl, mn_corr)
        csp = CubicSpline(x_ctrl, -mp_corr)

        self.ax2.clear()
        self.ax2.plot([0, L], [0, 0], 'k-', lw=6)
        self.ax2.plot(xs, csn(xs), 'b--', label='Neg corregido')
        self.ax2.plot(xs, csp(xs), 'r--', label='Pos corregido')
        self._draw_verticals(self.ax2, csn, csp, x_ctrl, dashed=True)
        self._label_points(self.ax2, csn, csp, x_ctrl)
        self._enable_hover(self.ax2, csn, csp)
        self._format(self.ax2)
        self.canvas.draw()

    def _draw_verticals(self, ax, csn, csp, x_ctrl, dashed=False):
        style = '--' if dashed else '-'
        lw = 2
        # Líneas azules (momentos negativos) en extremos
        for i, x_ext in zip((0, 2), (0.0, 1.0)):
            y = csn(x_ctrl[i])
            ax.plot([x_ext, x_ext], [0, y], 'b'+style, lw=lw)
        # Líneas rojas (momentos positivos) en extremos
        for i, x_ext in zip((0, 2), (0.0, 1.0)):
            y = csp(x_ctrl[i])
            ax.plot([x_ext, x_ext], [0, y], 'r'+style, lw=lw)

    def _label_points(self, ax, csn, csp, x_ctrl):
        y_n = csn(x_ctrl)
        y_p = csp(x_ctrl)
        for x, y in zip(x_ctrl, y_n):
            ax.text(x, y + np.sign(y)*0.05, f"{y:.2f}", ha='center',
                    va='bottom' if y >= 0 else 'top', fontsize=8)
        for x, y in zip(x_ctrl, y_p):
            ax.text(x, y - np.sign(y)*0.05, f"{y:.2f}", ha='center',
                    va='top' if y <= 0 else 'bottom', fontsize=8)

    def _enable_hover(self, ax, csn, csp):
        xs = np.linspace(0, 1.0, 100)
        for curve in (csn, csp):
            ys = curve(xs)
            pts = ax.scatter(xs, ys, s=0)
            cursor = mplcursors.cursor(pts, hover=True)
            @cursor.connect("add")
            def _(sel):
                x, y = sel.target
                sel.annotation.set_text(f"x={x:.2f}, M={y:.2f} TN·m")

    def _format(self, ax):
        ax.set_xlim(-0.02, 1.08)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xticklabels(['Extremo I','Centro','Extremo II'], fontsize=9)
        ax.set_ylabel('TN·m', fontsize=9)
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8)

    def correct_moments(self, mn, mp, sys_t):
        mn_k = np.abs(mn) * 100000
        mp_k = np.abs(mp) * 100000
        factor = 0.5 if sys_t == 'dual2' else 1/3

        for j in (0, 2):  # extremos
            mp_k[j] = max(mp_k[j], factor * mn_k[j])
            mn_k[j] = max(mn_k[j], factor * mp_k[j])

        max_ext = max(mn_k[0], mn_k[2], mp_k[0], mp_k[2])
        floor = 0.25 * max_ext
        mn_k[1] = max(mn_k[1], floor)
        mp_k[1] = max(mp_k[1], floor)

        return mn_k / 100000, mp_k / 100000

    def on_calculate(self):
        try:
            mn, mp = self.get_moments()
        except:
            return
        sys_t = 'dual2' if self.rb_dual2.isChecked() else 'dual1'
        mn_c, mp_c = self.correct_moments(mn, mp, sys_t)
        self.plot_original()
        self.plot_corrected(mn_c, mp_c)
        self.mn_corr = mn_c
        self.mp_corr = mp_c

    def on_next(self):
        if self.mn_corr is None or self.mp_corr is None:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Primero calcule los momentos corregidos",
            )
            return
        self.design_win = DesignWindow(self.mn_corr, self.mp_corr)
        self.design_win.show()

    def _capture_diagram(self):
        pix = self.canvas.grab()
        QGuiApplication.clipboard().setPixmap(pix)
        QMessageBox.information(
            self,
            "Captura",
            "Diagramas copiados al portapapeles.\n"
            "Usa Ctrl+V para pegar."
        )


class DesignWindow(QMainWindow):
    """Ventana para la etapa de diseño de acero (solo interfaz gráfica)."""

    def __init__(self, mn_corr, mp_corr):
        super().__init__()
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr
        self.setWindowTitle("Parte 2 – Diseño de Acero")
        self._build_ui()

    def _calc_as_req(self, Mu, fc, b, d, fy, phi):
        """Calculate required steel area for a single moment."""
        Mu_kgcm = abs(Mu) * 100000  # convert TN·m to kg·cm
        term = 1.7 * fc * b * d / (2 * fy)
        root = (2.89 * (fc * b * d) ** 2) / (fy ** 2) - (
            6.8 * fc * b * Mu_kgcm
        ) / (phi * (fy ** 2))
        root = max(root, 0)
        return term - 0.5 * np.sqrt(root)

    def _required_areas(self):
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
            fc = float(self.edits["f'c (kg/cm²)"].text())
            fy = float(self.edits["fy (kg/cm²)"].text())
            phi = float(self.edits["φ"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
        except ValueError:
            return np.zeros(3), np.zeros(3)

        d = h - r - de - 0.5 * db

        self.as_min, self.as_max = self._calc_as_limits(fc, fy, b, d)
        self.as_min_label.setText(f"{self.as_min:.2f}")
        self.as_max_label.setText(f"{self.as_max:.2f}")

        as_n = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mn_corr]
        as_p = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mp_corr]

        as_n = np.clip(as_n, self.as_min, self.as_max)
        as_p = np.clip(as_p, self.as_min, self.as_max)

        return np.array(as_n), np.array(as_p)

    def _calc_as_limits(self, fc, fy, b, d):
        beta1 = 0.85 if fc <= 280 else 0.85 - ((fc - 280) / 70) * 0.05
        as_min = 0.7 * (np.sqrt(fc) / fy) * b * d
        pmax = 0.75 * ((0.85 * fc * beta1 / fy) * (6000 / (6000 + fy)))
        as_max = pmax * b * d
        return as_min, as_max

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)

        labels = [
            ("b (cm)", "30"),
            ("h (cm)", "50"),
            ("r (cm)", "4"),
            ("f'c (kg/cm²)", "210"),
            ("fy (kg/cm²)", "4200"),
            ("φ", "0.9"),
        ]

        self.edits = {}
        for row, (text, val) in enumerate(labels):
            layout.addWidget(QLabel(text), row, 0)
            ed = QLineEdit(val)
            ed.setAlignment(Qt.AlignRight)
            ed.setFixedWidth(70)
            layout.addWidget(ed, row, 1)
            self.edits[text] = ed

        # Combos para diámetro de estribo y de varilla
        estribo_opts = ["8mm", "3/8\"", "1/2\""]
        layout.addWidget(QLabel("ϕ estribo"), len(labels), 0)
        self.cb_estribo = QComboBox(); self.cb_estribo.addItems(estribo_opts)
        self.cb_estribo.setCurrentText('3/8"')
        layout.addWidget(self.cb_estribo, len(labels), 1)

        varilla_opts = ["1/2\"", "5/8\"", "3/4\"", "1\""]
        layout.addWidget(QLabel("ϕ varilla"), len(labels)+1, 0)
        self.cb_varilla = QComboBox(); self.cb_varilla.addItems(varilla_opts)
        self.cb_varilla.setCurrentText('5/8"')
        layout.addWidget(self.cb_varilla, len(labels)+1, 1)

        qty_opts = [""] + [str(i) for i in range(1, 11)]
        dia_opts = ["", "1/2\"", "5/8\"", "3/4\"", "1\""]

        pos_labels = ["M1-", "M2-", "M3-", "M1+", "M2+", "M3+"]
        self.qty1_boxes, self.dia1_boxes = [], []
        self.qty2_boxes, self.dia2_boxes = [], []
        self.as_total_labels = []

        self.combo_grid = QGridLayout()

        for i, label in enumerate(pos_labels):
            row = 0 if i < 3 else 1
            col = i % 3

            q1 = QComboBox(); q1.addItems(qty_opts); q1.setCurrentIndex(0)
            d1 = QComboBox(); d1.addItems(dia_opts); d1.setCurrentIndex(0)
            q2 = QComboBox(); q2.addItems(qty_opts); q2.setCurrentIndex(0)
            d2 = QComboBox(); d2.addItems(dia_opts); d2.setCurrentIndex(0)
            lbl = QLabel("0.00")

            cell = QGridLayout()
            cell.addWidget(QLabel(label), 0, 0, 1, 2, alignment=Qt.AlignCenter)
            cell.addWidget(q1, 1, 0)
            cell.addWidget(d1, 1, 1)
            cell.addWidget(q2, 2, 0)
            cell.addWidget(d2, 2, 1)
            cell.addWidget(lbl, 3, 0, 1, 2, alignment=Qt.AlignCenter)

            self.combo_grid.addLayout(cell, row, col)

            self.qty1_boxes.append(q1)
            self.dia1_boxes.append(d1)
            self.qty2_boxes.append(q2)
            self.dia2_boxes.append(d2)
            self.as_total_labels.append(lbl)

        row_start = len(labels) + 2

        layout.addWidget(QLabel("As total (cm²):"), row_start, 0)
        self.as_total_label = QLabel("0.00")
        layout.addWidget(self.as_total_label, row_start, 1)

        layout.addWidget(QLabel("As min (cm²):"), row_start, 2)
        self.as_min_label = QLabel("0.00")
        layout.addWidget(self.as_min_label, row_start, 3)

        layout.addWidget(QLabel("As max (cm²):"), row_start + 1, 2)
        self.as_max_label = QLabel("0.00")
        layout.addWidget(self.as_max_label, row_start + 1, 3)

        layout.addWidget(QLabel("Base req. (cm):"), row_start, 4)
        self.base_req_label = QLabel("-")
        layout.addWidget(self.base_req_label, row_start, 5)
        self.base_msg_label = QLabel("")
        layout.addWidget(self.base_msg_label, row_start + 1, 4, 1, 2)

        self.fig_sec, self.ax_sec = plt.subplots(figsize=(3, 3), constrained_layout=True)
        self.canvas_sec = FigureCanvas(self.fig_sec)
        layout.addWidget(self.canvas_sec, 0, 2, len(labels) + 2, 4)

        self.fig_dist, (self.ax_req, self.ax_des) = plt.subplots(
            2, 1, figsize=(5, 6), constrained_layout=True
        )
        self.canvas_dist = FigureCanvas(self.fig_dist)
        layout.addWidget(self.canvas_dist, row_start + 2, 0, 1, 8)

        layout.addLayout(self.combo_grid, row_start + 3, 0, 1, 8)

        self.btn_capture = QPushButton("Capturar Diseño")
        self.btn_memoria = QPushButton("Memoria de Cálculo")
        self.btn_salir = QPushButton("Salir")

        self.btn_capture.clicked.connect(self._capture_design)
        self.btn_memoria.clicked.connect(self.show_memoria)
        self.btn_salir.clicked.connect(QApplication.instance().quit)

        layout.addWidget(self.btn_capture, row_start + 4, 0, 1, 2)
        layout.addWidget(self.btn_memoria, row_start + 4, 2, 1, 2)
        layout.addWidget(self.btn_salir,   row_start + 4, 4, 1, 2)

        for ed in self.edits.values():
            ed.editingFinished.connect(self._redraw)
        for cb in (self.cb_estribo, self.cb_varilla):
            cb.currentIndexChanged.connect(self._redraw)

        for widgets in (
            self.qty1_boxes,
            self.dia1_boxes,
            self.qty2_boxes,
            self.dia2_boxes,
        ):
            for w in widgets:
                w.currentIndexChanged.connect(self.update_design_as)

        self.as_min = 0.0
        self.as_max = 0.0
        self.as_total = 0.0

        self.draw_section()
        self.draw_required_distribution()
        self.update_design_as()

    def draw_section(self):
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
        except ValueError:
            return

        d = h - r - de - 0.5 * db
        y_d = r + de + 0.5 * db

        self.ax_sec.clear()
        self.ax_sec.set_aspect('equal')
        self.ax_sec.plot([0, b, b, 0, 0], [0, 0, h, h, 0], 'k-')
        self.ax_sec.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], 'r--')

        self.ax_sec.annotate('', xy=(0, -5), xytext=(b, -5), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(b / 2, -6, 'b', ha='center', va='top')

        self.ax_sec.annotate('', xy=(-5, 0), xytext=(-5, h), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(-6, h / 2, 'h', ha='right', va='center', rotation=90)

        self.ax_sec.annotate('', xy=(-2, h), xytext=(-2, y_d), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(-3, (h + y_d) / 2, 'd', ha='right', va='center', rotation=90)

        self.ax_sec.set_xlim(-10, b + 10)
        self.ax_sec.set_ylim(-10, h + 10)
        self.ax_sec.axis('off')
        self.canvas_sec.draw()

    def _redraw(self):
        self.draw_section()
        self.draw_required_distribution()
        self.update_design_as()

    def draw_required_distribution(self):
        """Display required As along the beam."""
        x_ctrl = [0.0, 0.5, 1.0]
        areas_n, areas_p = self._required_areas()

        self.ax_req.clear()
        self.ax_req.plot([0, 1], [0, 0], 'k-', lw=6)

        y_off = 0.1 * max(np.max(areas_n), np.max(areas_p), 1)
        for x, a_n in zip(x_ctrl, areas_n):
            self.ax_req.text(x, y_off, f"As- {a_n:.2f}", ha='center',
                             va='bottom', color='b', fontsize=9)
        for x, a_p in zip(x_ctrl, areas_p):
            self.ax_req.text(x, -y_off, f"As+ {a_p:.2f}", ha='center',
                             va='top', color='r', fontsize=9)

        self.ax_req.set_xlim(-0.05, 1.05)
        self.ax_req.set_ylim(-2*y_off, 2*y_off)
        self.ax_req.axis('off')
        self.canvas_dist.draw()

    def update_design_as(self):
        as_req_n, as_req_p = self._required_areas()
        as_reqs = list(as_req_n) + list(as_req_p)
        totals = []
        n1_list = []
        d1_list = []
        n2_list = []
        d2_list = []
        for q1, d1, q2, d2, lbl in zip(
            self.qty1_boxes,
            self.dia1_boxes,
            self.qty2_boxes,
            self.dia2_boxes,
            self.as_total_labels,
        ):
            try:
                n1 = int(q1.currentText()) if q1.currentText() else 0
            except ValueError:
                n1 = 0
            a1 = BAR_DATA.get(d1.currentText(), 0)

            try:
                n2 = int(q2.currentText()) if q2.currentText() else 0
            except ValueError:
                n2 = 0
            a2 = BAR_DATA.get(d2.currentText(), 0)

            total = n1 * a1 + n2 * a2
            totals.append(total)
            n1_list.append(n1)
            d1_list.append(d1.currentText())
            n2_list.append(n2)
            d2_list.append(d2.currentText())

        for lbl, total, req in zip(self.as_total_labels, totals, as_reqs):
            status = "OK" if total >= req else "NO OK"
            lbl.setText(f"{total:.2f} {status}")

        self.as_total = sum(totals)
        overall_ok = all(t >= r for t, r in zip(totals, as_reqs))
        ov_status = "OK" if overall_ok else "NO OK"
        self.as_total_label.setText(f"{self.as_total:.2f} {ov_status}")

        if totals:
            idx = int(np.argmax(totals))
            a = n1_list[idx]
            d1 = DIAM_CM.get(d1_list[idx], 0)
            bq = n2_list[idx]
            d2 = DIAM_CM.get(d2_list[idx], 0)
            try:
                b_val = float(self.edits["b (cm)"].text())
                r = float(self.edits["r (cm)"].text())
                de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            except ValueError:
                self.base_req_label.setText("-")
                self.base_msg_label.setText("")
            else:
                spacing = max(a + bq - 1, 0) * 2.5
                base_req = 2 * r + 2 * de + a * d1 + bq * d2 + spacing
                self.base_req_label.setText(f"{base_req:.1f}")
                self.base_msg_label.setText("OK" if base_req <= b_val else "Aumentar base o capa")

        self.draw_design_distribution(totals)

    def draw_design_distribution(self, areas):
        x_ctrl = [0.0, 0.5, 1.0]
        areas_n = areas[:3]
        areas_p = areas[3:]
        self.ax_des.clear()
        self.ax_des.plot([0, 1], [0, 0], 'k-', lw=6)
        y_off = 0.1 * max(max(areas_n, default=0), max(areas_p, default=0), 1)
        for x, a in zip(x_ctrl, areas_n):
            self.ax_des.text(x, y_off, f"Asd- {a:.2f}", ha='center',
                             va='bottom', color='g', fontsize=9)
        for x, a in zip(x_ctrl, areas_p):
            self.ax_des.text(x, -y_off, f"Asd+ {a:.2f}", ha='center',
                             va='top', color='g', fontsize=9)
        self.ax_des.set_xlim(-0.05, 1.05)
        self.ax_des.set_ylim(-2 * y_off, 2 * y_off)
        self.ax_des.axis('off')
        self.canvas_dist.draw()

    def _capture_design(self):
        pix = self.centralWidget().grab()
        QGuiApplication.clipboard().setPixmap(pix)
        QMessageBox.information(
            self,
            "Captura",
            "Dise\u00f1o copiado al portapapeles.\nUsa Ctrl+V para pegar.",
        )

    def show_memoria(self):
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
        except ValueError:
            b = h = 0
        title = f"VIGA {int(b)}X{int(h)}"
        text = (
            "Memoria de c\u00e1lculo:\n"
            "Mu corregido seg\u00fan NTP E.060.\n"
            "As = Mu / (\u03c6 fy d (1-0.59\u03b2))\n"
            "d = h - r - \u03c6_estribo - 0.5 \u03c6_barra\n"
            "As_{min} = 0.7 \u221a(fc)/fy * b * d\n"
            "As_{max} = p_{max} * b * d"
        )
        QMessageBox.information(self, title, text)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MomentApp()
    sys.exit(app.exec_())
