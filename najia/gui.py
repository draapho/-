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
    "1 少阳(静)",
    "2 少阴(静)",
    "o 老阳(动)",
    "x 老阴(动)",
]

BAGUA_MAPPING = {
    "1 乾天(☰)": ["1 少阳(静)", "1 少阳(静)", "1 少阳(静)"],
    "2 兑泽(☱)": ["2 少阴(静)", "1 少阳(静)", "1 少阳(静)"],
    "3 离火(☲)": ["1 少阳(静)", "2 少阴(静)", "1 少阳(静)"],
    "4 震雷(☳)": ["2 少阴(静)", "2 少阴(静)", "1 少阳(静)"],
    "5 巽风(☴)": ["1 少阳(静)", "1 少阳(静)", "2 少阴(静)"],
    "6 坎水(☵)": ["2 少阴(静)", "1 少阳(静)", "2 少阴(静)"],
    "7 艮山(☶)": ["1 少阳(静)", "2 少阴(静)", "2 少阴(静)"],
    "8 坤地(☷)": ["2 少阴(静)", "2 少阴(静)", "2 少阴(静)"],
}


def _yao_from_combo(value: str) -> int:
    char = str(value).strip().split()[0].lower()

    mapping = {
        "2": 0,
        "1": 1,
        "x": 2,
        "o": 3,
    }

    return mapping.get(char, 0)


class NajiaApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("纳甲六爻排盘")
        self.minsize(920, 640)
        self.geometry("980x720")

        self._build_form()
        self._build_output()

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
        ttk.Label(row0, text="格式 YYYYMMDDHHmm 或 YYYYMMDD.HHmm").pack(side=tk.LEFT)

        row_mode = ttk.Frame(frm)
        row_mode.pack(fill=tk.X, pady=2)
        ttk.Label(row_mode, text="起卦方式").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="manual")
        ttk.Radiobutton(
            row_mode,
            text="梅花易·时间起卦(年支+农历月日+时支)",
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
            text="六爻(左:上卦 · 右:下卦)",
            padding=(12, 10),
        )
        row2.pack(fill=tk.X, pady=6)

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
        left_fr.grid_columnconfigure(1, weight=1)

        ttk.Label(left_fr, text="上卦", width=5, font=("", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8), pady=(0, 6)
        )
        self.upper_bagua_cb = ttk.Combobox(
            left_fr, values=list(BAGUA_MAPPING.keys()), state="readonly"
        )
        self.upper_bagua_cb.grid(row=0, column=1, sticky=tk.EW, pady=(0, 6))
        self.upper_bagua_cb.bind("<<ComboboxSelected>>", self._on_upper_bagua_selected)

        for r_idx, yao_idx in enumerate((5, 4, 3), start=1):
            ttk.Label(left_fr, text=YAO_LABELS[yao_idx], width=5).grid(
                row=r_idx, column=0, sticky=tk.W, padx=(0, 8), pady=5
            )
            cb = ttk.Combobox(left_fr, values=YAO_OPTIONS, state="readonly")
            cb.set(YAO_OPTIONS[0])
            cb.grid(row=r_idx, column=1, sticky=tk.EW, pady=5)
            self.yao_boxes[yao_idx] = cb

        ttk.Separator(inner, orient=tk.VERTICAL).grid(
            row=0, column=1, sticky=tk.NS, padx=6
        )

        right_fr = ttk.Frame(inner, padding=(8, 0, 0, 0))
        right_fr.grid(row=0, column=2, sticky=tk.NSEW)
        right_fr.grid_columnconfigure(1, weight=1)

        ttk.Label(right_fr, text="下卦", width=5, font=("", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8), pady=(0, 6)
        )
        self.lower_bagua_cb = ttk.Combobox(
            right_fr, values=list(BAGUA_MAPPING.keys()), state="readonly"
        )
        self.lower_bagua_cb.grid(row=0, column=1, sticky=tk.EW, pady=(0, 6))
        self.lower_bagua_cb.bind("<<ComboboxSelected>>", self._on_lower_bagua_selected)

        for r_idx, yao_idx in enumerate((2, 1, 0), start=1):
            ttk.Label(right_fr, text=YAO_LABELS[yao_idx], width=5).grid(
                row=r_idx, column=0, sticky=tk.W, padx=(0, 8), pady=5
            )
            cb = ttk.Combobox(right_fr, values=YAO_OPTIONS, state="readonly")
            cb.set(YAO_OPTIONS[0])
            cb.grid(row=r_idx, column=1, sticky=tk.EW, pady=5)
            self.yao_boxes[yao_idx] = cb
        # 设置默认值为 "1 乾天(☰)" 并自动同步至各爻
        default_bagua = "1 乾天(☰)"
        self.upper_bagua_cb.set(default_bagua)
        self._on_upper_bagua_selected()
        self.lower_bagua_cb.set(default_bagua)
        self._on_lower_bagua_selected()

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
        gender_cb = ttk.Combobox(
            row3,
            textvariable=self.gender_var,
            values=["", "男", "女"],
            width=6,
            state="readonly",
        )
        gender_cb.pack(side=tk.LEFT, padx=6)
        self.guaci_var = tk.BooleanVar(value=True)
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

        self.guaci_outer = ttk.Frame(self._scroll_inner)
        self.guaci_outer.pack(fill=tk.X, pady=(6, 0))
        self.guaci_outer.pack_forget()
        gh = ttk.Label(
            self.guaci_outer,
            text="卦辞 · 彖传 · 象传 · 爻辞（左：本卦 右：变卦）",
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

    def _on_upper_bagua_selected(self, event=None) -> None:
        bagua = self.upper_bagua_cb.get()
        if bagua in BAGUA_MAPPING:
            yaos = BAGUA_MAPPING[bagua]
            self.yao_boxes[5].set(yaos[0])
            self.yao_boxes[4].set(yaos[1])
            self.yao_boxes[3].set(yaos[2])

    def _on_lower_bagua_selected(self, event=None) -> None:
        bagua = self.lower_bagua_cb.get()
        if bagua in BAGUA_MAPPING:
            yaos = BAGUA_MAPPING[bagua]
            self.yao_boxes[2].set(yaos[0])
            self.yao_boxes[1].set(yaos[1])
            self.yao_boxes[0].set(yaos[2])

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
        state = "readonly" if manual else "disabled"
        for cb in self.yao_boxes:
            cb.configure(state=state)
        if hasattr(self, "upper_bagua_cb"):
            self.upper_bagua_cb.configure(state=state)
            self.lower_bagua_cb.configure(state=state)

    def _collect_params(self) -> list[int]:
        return [_yao_from_combo(cb.get()) for cb in self.yao_boxes]

    def _run(self) -> None:
        date_s = self.date_var.get().strip()
        try:
            if len(date_s) == 12 and date_s.isdigit():
                dt = arrow.get(date_s, "YYYYMMDDHHmm")
            elif len(date_s) == 13 and date_s.replace(".", "").isdigit():
                dt = arrow.get(date_s, "YYYYMMDD.HHmm")
            else:
                dt = arrow.get(date_s)
            date_s = dt.format("YYYY-MM-DD HH:mm")
        except Exception:
            messagebox.showerror(
                "日期无效. 请使用如下格式: ",
                "202512060000, 20251206.0000",
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

        n = Najia().compile(
            params=params,
            gender=gender or None,
            date=date_s,
            title=title or None,
            guaci=guaci,
        )
        text = n.render()

        self.hex_text.delete("1.0", tk.END)
        self.hex_text.insert(tk.END, text.rstrip() + "\n")

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