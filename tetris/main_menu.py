import tkinter as tk
import subprocess
import sys

def start_game():
    root.destroy()
    subprocess.Popen([sys.executable, "game.py"])

root = tk.Tk()
root.title("テトリス - メインメニュー")
root.geometry("300x200")

label = tk.Label(root, text="テトリスへようこそ", font=("Helvetica", 16))
label.pack(pady=20)

start_button = tk.Button(root, text="ゲーム開始", font=("Helvetica", 14), command=start_game)
start_button.pack(pady=10)

quit_button = tk.Button(root, text="終了", font=("Helvetica", 14), command=root.quit)
quit_button.pack(pady=10)

root.mainloop()

