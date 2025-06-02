import serial
import time
import unicodedata
import csv
import sys

# Đảm bảo in Unicode ra terminal không lỗi
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

# Cổng COM kết nối Arduino
ser = serial.Serial('COM5', 9600)
time.sleep(2)

# Tên file xuất
filename_all = 'du_lieu_day_du.csv'
filename_avg = 'du_lieu_trung_binh.csv'
filename_avg_structured = 'du_lieu_trung_binh_dang_bang.csv'

# Ghi tiêu đề cho cả 3 file
with open(filename_all, mode='w', newline='', encoding='utf-8') as f_all, \
     open(filename_avg, mode='w', newline='', encoding='utf-8') as f_avg, \
     open(filename_avg_structured, mode='w', newline='', encoding='utf-8') as f_struct:
    
    writer_all = csv.writer(f_all)
    writer_avg = csv.writer(f_avg)
    writer_struct = csv.writer(f_struct)

    writer_all.writerow(['Noi_Dung'])
    writer_avg.writerow(['Noi_Dung'])
    writer_struct.writerow([
        "Nhiet do TB (C)",
        "Do am TB (%)",
        "Anh sang TB (lx)",
        "Do am dat TB (%)",
        "Luu luong TB (L/phut)",
        "Nang suat thang (kg/ha)"
    ])

print("Dang doc du lieu tu Arduino...")

start_time = time.time()

# Các danh sách lưu dữ liệu
nhiet_do_list = []
do_am_list = []
anh_sang_list = []
do_am_dat_list = []
luu_luong_list = []

try:
    while time.time() - start_time < 30:
        if ser.in_waiting:
            line_bytes = ser.readline()
            try:
                line = line_bytes.decode('utf-8').strip()
            except UnicodeDecodeError:
                line = line_bytes.decode('latin1').strip()

            ascii_line = to_ascii(line)
            print("Du lieu nhan duoc :", ascii_line)

            # Ghi vào file đầy đủ
            with open(filename_all, mode='a', newline='', encoding='utf-8') as f_all:
                writer = csv.writer(f_all)
                writer.writerow([f'Du lieu nhan duoc : {ascii_line}'])

            # Phân tích dữ liệu
            if "Nhiet o" in ascii_line and "|" in ascii_line:
                try:
                    parts = ascii_line.split('|')
                    nhiet_do = float(parts[0].split(':')[1].replace('C', '').strip())
                    do_am = float(parts[1].split(':')[1].replace('%', '').strip())
                    anh_sang = float(parts[2].split(':')[1].replace('lx', '').strip())
                    do_am_dat = float(parts[3].split(':')[1].replace('%', '').strip())

                    nhiet_do_list.append(nhiet_do)
                    do_am_list.append(do_am)
                    anh_sang_list.append(anh_sang)
                    do_am_dat_list.append(do_am_dat)
                except Exception as e:
                    print("Khong the phan tich du lieu thoi tiet:", e)

            elif "Luu luong" in ascii_line:
                try:
                    value = float(ascii_line.split(':')[1].replace('L/phut', '').strip())
                    luu_luong_list.append(value)
                except Exception as e:
                    print("Khong the phan tich du lieu luu luong:", e)

    print("\nDa het 30 giay. Ket thuc doc du lieu.")
    ser.close()

    # Tính trung bình và ghi vào cả hai file
    if nhiet_do_list or luu_luong_list:
        avg_temp = round(sum(nhiet_do_list) / len(nhiet_do_list), 2) if nhiet_do_list else 0
        avg_hum = round(sum(do_am_list) / len(do_am_list), 2) if do_am_list else 0
        avg_light = round(sum(anh_sang_list) / len(anh_sang_list), 2) if anh_sang_list else 0
        avg_soil = round(sum(do_am_dat_list) / len(do_am_dat_list), 2) if do_am_dat_list else 0
        avg_flow = round(sum(luu_luong_list) / len(luu_luong_list), 2) if luu_luong_list else 0

        # Ghi dạng văn bản mô tả
        avg_line = (
            f'Du lieu nhan duoc : Trung binh -> '
            f'Nhiet do: {avg_temp} C | '
            f'Do am: {avg_hum} % | '
            f'Anh sang: {avg_light} lx | '
            f'Do am dat: {avg_soil} % | '
            f'Luu luong: {avg_flow} L/phut'
        )

        with open(filename_avg, mode='a', newline='', encoding='utf-8') as f_avg:
            writer = csv.writer(f_avg)
            writer.writerow([avg_line])

        # Ghi dạng bảng chuẩn để phần mềm học máy sử dụng
        with open(filename_avg_structured, mode='a', newline='', encoding='utf-8') as f_struct:
            writer = csv.writer(f_struct)
            writer.writerow([
                avg_temp,
                avg_hum,
                avg_light,
                avg_soil,
                avg_flow,
                0  # Giá trị năng suất giả lập, có thể sửa bằng tay sau
            ])

    else:
        print("Khong co du lieu hop le de tinh trung binh.")

except KeyboardInterrupt:
    print("Da ngat chuong trinh bang tay.")
    ser.close()
