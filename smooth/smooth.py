import os
import sys
import math
import tkinter as tk
from tkinter import filedialog, messagebox

# ---------- 移动平均核心函数 ----------
def moving_average_symmetric(vals, window):
    n = len(vals)
    if n == 0:
        return vals
    smoothed = list(vals)
    half_win = (window - 1) // 2
    for i in range(half_win, n - half_win):
        window_vals = vals[i - half_win : i + half_win + 1]
        valid = [x for x in window_vals if not math.isnan(x)]
        if valid:
            smoothed[i] = sum(valid) / len(valid)
        else:
            smoothed[i] = float('nan')
    return smoothed

# ---------- 主处理逻辑（增加 placeholder 参数）----------
def process_file(input_path, interval, x_skip, y_skip, placeholder=' '):
    # 读取全部行
    with open(input_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    # 标题行与数据行分离
    header_lines = all_lines[:y_skip] if y_skip > 0 else []
    data_lines = all_lines[y_skip:]

    # 确定数值列数
    num_cols = None
    for line in data_lines:
        stripped = line.rstrip('\n\r')
        if stripped.strip() != '':
            parts = stripped.split('\t')
            if len(parts) > x_skip:
                num_cols = len(parts) - x_skip
                break
    if num_cols is None:
        raise ValueError("数据行中没有找到有效的数值列。")

    # 解析每一行
    index_parts = []
    numeric_data = []
    for line in data_lines:
        stripped = line.rstrip('\n\r')
        if stripped.strip() == '':
            index_parts.append([''] * x_skip)
            numeric_data.append([float('nan')] * num_cols)
            continue
        parts = stripped.split('\t')
        idx = []
        vals = []
        if len(parts) <= x_skip:
            idx = [''] * x_skip
            vals = [float('nan')] * num_cols
        else:
            idx = parts[:x_skip]
            raw_vals = parts[x_skip:]
            for j in range(num_cols):
                if j < len(raw_vals):
                    try:
                        val = float(raw_vals[j])
                    except ValueError:
                        val = float('nan')
                    vals.append(val)
                else:
                    vals.append(float('nan'))
        index_parts.append(idx)
        numeric_data.append(vals)

    # 逐列平滑
    columns = list(zip(*numeric_data))
    smoothed_columns = []
    for col_vals in columns:
        smoothed_columns.append(
            moving_average_symmetric(list(col_vals), interval)
        )
    smoothed_rows = list(zip(*smoothed_columns))

    # 输出文件名
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_analysis{ext}"

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in header_lines:
            f.write(line)
        for idx_list, sm_row in zip(index_parts, smoothed_rows):
            out_parts = list(idx_list)
            for v in sm_row:
                if math.isnan(v):
                    out_parts.append(placeholder)   # 使用用户指定的占位符
                else:
                    out_parts.append(str(v))
            f.write('\t'.join(out_parts) + '\n')
    return output_path

# ---------- GUI 界面 ----------
class SmoothingApp:
    def __init__(self, root):
        self.root = root
        root.title("移动平均平滑工具")
        root.resizable(False, False)

        # ---- 变量绑定 ----
        self.input_file = tk.StringVar()
        self.interval = tk.IntVar(value=5)
        self.x_skip = tk.IntVar(value=0)
        self.y_skip = tk.IntVar(value=0)
        self.placeholder_var = tk.StringVar(value=' ')   # 默认一个空格

        # ---- 布局 ----
        # 第0行：文件选择
        tk.Label(root, text="输入文件 (.tsv/.txt)：").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(root, textvariable=self.input_file, width=40).grid(row=0, column=1, padx=5)
        tk.Button(root, text="浏览...", command=self.choose_file).grid(row=0, column=2, padx=5)

        # 第1行：窗口长度
        tk.Label(root, text="窗口长度 (奇数)：").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(root, textvariable=self.interval, width=10).grid(row=1, column=1, sticky='w', padx=5)

        # 第2行：忽略前x列
        tk.Label(root, text="忽略前 x 列：").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(root, textvariable=self.x_skip, width=10).grid(row=2, column=1, sticky='w', padx=5)

        # 第3行：忽略前y行
        tk.Label(root, text="忽略前 y 行：").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(root, textvariable=self.y_skip, width=10).grid(row=3, column=1, sticky='w', padx=5)

        # 第4行：缺失值占位符
        tk.Label(root, text="缺失值占位符：").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        tk.Entry(root, textvariable=self.placeholder_var, width=10).grid(row=4, column=1, sticky='w', padx=5)
        tk.Label(root, text="（默认为一个空格）", fg='gray').grid(row=4, column=2, sticky='w', padx=5)

        # 第5行：开始按钮
        self.run_btn = tk.Button(root, text="开始平滑", command=self.run_smoothing, bg='#4CAF50', fg='white', font=('微软雅黑', 11))
        self.run_btn.grid(row=5, column=0, columnspan=3, pady=15)

        # 第6行：状态标签
        self.status = tk.Label(root, text="就绪", fg='gray')
        self.status.grid(row=6, column=0, columnspan=3, pady=5)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="选择制表符分隔的数据文件",
            filetypes=[("TSV/TXT 文件", "*.tsv *.txt"), ("所有文件", "*.*")]
        )
        if path:
            self.input_file.set(path)

    def run_smoothing(self):
        # 基本输入校验
        input_path = self.input_file.get().strip()
        if not input_path:
            messagebox.showerror("错误", "请先选择输入文件。")
            return
        if not os.path.isfile(input_path):
            messagebox.showerror("错误", "文件不存在，请重新选择。")
            return

        try:
            interval = self.interval.get()
        except tk.TclError:
            messagebox.showerror("错误", "窗口长度必须为整数。")
            return
        if interval < 3:
            messagebox.showerror("错误", "窗口长度至少为 3。")
            return
        if interval % 2 == 0:
            interval += 1
            self.interval.set(interval)

        try:
            x_skip = self.x_skip.get()
            y_skip = self.y_skip.get()
        except tk.TclError:
            messagebox.showerror("错误", "忽略行/列数必须为整数。")
            return
        if x_skip < 0 or y_skip < 0:
            messagebox.showerror("错误", "忽略行/列数不能为负数。")
            return

        placeholder = self.placeholder_var.get()
        if placeholder.strip() == '' and placeholder != ' ':
            # 若用户输入空白（即清空），自动恢复为空格
            placeholder = ' '
            self.placeholder_var.set(' ')

        # 执行处理
        self.status.config(text="正在处理，请稍候...", fg='blue')
        self.root.update()
        try:
            out_path = process_file(input_path, interval, x_skip, y_skip, placeholder)
            self.status.config(text=f"完成！结果文件：{os.path.basename(out_path)}", fg='green')
            messagebox.showinfo("成功", f"平滑已完成！\n输出文件：\n{out_path}")
        except Exception as e:
            self.status.config(text="处理失败", fg='red')
            messagebox.showerror("失败", f"发生错误：\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmoothingApp(root)
    root.mainloop()