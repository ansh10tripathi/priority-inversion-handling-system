"""
Priority Inversion Handling System — Desktop GUI
Run:  python gui/gui.py   (from project root)
      python -m gui.gui
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gui.controller import SimController, DEFAULT_TASKS

# ── Palette ──────────────────────────────────────────────────────────────────

BG          = '#1e1e2e'
PANEL_BG    = '#2a2a3e'
BORDER      = '#44475a'
FG          = '#cdd6f4'
FG_DIM      = '#6c7086'
ACCENT      = '#89b4fa'
GREEN       = '#a6e3a1'
RED         = '#f38ba8'
YELLOW      = '#f9e2af'
ORANGE      = '#fab387'
PURPLE      = '#cba6f7'
TEAL        = '#94e2d5'

TASK_COLORS = [
    '#89b4fa', '#a6e3a1', '#f38ba8', '#fab387',
    '#cba6f7', '#94e2d5', '#f9e2af', '#89dceb',
]

GANTT_ROW_H  = 28
GANTT_COL_W  = 40
GANTT_LEFT   = 70   # label column width
GANTT_TOP    = 10

AUTO_DELAY_MS = 700   # milliseconds between auto-play steps


# ── Helpers ──────────────────────────────────────────────────────────────────

def _label(parent, text, fg=FG, bg=PANEL_BG, font=('Consolas', 10), **kw):
    return tk.Label(parent, text=text, fg=fg, bg=bg, font=font, **kw)


def _frame(parent, bg=PANEL_BG, **kw):
    return tk.Frame(parent, bg=bg, **kw)


def _section_title(parent, text):
    f = _frame(parent)
    f.pack(fill='x', pady=(8, 2))
    tk.Label(f, text=text, fg=ACCENT, bg=PANEL_BG,
             font=('Consolas', 10, 'bold')).pack(side='left', padx=6)
    tk.Frame(f, bg=BORDER, height=1).pack(side='left', fill='x', expand=True, padx=4)
    return f


# ── Main Application ─────────────────────────────────────────────────────────

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Priority Inversion Handling System — Simulator')
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1100, 700)

        self._ctrl        = SimController()
        self._running     = False       # auto-play state
        self._after_id    = None
        self._task_rows   = []          # list of dicts from the form
        self._color_map   = {}          # task_id → hex color
        self._gantt_cols  = 0           # how many time columns drawn so far
        self._gantt_tasks = []          # ordered task ids for gantt rows
        self._last_blocked = []         # blocked list from last snapshot

        self._build_ui()
        self._load_example()            # start with default tasks visible

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── top bar ─────────────────────────────────────────────────────────
        top = _frame(self, bg=BG)
        top.pack(fill='x', padx=8, pady=6)

        _label(top, '  Priority Inversion Simulator',
               fg=ACCENT, bg=BG, font=('Consolas', 13, 'bold')).pack(side='left')

        # protocol
        _label(top, '  Protocol:', bg=BG, fg=FG_DIM).pack(side='left', padx=(20, 4))
        self._protocol_var = tk.StringVar(value='None')
        self._proto_cb = ttk.Combobox(top, textvariable=self._protocol_var,
                                      values=['None', 'PIP', 'PCP'],
                                      state='readonly', width=6,
                                      font=('Consolas', 10))
        self._proto_cb.pack(side='left')

        # speed
        _label(top, '  Speed (ms):', bg=BG, fg=FG_DIM).pack(side='left', padx=(16, 4))
        self._speed_var = tk.IntVar(value=AUTO_DELAY_MS)
        tk.Scale(top, from_=100, to=2000, orient='horizontal',
                 variable=self._speed_var, bg=BG, fg=FG, troughcolor=BORDER,
                 highlightthickness=0, length=120).pack(side='left')

        # buttons
        btn_cfg = dict(font=('Consolas', 10, 'bold'), relief='flat',
                       padx=10, pady=4, cursor='hand2')
        self._btn_run    = tk.Button(top, text='Run',    bg=GREEN,  fg=BG,
                                     command=self._on_run,    **btn_cfg)
        self._btn_pause  = tk.Button(top, text='Pause',  bg=YELLOW, fg=BG,
                                     command=self._on_pause,  **btn_cfg)
        self._btn_step   = tk.Button(top, text='Step',   bg=ACCENT, fg=BG,
                                     command=self._on_step,   **btn_cfg)
        self._btn_reset  = tk.Button(top, text='Reset',  bg=ORANGE, fg=BG,
                                     command=self._on_reset,  **btn_cfg)
        self._btn_graphs = tk.Button(top, text='Graphs', bg=PURPLE, fg=BG,
                                     command=self._on_show_graphs, **btn_cfg)

        for b in (self._btn_run, self._btn_pause, self._btn_step,
                  self._btn_reset, self._btn_graphs):
            b.pack(side='left', padx=4)

        # time display
        self._time_var = tk.StringVar(value='T = —')
        _label(top, '', bg=BG, textvariable=self._time_var,
               fg=PURPLE, font=('Consolas', 12, 'bold')).pack(side='right', padx=12)

        # ── main body ───────────────────────────────────────────────────────
        body = _frame(self, bg=BG)
        body.pack(fill='both', expand=True, padx=8, pady=4)

        body.columnconfigure(0, weight=0, minsize=230)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(2, weight=0, minsize=200)
        body.rowconfigure(0, weight=1)
        body.rowconfigure(1, weight=0, minsize=160)

        self._build_left(body)
        self._build_center(body)
        self._build_right(body)
        self._build_bottom(body)

    # ── left panel ──────────────────────────────────────────────────────────

    def _build_left(self, parent):
        left = _frame(parent, bg=PANEL_BG,
                      highlightbackground=BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 4), pady=(0, 4))

        _section_title(left, '  ➕  Add Task')

        form = _frame(left)
        form.pack(fill='x', padx=8)

        fields = [
            ('Name',       'entry'),
            ('Priority',   'entry'),
            ('Arrival',    'entry'),
            ('Execution',  'entry'),
            ('Needs Res.', 'check'),
        ]
        self._form_vars = {}
        for label, kind in fields:
            row = _frame(form)
            row.pack(fill='x', pady=2)
            _label(row, f'{label:<11}', fg=FG_DIM, font=('Consolas', 9)).pack(side='left')
            if kind == 'entry':
                var = tk.StringVar()
                e = tk.Entry(row, textvariable=var, bg=BG, fg=FG,
                             insertbackground=FG, relief='flat',
                             font=('Consolas', 10), width=10)
                e.pack(side='left', fill='x', expand=True)
                self._form_vars[label] = var
            else:
                var = tk.BooleanVar()
                tk.Checkbutton(row, variable=var, bg=PANEL_BG,
                               activebackground=PANEL_BG,
                               selectcolor=BG).pack(side='left')
                self._form_vars[label] = var

        btn_row = _frame(left)
        btn_row.pack(fill='x', padx=8, pady=6)
        tk.Button(btn_row, text='Add Task', bg=ACCENT, fg=BG,
                  font=('Consolas', 9, 'bold'), relief='flat',
                  padx=8, pady=3, cursor='hand2',
                  command=self._on_add_task).pack(side='left')
        tk.Button(btn_row, text='Load Example', bg=TEAL, fg=BG,
                  font=('Consolas', 9, 'bold'), relief='flat',
                  padx=8, pady=3, cursor='hand2',
                  command=self._load_example).pack(side='left', padx=(6, 0))

        _section_title(left, '  📋  Task List')

        cols = ('ID', 'P', 'Arr', 'Exec', 'Res')
        self._task_tree = ttk.Treeview(left, columns=cols, show='headings',
                                       height=8, selectmode='browse')
        widths = (40, 30, 35, 40, 35)
        for col, w in zip(cols, widths):
            self._task_tree.heading(col, text=col)
            self._task_tree.column(col, width=w, anchor='center')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=BG, foreground=FG,
                        fieldbackground=BG, rowheight=22,
                        font=('Consolas', 9))
        style.configure('Treeview.Heading', background=BORDER,
                        foreground=ACCENT, font=('Consolas', 9, 'bold'))
        style.map('Treeview', background=[('selected', ACCENT)],
                  foreground=[('selected', BG)])

        self._task_tree.pack(fill='both', expand=True, padx=8, pady=4)

        tk.Button(left, text='Remove Selected', bg=RED, fg=BG,
                  font=('Consolas', 9, 'bold'), relief='flat',
                  padx=6, pady=2, cursor='hand2',
                  command=self._on_remove_task).pack(padx=8, pady=(0, 8))

    # ── center panel ────────────────────────────────────────────────────────

    def _build_center(self, parent):
        center = _frame(parent, bg=PANEL_BG,
                        highlightbackground=BORDER, highlightthickness=1)
        center.grid(row=0, column=1, sticky='nsew', padx=4, pady=(0, 4))

        _section_title(center, '  📊  CPU Execution Timeline (Gantt)')

        # running task badge
        badge_row = _frame(center)
        badge_row.pack(fill='x', padx=10, pady=(0, 4))
        _label(badge_row, 'Running:', fg=FG_DIM, font=('Consolas', 9)).pack(side='left')
        self._running_var = tk.StringVar(value='—')
        _label(badge_row, '', textvariable=self._running_var,
               fg=GREEN, font=('Consolas', 11, 'bold')).pack(side='left', padx=6)

        # canvas + scrollbar
        canvas_frame = _frame(center)
        canvas_frame.pack(fill='both', expand=True, padx=8, pady=4)

        self._gantt_canvas = tk.Canvas(canvas_frame, bg=BG,
                                       highlightthickness=0)
        h_scroll = tk.Scrollbar(canvas_frame, orient='horizontal',
                                command=self._gantt_canvas.xview)
        self._gantt_canvas.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side='bottom', fill='x')
        self._gantt_canvas.pack(fill='both', expand=True)

        # metrics strip
        _section_title(center, '  📈  Metrics')
        self._metrics_frame = _frame(center)
        self._metrics_frame.pack(fill='x', padx=10, pady=(0, 8))
        self._metric_labels = {}
        metric_names = [
            ('Total Time',    'total_time'),
            ('Avg Wait',      'avg_waiting_time'),
            ('Avg Turnaround','avg_turnaround_time'),
            ('CPU Util %',    'cpu_utilization'),
            ('Ctx Switches',  'context_switches'),
            ('Inv. Count',    'priority_inversion_count'),
            ('Inv. Duration', 'priority_inversion_duration'),
        ]
        for i, (name, key) in enumerate(metric_names):
            col = i % 4
            row_idx = i // 4
            cell = _frame(self._metrics_frame)
            cell.grid(row=row_idx, column=col, padx=6, pady=2, sticky='w')
            _label(cell, f'{name}:', fg=FG_DIM, font=('Consolas', 8)).pack(side='left')
            var = tk.StringVar(value='—')
            _label(cell, '', textvariable=var,
                   fg=YELLOW, font=('Consolas', 9, 'bold')).pack(side='left', padx=3)
            self._metric_labels[key] = var

    # ── right panel ─────────────────────────────────────────────────────────

    def _build_right(self, parent):
        right = _frame(parent, bg=PANEL_BG,
                       highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=2, sticky='nsew', padx=(4, 0), pady=(0, 4))

        _section_title(right, '  🟢  Ready Queue')
        self._ready_frame = _frame(right)
        self._ready_frame.pack(fill='x', padx=8, pady=4)

        _section_title(right, '  🔴  Blocked Queue')
        self._blocked_frame = _frame(right)
        self._blocked_frame.pack(fill='x', padx=8, pady=4)

        _section_title(right, '  🔒  Mutex')
        mutex_row = _frame(right)
        mutex_row.pack(fill='x', padx=8, pady=4)
        _label(mutex_row, 'Owner:', fg=FG_DIM, font=('Consolas', 9)).pack(side='left')
        self._mutex_var = tk.StringVar(value='None')
        _label(mutex_row, '', textvariable=self._mutex_var,
               fg=ORANGE, font=('Consolas', 10, 'bold')).pack(side='left', padx=4)

        _section_title(right, '  🎨  Legend')
        legend_f = _frame(right)
        legend_f.pack(fill='x', padx=8, pady=4)
        for color, label in [(GREEN, 'Running'), (ACCENT, 'Ready'),
                              (RED, 'Blocked'), (ORANGE, 'Holds Mutex')]:
            row = _frame(legend_f)
            row.pack(fill='x', pady=1)
            tk.Frame(row, bg=color, width=14, height=14).pack(side='left', padx=(0, 6))
            _label(row, label, fg=FG_DIM, font=('Consolas', 8)).pack(side='left')

    # ── bottom panel ────────────────────────────────────────────────────────

    def _build_bottom(self, parent):
        bottom = _frame(parent, bg=PANEL_BG,
                        highlightbackground=BORDER, highlightthickness=1)
        bottom.grid(row=1, column=0, columnspan=3,
                    sticky='nsew', pady=(4, 0))

        _section_title(bottom, '  📝  Event Log')

        log_frame = _frame(bottom)
        log_frame.pack(fill='both', expand=True, padx=8, pady=(0, 6))

        self._log_text = tk.Text(log_frame, bg=BG, fg=FG,
                                 font=('Consolas', 9), height=6,
                                 relief='flat', state='disabled',
                                 wrap='word')
        v_scroll = tk.Scrollbar(log_frame, command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side='right', fill='y')
        self._log_text.pack(fill='both', expand=True)

        # colour tags
        self._log_text.tag_config('inv',      foreground=RED,    font=('Consolas', 9, 'bold'))
        self._log_text.tag_config('protocol', foreground=PURPLE, font=('Consolas', 9, 'bold'))
        self._log_text.tag_config('complete', foreground=GREEN,  font=('Consolas', 9, 'bold'))
        self._log_text.tag_config('time',     foreground=FG_DIM)
        self._log_text.tag_config('resource', foreground=ORANGE)

    # ── task management ──────────────────────────────────────────────────────

    def _on_add_task(self):
        try:
            name  = self._form_vars['Name'].get().strip()
            prio  = int(self._form_vars['Priority'].get())
            arr   = int(self._form_vars['Arrival'].get())
            exe   = int(self._form_vars['Execution'].get())
            res   = self._form_vars['Needs Res.'].get()

            if not name:
                raise ValueError('Name cannot be empty')
            if prio < 1:
                raise ValueError('Priority must be >= 1')
            if arr < 0:
                raise ValueError('Arrival must be >= 0')
            if exe < 1:
                raise ValueError('Execution must be >= 1')
            if any(r['task_id'] == name for r in self._task_rows):
                raise ValueError(f"Task '{name}' already exists")

        except ValueError as e:
            messagebox.showerror('Invalid Input', str(e))
            return

        self._task_rows.append(dict(
            task_id=name, priority=prio,
            arrival_time=arr, execution_time=exe,
            needs_resource=res,
        ))
        self._refresh_task_tree()

        # clear form
        for key in ('Name', 'Priority', 'Arrival', 'Execution'):
            self._form_vars[key].set('')
        self._form_vars['Needs Res.'].set(False)

    def _on_remove_task(self):
        sel = self._task_tree.selection()
        if not sel:
            return
        item = self._task_tree.item(sel[0])
        tid  = item['values'][0]
        self._task_rows = [r for r in self._task_rows if r['task_id'] != tid]
        self._refresh_task_tree()

    def _load_example(self):
        self._task_rows = [dict(**d) for d in DEFAULT_TASKS]
        self._refresh_task_tree()
        self._log('Loaded default priority-inversion scenario (L / H / M)', 'time')

    def _refresh_task_tree(self):
        for item in self._task_tree.get_children():
            self._task_tree.delete(item)
        for r in self._task_rows:
            res = '✓' if r['needs_resource'] else ''
            self._task_tree.insert('', 'end', values=(
                r['task_id'], r['priority'],
                r['arrival_time'], r['execution_time'], res,
            ))

    # ── simulation controls ──────────────────────────────────────────────────

    def _on_run(self):
        if self._ctrl.is_finished():
            return
        if not self._running:
            self._ensure_initialised()
            self._running = True
            self._proto_cb.configure(state='disabled')  # lock protocol during run
            self._schedule_tick()

    def _on_pause(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _on_step(self):
        self._on_pause()
        self._ensure_initialised()
        if not self._ctrl.is_finished():
            self._do_tick()

    def _on_reset(self):
        self._on_pause()
        self._running  = False
        self._ctrl     = SimController()
        self._color_map.clear()
        self._gantt_cols  = 0
        self._gantt_tasks = []
        self._gantt_canvas.delete('all')
        self._running_var.set('—')
        self._mutex_var.set('None')
        self._time_var.set('T = —')
        self._clear_queue_panel(self._ready_frame)
        self._clear_queue_panel(self._blocked_frame)
        for var in self._metric_labels.values():
            var.set('—')
        self._log_text.configure(state='normal')
        self._log_text.delete('1.0', 'end')
        self._log_text.configure(state='disabled')
        self._proto_cb.configure(state='readonly')  # unlock protocol on reset

    def _on_show_graphs(self):
        """Generate matplotlib Gantt chart from completed simulation."""
        if not self._ctrl.is_finished():
            messagebox.showinfo('Graphs', 'Run the simulation to completion first.')
            return
        try:
            from visualization import plot_gantt_chart
            protocol = self._ctrl._protocol
            tasks    = self._ctrl._tasks
            timeline = self._ctrl._timeline
            rich_tl  = self._ctrl._rich_timeline
            plot_gantt_chart(timeline, tasks, protocol,
                             output_dir='output', rich_timeline=rich_tl)
            path = f'output/gantt_{protocol.lower()}.png'
            self._log(f'Gantt chart saved: {path}', 'complete')
            messagebox.showinfo('Graphs', f'Saved: {path}')
        except Exception as e:
            messagebox.showerror('Graph Error', str(e))

    def _ensure_initialised(self):
        """Initialise controller if not yet started for this run."""
        if self._ctrl.is_finished():
            return
        if self._ctrl._tasks:   # already initialised
            return
        task_dicts = self._task_rows if self._task_rows else list(DEFAULT_TASKS)
        protocol   = self._protocol_var.get()
        self._ctrl.reset(task_dicts, protocol)
        self._assign_colors(task_dicts)
        self._gantt_tasks = [d['task_id'] for d in task_dicts]
        self._draw_gantt_labels()
        self._log(f'--- Simulation started  Protocol: {protocol} ---', 'time')
        self._log(f'    Tasks: {[d["task_id"] for d in task_dicts]}', 'time')

    def _schedule_tick(self):
        if self._running and not self._ctrl.is_finished():
            self._do_tick()
            if self._ctrl.is_finished():
                # Simulation ended during this tick — clean up
                self._running = False
                self._proto_cb.configure(state='readonly')
            else:
                self._after_id = self.after(self._speed_var.get(), self._schedule_tick)
        else:
            self._running = False

    def _do_tick(self):
        snap = self._ctrl.tick()
        self._apply_snapshot(snap)

    # ── snapshot → UI ────────────────────────────────────────────────────────

    def _apply_snapshot(self, snap):
        self._time_var.set(f'T = {snap.time}')
        self._last_blocked = snap.blocked  # track for Gantt coloring

        # running badge
        if snap.running:
            self._running_var.set(f'Task {snap.running}')
        else:
            self._running_var.set('IDLE')

        # gantt — pass mutex_owner so it can color the holder orange
        self._draw_gantt_block(snap.time, snap.running, snap.mutex_owner)

        # queues
        self._update_queue(self._ready_frame,   snap.ready,   ACCENT)
        self._update_queue(self._blocked_frame, snap.blocked, RED)

        # mutex
        self._mutex_var.set(snap.mutex_owner if snap.mutex_owner else 'None')

        # events → log
        for ev in snap.events:
            if 'Inversion' in ev:
                tag = 'inv'
            elif 'PIP' in ev or 'PCP' in ev:
                tag = 'protocol'
            elif 'Completed' in ev or 'Complete' in ev:
                tag = 'complete'
            elif 'Mutex' in ev or 'released' in ev or 'Released' in ev:
                tag = 'resource'
            else:
                tag = 'time'
            self._log(f'[T={snap.time}] {ev}', tag)

        # metrics (only when done)
        if snap.done and snap.metrics:
            self._update_metrics(snap.metrics)

    # ── Gantt chart ──────────────────────────────────────────────────────────

    def _assign_colors(self, task_dicts):
        for i, d in enumerate(task_dicts):
            self._color_map[d['task_id']] = TASK_COLORS[i % len(TASK_COLORS)]

    def _draw_gantt_labels(self):
        c = self._gantt_canvas
        c.delete('all')
        self._gantt_cols = 0
        for i, tid in enumerate(self._gantt_tasks):
            y = GANTT_TOP + i * GANTT_ROW_H + GANTT_ROW_H // 2
            color = self._color_map.get(tid, FG)
            c.create_text(GANTT_LEFT - 6, y, text=tid,
                          fill=color, anchor='e',
                          font=('Consolas', 9, 'bold'))
        # horizontal grid lines
        total_h = GANTT_TOP + len(self._gantt_tasks) * GANTT_ROW_H
        c.create_line(GANTT_LEFT, GANTT_TOP, GANTT_LEFT, total_h,
                      fill=BORDER, width=1)

    def _draw_gantt_block(self, time_unit, running_id, mutex_owner_id=None):
        c   = self._gantt_canvas
        col = self._gantt_cols

        x0 = GANTT_LEFT + col * GANTT_COL_W
        x1 = x0 + GANTT_COL_W

        for i, tid in enumerate(self._gantt_tasks):
            y0 = GANTT_TOP + i * GANTT_ROW_H + 2
            y1 = y0 + GANTT_ROW_H - 4

            if tid == running_id:
                # orange if holding mutex, green otherwise
                fill = ORANGE if mutex_owner_id == tid else self._color_map.get(tid, GREEN)
                c.create_rectangle(x0, y0, x1, y1,
                                   fill=fill, outline=BG, width=1)
                c.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                              text=str(time_unit),
                              fill=BG, font=('Consolas', 7, 'bold'))
            elif tid in [b[0] for b in self._last_blocked]:
                # red tint for blocked tasks
                c.create_rectangle(x0, y0, x1, y1,
                                   fill='#3d1a1a', outline=RED, width=1)
            else:
                c.create_rectangle(x0, y0, x1, y1,
                                   fill=PANEL_BG, outline=BORDER, width=1)

        # time tick below chart
        total_h = GANTT_TOP + len(self._gantt_tasks) * GANTT_ROW_H
        c.create_text(x0 + GANTT_COL_W // 2, total_h + 10,
                      text=str(time_unit),
                      fill=FG_DIM, font=('Consolas', 7))

        self._gantt_cols += 1

        # expand scroll region
        total_w = GANTT_LEFT + self._gantt_cols * GANTT_COL_W + 20
        c.configure(scrollregion=(0, 0, total_w, total_h + 24))
        c.xview_moveto(1.0)   # auto-scroll right

    # ── queue panels ─────────────────────────────────────────────────────────

    def _clear_queue_panel(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _update_queue(self, frame, items, color):
        self._clear_queue_panel(frame)
        if not items:
            _label(frame, 'empty', fg=FG_DIM,
                   font=('Consolas', 9, 'italic')).pack(anchor='w')
            return
        for tid, prio in items:
            row = _frame(frame)
            row.pack(fill='x', pady=1)
            tk.Frame(row, bg=color, width=8, height=8).pack(side='left', padx=(0, 4))
            _label(row, f'Task {tid}',
                   fg=color, font=('Consolas', 9, 'bold')).pack(side='left')
            _label(row, f'  P={prio}',
                   fg=FG_DIM, font=('Consolas', 8)).pack(side='left')

    # ── metrics strip ────────────────────────────────────────────────────────

    def _update_metrics(self, metrics):
        fmt = {
            'total_time':                  lambda v: str(v),
            'avg_waiting_time':            lambda v: f'{v:.2f}',
            'avg_turnaround_time':         lambda v: f'{v:.2f}',
            'cpu_utilization':             lambda v: f'{v:.1f}%',
            'context_switches':            lambda v: str(v),
            'priority_inversion_count':    lambda v: str(v),
            'priority_inversion_duration': lambda v: str(v),
        }
        for key, fn in fmt.items():
            if key in self._metric_labels and key in metrics:
                self._metric_labels[key].set(fn(metrics[key]))

    # ── log ──────────────────────────────────────────────────────────────────

    def _log(self, msg, tag='time'):
        self._log_text.configure(state='normal')
        self._log_text.insert('end', msg + '\n', tag)
        self._log_text.see('end')
        self._log_text.configure(state='disabled')


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = App()
    app.mainloop()
