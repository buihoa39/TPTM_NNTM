import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from sklearn.linear_model import LinearRegression

# Hàm xử lý dự đoán năng suất

def build_and_predict(sim_file_path, real_file_path):
    try:
        # Đọc dữ liệu mô phỏng và thực tế
        df_sim = pd.read_csv(sim_file_path)
        df_real = pd.read_csv(real_file_path)

        # Dữ liệu đầu vào thực tế
        real_temp = df_real.iloc[0]["Nhiet do TB (C)"]
        real_hum = df_real.iloc[0]["Do am TB (%)"]
        real_light = df_real.iloc[0]["Anh sang TB (lx)"]
        real_soil = df_real.iloc[0]["Do am dat TB (%)"]
        real_flow = df_real.iloc[0]["Luu luong TB (L/phut)"]

        real_input = [[real_temp, real_hum, real_light, real_soil, real_flow]]

        # Dự đoán và so sánh theo từng năm
        result_lines = []

        for year in sorted(df_sim['Nam'].unique()):
            df_year = df_sim[df_sim['Nam'] == year]
            X = df_year[[
                "Nhiet do TB (C)",
                "Do am TB (%)",
                "Anh sang TB (lx)",
                "Do am dat TB (%)",
                "Luu luong TB (L/phut)"
            ]]
            y = df_year["Nang suat thang (kg/ha)"]

            model = LinearRegression()
            model.fit(X, y)

            predicted_y = model.predict(real_input)[0]
            avg_sim_y = y.mean()
            delta_percent = ((predicted_y - avg_sim_y) / avg_sim_y) * 100

            result_lines.append(f"\n📅 Năm {year}:")
            result_lines.append(f"✅ Năng suất dự đoán: {round(predicted_y, 2)}")
            result_lines.append(f"📊 Trung bình năm {year}: {round(avg_sim_y, 2)}")
            result_lines.append(f"📈 % Chênh lệch: {round(delta_percent, 2)}%")

            # Lời khuyên
            avg_year_temp = df_year["Nhiet do TB (C)"].mean()
            if real_temp > avg_year_temp + 1:
                result_lines.append("🟠 Cảnh báo: Năm nay nhiệt độ cao hơn trung bình rõ rệt. Cần chú ý tưới nước và che phủ.")
            elif real_temp < avg_year_temp - 1:
                result_lines.append("🔵 Lưu ý: Năm nay mát hơn trung bình. Có thể điều chỉnh lịch bón phân để tối ưu.")
            else:
                result_lines.append("✅ Thời tiết năm nay tương đối ổn định so với trung bình năm.")

        return result_lines

    except Exception as e:
        return [f"Lỗi: {str(e)}"]

# Giao diện tkinter

def run_gui():
    def select_sim_file():
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            sim_file_var.set(path)

    def select_real_file():
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            real_file_var.set(path)

    def predict():
        sim_path = sim_file_var.get()
        real_path = real_file_var.get()

        if not sim_path or not real_path:
            messagebox.showwarning("Thiếu file", "Vui lòng chọn cả hai file CSV.")
            return

        result = build_and_predict(sim_path, real_path)
        result_text.delete("1.0", tk.END)
        for line in result:
            result_text.insert(tk.END, line + "\n")

    # Cửa sổ chính
    root = tk.Tk()
    root.title("Dự đoán năng suất cây trồng")
    root.geometry("650x600")

    sim_file_var = tk.StringVar()
    real_file_var = tk.StringVar()

    tk.Label(root, text="Chọn file mô phỏng (.csv):").pack()
    tk.Entry(root, textvariable=sim_file_var, width=80).pack()
    tk.Button(root, text="Duyệt...", command=select_sim_file).pack(pady=5)

    tk.Label(root, text="Chọn file dữ liệu thực tế (.csv):").pack()
    tk.Entry(root, textvariable=real_file_var, width=80).pack()
    tk.Button(root, text="Duyệt...", command=select_real_file).pack(pady=5)

    tk.Button(root, text="Dự đoán", command=predict, bg='green', fg='white').pack(pady=10)

    result_text = tk.Text(root, height=30)
    result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    run_gui()
