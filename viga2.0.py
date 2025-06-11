import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QLabel,
    QLineEdit, QPushButton, QRadioButton, QButtonGroup, QMessageBox
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

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)

        labels = [
            ("b (cm)", "30"),
            ("h (cm)", "50"),
            ("r (cm)", "4"),
            ("f'c (kg/cm²)", "280"),
            ("fy (kg/cm²)", "4200"),
            ("φ", "0.9"),
            ("ϕ estribo (cm)", "1.0"),
            ("ϕ varilla (cm)", "1.6"),
        ]

        self.edits = {}
        for row, (text, val) in enumerate(labels):
            layout.addWidget(QLabel(text), row, 0)
            ed = QLineEdit(val)
            ed.setAlignment(Qt.AlignRight)
            layout.addWidget(ed, row, 1)
            self.edits[text] = ed

        layout.addWidget(QLabel("Varilla 1: n, ϕ(cm)"), 0, 2)
        self.v1n = QLineEdit("0")
        self.v1d = QLineEdit("0")
        layout.addWidget(self.v1n, 0, 3)
        layout.addWidget(self.v1d, 0, 4)

        layout.addWidget(QLabel("Varilla 2: n, ϕ(cm)"), 1, 2)
        self.v2n = QLineEdit("0")
        self.v2d = QLineEdit("0")
        layout.addWidget(self.v2n, 1, 3)
        layout.addWidget(self.v2d, 1, 4)

        layout.addWidget(QLabel("As total (cm²):"), 2, 2)
        self.as_total = QLabel("-")
        layout.addWidget(self.as_total, 2, 3, 1, 2)

        self.fig_sec, self.ax_sec = plt.subplots(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig_sec)
        layout.addWidget(self.canvas, 3, 0, 1, 5)

        for ed in self.edits.values():
            ed.editingFinished.connect(self.draw_section)
        self.draw_section()

    def draw_section(self):
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
            de = float(self.edits["ϕ estribo (cm)"].text())
            db = float(self.edits["ϕ varilla (cm)"].text())
        except ValueError:
            return

        d = h - r - de - 0.5 * db

        self.ax_sec.clear()
        self.ax_sec.set_aspect('equal')
        self.ax_sec.plot([0, b, b, 0, 0], [0, 0, h, h, 0], 'k-')
        self.ax_sec.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], 'r--')

        self.ax_sec.annotate('', xy=(0, -5), xytext=(b, -5), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(b / 2, -6, 'b', ha='center', va='top')

        self.ax_sec.annotate('', xy=(-5, 0), xytext=(-5, h), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(-6, h / 2, 'h', ha='right', va='center', rotation=90)

        self.ax_sec.annotate('', xy=(-2, h), xytext=(-2, d), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(-3, (h + d) / 2, 'd', ha='right', va='center', rotation=90)

        self.ax_sec.set_xlim(-10, b + 10)
        self.ax_sec.set_ylim(-10, h + 10)
        self.ax_sec.axis('off')
        self.canvas.draw()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MomentApp()
    sys.exit(app.exec_())
