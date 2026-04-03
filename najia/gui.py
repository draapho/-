"""
Desktop UI for najia: enter datetime and six yao values, display the same text
layout as Najia.render() (terminal output).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import arrow

from . import Najia
from .meihua import meihua_from_ymdhms

YAO_LABELS = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

YAO_OPTIONS = [
    "0 少阴(静)",
    "1 少阳(静)",
    "2 老阴(动)",
    "3 老阳(动)",
]


def _yao_from_combo(value: str) -> int:
    return int(str(value).strip().split()[0])


class NajiaApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("纳甲六爻排盘")
        self.minsize(920, 640)
        self.geometry("980x720")

        self._build_form()
        self._build_output()

        # 六爻表区域：仿终端深色
        self.hex_text.configure(
            bg="#0c1929",
            fg="#7fd7ff",
            insertbackground="#7fd7ff",
            selectbackground="#1e3a5f",
            selectforeground="#ffffff",
        )

    def _build_form(self) -> None:
        frm = ttk.Frame(self, padding=8)
        frm.pack(side=tk.TOP, fill=tk.X)

        row0 = ttk.Frame(frm)
        row0.pack(fill=tk.X, pady=2)
        ttk.Label(row0, text="公历日期时间").pack(side=tk.LEFT)
        now = arrow.now().format("YYYY-MM-DD HH:mm")
        self.date_var = tk.StringVar(value=now)
        ttk.Entry(row0, textvariable=self.date_var, width=22).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Label(row0, text="格式 YYYY-MM-DD HH:mm").pack(side=tk.LEFT)

        row_mode = ttk.Frame(frm)
        row_mode.pack(fill=tk.X, pady=2)
        ttk.Label(row_mode, text="起卦方式").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="meihua")
        ttk.Radiobutton(
            row_mode,
            text="梅花易·时间起卦（年支+农历月日+时支；与手写算法一致）",
            variable=self.mode_var,
            value="meihua",
            command=self._sync_mode_widgets,
        ).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(
            row_mode,
            text="手动六爻",
            variable=self.mode_var,
            value="manual",
            command=self._sync_mode_widgets,
        ).pack(side=tk.LEFT, padx=4)

        row2 = ttk.LabelFrame(
            frm,
            text="六爻（左：上卦 · 右：下卦；自上而下与卦象自下而上初→上一致）",
            padding=(12, 10),
        )
        row2.pack(fill=tk.X, pady=6)
        self._yao_hint = ttk.Label(
            row2,
            text=(
                "时间起卦时动爻与变卦由算法自动生成；手动模式请在下方选择 0–3。"
                "排盘含本卦、动爻标记、变卦列（静卦时变卦列为占位）。"
                "结果区仅右侧一条竖滚动条。"
            ),
            justify=tk.LEFT,
        )
        self._yao_hint.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))
        frm.bind(
            "<Configure>",
            lambda e: self._yao_hint.configure(wraplength=max(320, e.width - 48)),
            add="+",
        )

        self.yao_boxes: list[ttk.Combobox | None] = [None] * 6
        inner = ttk.Frame(row2)
        inner.pack(fill=tk.BOTH, expand=True)
        inner.grid_columnconfigure(0, weight=1, uniform="yao_cols")
        inner.grid_columnconfigure(2, weight=1, uniform="yao_cols")

        def _place_yao_row(parent: ttk.Frame, yao_idx: int) -> None:
            row_fr = ttk.Frame(parent)
            row_fr.pack(fill=tk.X, pady=5)
            row_fr.grid_columnconfigure(1, weight=1)
            ttk.Label(row_fr, text=YAO_LABELS[yao_idx], width=5).grid(
                row=0, column=0, sticky=tk.W, padx=(0, 8)
            )
            cb = ttk.Combobox(row_fr, values=YAO_OPTIONS, state="readonly")
            cb.set(YAO_OPTIONS[0])
            cb.grid(row=0, column=1, sticky=tk.EW)
            self.yao_boxes[yao_idx] = cb

        left_fr = ttk.Frame(inner, padding=(0, 0, 8, 0))
        left_fr.grid(row=0, column=0, sticky=tk.NSEW)
        ttk.Label(left_fr, text="上卦", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 6)
        )
        for yao_idx in (5, 4, 3):
            _place_yao_row(left_fr, yao_idx)

        ttk.Separator(inner, orient=tk.VERTICAL).grid(
            row=0, column=1, sticky=tk.NS, padx=6
        )

        right_fr = ttk.Frame(inner, padding=(8, 0, 0, 0))
        right_fr.grid(row=0, column=2, sticky=tk.NSEW)
        ttk.Label(right_fr, text="下卦", font=("", 10, "bold")).pack(
            anchor=tk.W, pady=(0, 6)
        )
        for yao_idx in (2, 1, 0):
            _place_yao_row(right_fr, yao_idx)

        self._sync_mode_widgets()

        row3 = ttk.Frame(frm)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="测事").pack(side=tk.LEFT)
        self.title_var = tk.StringVar(value="")
        ttk.Entry(row3, textvariable=self.title_var, width=28).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Label(row3, text="性别").pack(side=tk.LEFT)
        self.gender_var = tk.StringVar(value="")
        ttk.Entry(row3, textvariable=self.gender_var, width=8).pack(
            side=tk.LEFT, padx=6
        )
        self.guaci_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row3, text="显示卦辞", variable=self.guaci_var).pack(
            side=tk.LEFT, padx=8
        )

        row4 = ttk.Frame(frm)
        row4.pack(fill=tk.X, pady=6)
        ttk.Button(row4, text="排盘", command=self._run).pack(side=tk.LEFT, padx=2)
        ttk.Button(row4, text="复制结果", command=self._copy).pack(
            side=tk.LEFT, padx=2
        )

    def _build_output(self) -> None:
        self._mono_font = self._pick_mono_font()
        self._output_wrap = ttk.Frame(self, padding=(8, 0, 8, 8))
        self._output_wrap.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._output_wrap.grid_columnconfigure(0, weight=1)
        self._output_wrap.grid_rowconfigure(0, weight=1)

        # 单一右侧纵轴滚动：Canvas + 内层 Frame（六爻 + 卦辞同卷）
        self._scroll_canvas = tk.Canvas(
            self._output_wrap,
            highlightthickness=0,
            bd=0,
            bg="#0c1929",
        )
        self._main_vsb = ttk.Scrollbar(
            self._output_wrap,
            orient=tk.VERTICAL,
            command=self._scroll_canvas.yview,
        )
        self._scroll_canvas.configure(yscrollcommand=self._main_vsb.set)
        self._scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self._main_vsb.grid(row=0, column=1, sticky="ns")

        self._scroll_inner = ttk.Frame(self._scroll_canvas)
        self._scroll_window = self._scroll_canvas.create_window(
            (0, 0), window=self._scroll_inner, anchor="nw"
        )

        def _on_inner_configure(_event=None):
            self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

        def _on_canvas_configure(ev: tk.Event) -> None:
            self._scroll_canvas.itemconfig(self._scroll_window, width=ev.width)

        self._scroll_inner.bind("<Configure>", lambda e: _on_inner_configure())
        self._scroll_canvas.bind("<Configure>", _on_canvas_configure)

        hex_wrap = ttk.Frame(self._scroll_inner)
        hex_wrap.pack(fill=tk.X)
        self.hex_text = tk.Text(
            hex_wrap,
            wrap=tk.NONE,
            height=12,
            bd=0,
            relief=tk.FLAT,
        )
        self.hex_text.pack(fill=tk.X)
        self.hex_text.configure(font=self._mono_font)

        # 卦辞爻辞：左右分栏 + 不同底色（仅勾选「显示卦辞」时出现）
        self.guaci_outer = ttk.Frame(self._scroll_inner)
        self.guaci_outer.pack(fill=tk.X, pady=(6, 0))
        self.guaci_outer.pack_forget()
        gh = ttk.Label(
            self.guaci_outer,
            text="卦辞 · 彖传 · 象传 · 爻辞（左：本卦　右：变卦）",
        )
        gh.pack(anchor=tk.W, pady=(0, 4))
        self.guaci_body = ttk.Frame(self.guaci_outer)
        self.guaci_body.pack(fill=tk.BOTH, expand=True)
        self.guaci_body.grid_columnconfigure(0, weight=1)
        self.guaci_body.grid_columnconfigure(1, weight=1)
        self.guaci_body.grid_rowconfigure(1, weight=1)

        self._guaci_hdr_left = ttk.Label(self.guaci_body, text="本卦")
        self._guaci_hdr_left.grid(row=0, column=0, sticky=tk.W)
        self._guaci_hdr_right = ttk.Label(self.guaci_body, text="变卦")
        self._guaci_hdr_right.grid(row=0, column=1, sticky=tk.W)

        left_bg, left_fg = "#132c45", "#aee4ff"
        right_bg, right_fg = "#2f1a24", "#ffc8e0"

        lf = ttk.Frame(self.guaci_body)
        lf.grid(row=1, column=0, sticky="nsew", padx=(0, 4))
        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)
        self.guaci_left = tk.Text(
            lf,
            wrap=tk.WORD,
            bd=0,
            relief=tk.FLAT,
            padx=8,
            pady=8,
            bg=left_bg,
            fg=left_fg,
            insertbackground=left_fg,
            selectbackground="#1e4a72",
            selectforeground="#ffffff",
        )
        self.guaci_left.configure(font=self._mono_font)
        self.guaci_left.grid(row=0, column=0, sticky="nsew")

        self._guaci_rf = ttk.Frame(self.guaci_body)
        rf = self._guaci_rf
        rf.grid(row=1, column=1, sticky="nsew", padx=(4, 0))
        rf.grid_rowconfigure(0, weight=1)
        rf.grid_columnconfigure(0, weight=1)
        self.guaci_right = tk.Text(
            rf,
            wrap=tk.WORD,
            bd=0,
            relief=tk.FLAT,
            padx=8,
            pady=8,
            bg=right_bg,
            fg=right_fg,
            insertbackground=right_fg,
            selectbackground="#5c2840",
            selectforeground="#ffffff",
        )
        self.guaci_right.configure(font=self._mono_font)
        self.guaci_right.grid(row=0, column=0, sticky="nsew")

        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self._scroll_canvas.bind(seq, self._on_output_mousewheel)
        self._bind_output_mousewheel_recursively(
            self._scroll_inner, self._on_output_mousewheel
        )

    def _on_output_mousewheel(self, event: tk.Event) -> str:
        d = 0
        if getattr(event, "delta", 0):
            d = int(-1 * (event.delta / 120))
        elif getattr(event, "num", None) == 4:
            d = -3
        elif getattr(event, "num", None) == 5:
            d = 3
        if d:
            self._scroll_canvas.yview_scroll(d, "units")
        return "break"

    def _bind_output_mousewheel_recursively(self, widget: tk.Misc, handler) -> None:
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            widget.bind(seq, handler)
        for ch in widget.winfo_children():
            self._bind_output_mousewheel_recursively(ch, handler)

    def _sync_scroll_region(self) -> None:
        """Text 按行数撑开高度，由外层 Canvas 统一滚动。"""
        self.update_idletasks()
        try:
            n = int(self.hex_text.index("end-1c").split(".")[0])
        except tk.TclError:
            n = 1
        self.hex_text.configure(height=max(1, n))
        if self.guaci_outer.winfo_ismapped():
            try:
                nl = int(self.guaci_left.index("end-1c").split(".")[0])
            except tk.TclError:
                nl = 1
            if self._guaci_rf.winfo_ismapped():
                try:
                    nr = int(self.guaci_right.index("end-1c").split(".")[0])
                except tk.TclError:
                    nr = 1
                hm = max(nl, nr, 1)
            else:
                hm = max(nl, 1)
            self.guaci_left.configure(height=hm)
            if self._guaci_rf.winfo_ismapped():
                self.guaci_right.configure(height=hm)
        bbox = self._scroll_canvas.bbox("all")
        if bbox:
            self._scroll_canvas.configure(scrollregion=bbox)

    def _pick_mono_font(self) -> tuple:
        for fam in ("NSimSun", "SimSun", "新宋体", "Microsoft YaHei Mono", "Consolas"):
            t = tk.Text(self)
            try:
                t.configure(font=(fam, 12))
                t.destroy()
                return (fam, 12)
            except tk.TclError:
                t.destroy()
                continue
        return ("Consolas", 12)

    def _fill_guaci_panels(self, payload: dict) -> None:
        self.guaci_left.delete("1.0", tk.END)
        self.guaci_right.delete("1.0", tk.END)
        if payload["mode"] == "single":
            self._guaci_hdr_right.grid_remove()
            self._guaci_rf.grid_remove()
            self.guaci_body.grid_columnconfigure(1, weight=0, minsize=0)
            self.guaci_left.insert("1.0", payload["text_left"])
            return
        self._guaci_hdr_right.grid(row=0, column=1, sticky=tk.W)
        self._guaci_rf.grid(row=1, column=1, sticky="nsew", padx=(4, 0))
        self.guaci_body.grid_columnconfigure(1, weight=1)
        mn, bn = payload["main_name"], payload["bian_name"]
        parts_l = [
            "【卦辞 · 彖传 · 象传】\n",
            f"「{mn}」\n\n",
            payload["preamble_left"],
            "\n\n【爻辞】\n\n",
        ]
        parts_r = [
            "【卦辞 · 彖传 · 象传】\n",
            f"「{bn}」\n\n",
            payload["preamble_right"],
            "\n\n【爻辞】\n\n",
        ]
        for y in payload["yaos"]:
            parts_l.append(f"── {y['label']} ──\n{y['left']}\n\n")
            parts_r.append(f"── {y['label']} ──\n{y['right']}\n\n")
        self.guaci_left.insert("1.0", "".join(parts_l))
        self.guaci_right.insert("1.0", "".join(parts_r))

    def _sync_mode_widgets(self) -> None:
        manual = self.mode_var.get() == "manual"
        for cb in self.yao_boxes:
            cb.configure(state="readonly" if manual else "disabled")

    def _collect_params(self) -> list[int]:
        return [_yao_from_combo(cb.get()) for cb in self.yao_boxes]

    def _run(self) -> None:
        date_s = self.date_var.get().strip()
        try:
            dt = arrow.get(date_s)
        except Exception:
            messagebox.showerror(
                "日期无效",
                "请使用形如 2025-12-06 00:00 的公历时间。",
            )
            return

        if self.mode_var.get() == "meihua":
            try:
                params, _meta = meihua_from_ymdhms(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    getattr(dt, "second", 0) or 0,
                )
            except Exception as ex:
                messagebox.showerror("梅花起卦失败", str(ex))
                return
        else:
            params = self._collect_params()

        title = self.title_var.get().strip()
        gender = self.gender_var.get().strip()
        guaci = bool(self.guaci_var.get())

        try:
            n = Najia().compile(
                params=params,
                gender=gender or None,
                date=date_s,
                title=title or None,
                guaci=guaci,
            )
            text = n.render(embed_guaci_plain=not guaci)
        except Exception as ex:
            messagebox.showerror("排盘失败", str(ex))
            return

        self.hex_text.delete("1.0", tk.END)
        self.hex_text.insert(tk.END, text.rstrip() + "\n")

        payload = n.guaci_dual_payload() if guaci else None
        if payload:
            self.guaci_outer.pack(fill=tk.X, pady=(6, 0))
            self._fill_guaci_panels(payload)
        else:
            self.guaci_outer.pack_forget()

        self._sync_scroll_region()
        self._scroll_canvas.yview_moveto(0)

    def _copy(self) -> None:
        parts = [self.hex_text.get("1.0", tk.END).rstrip()]
        if self.guaci_outer.winfo_ismapped():
            parts.append(self.guaci_left.get("1.0", tk.END).rstrip())
            if self._guaci_rf.winfo_ismapped():
                parts.append(self.guaci_right.get("1.0", tk.END).rstrip())
        s = "\n\n".join(p for p in parts if p) + "\n"
        self.clipboard_clear()
        self.clipboard_append(s)
        messagebox.showinfo("已复制", "结果已复制到剪贴板。")


def main() -> None:
    app = NajiaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
