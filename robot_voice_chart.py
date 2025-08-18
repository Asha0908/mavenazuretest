#!/usr/bin/env python3
"""
📞 Robot Voice-Only Chart Creator (Tkinter)
- Beautiful UI with an animated robot avatar that "speaks"
- Auto-greets and starts listening (no clicks)
- Asks for dataset (built-in + CSV in ./datasets)
- Renders a default business chart
- Guides full voice customization by voice: type, X, Y, color
- Advanced charts beyond Excel: violin, box, heatmap, area, donut, radar, waterfall

Dependencies:
  pip install matplotlib pandas numpy speechrecognition pyttsx3 pyaudio pillow
System (Linux) tips:
  sudo apt-get install portaudio19-dev espeak-ng
"""

import os
import io
import time
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import difflib
import speech_recognition as sr
import pyttsx3

# --------------------- Utility helpers ---------------------

def ensure_dir(path: str):
	if not os.path.exists(path):
		os.makedirs(path)

def list_csv_datasets(dir_path: str):
	if not os.path.isdir(dir_path):
		return []
	return [f for f in os.listdir(dir_path) if f.lower().endswith(".csv")]

def pick_best_match(spoken: str, choices: list[str], cutoff: float = 0.6):
	if not choices:
		return None
	matches = difflib.get_close_matches(spoken.lower(), [c.lower() for c in choices], n=1, cutoff=cutoff)
	if not matches:
		return None
	for c in choices:
		if c.lower() == matches[0]:
			return c
	return None

def is_datetime_like(series: pd.Series) -> bool:
	try:
		pd.to_datetime(series.dropna().astype(str), errors="raise")
		return True
	except Exception:
		return False

def first_categorical(df: pd.DataFrame):
	for col in df.columns:
		if df[col].dtype == object or df[col].dtype.name.startswith("category"):
			return col
	for col in df.columns:
		if not pd.api.types.is_numeric_dtype(df[col]):
			return col
	return None

def first_numeric(df: pd.DataFrame):
	for col in df.columns:
		if pd.api.types.is_numeric_dtype(df[col]):
			return col
	return None

def hex_colors(n: int):
	palette = ["#3498db","#e74c3c","#2ecc71","#f39c12","#9b59b6","#1abc9c","#e67e22","#34495e",
			   "#8e44ad","#16a085","#d35400","#2c3e50","#27ae60","#2980b9","#c0392b","#f1c40f"]
	out = []
	i = 0
	while len(out) < n:
		out.append(palette[i % len(palette)])
		i += 1
	return out

# --------------------- Robot avatar ---------------------

class RobotAvatar:
	def __init__(self, parent: tk.Frame):
		self.canvas = tk.Canvas(parent, width=360, height=360, bg="#0b111b", highlightthickness=0)
		self.canvas.pack(padx=16, pady=16)
		self.is_listening = False
		self.is_speaking = False
		self.mouth_open = False
		self._draw_robot()
		self._animate_loop()

	def _draw_robot(self):
		c = self.canvas
		c.delete("all")
		# Head
		c.create_oval(40, 40, 320, 320, fill="#121927", outline="#1f2a3a", width=3)
		# Antenna
		c.create_line(180, 18, 180, 42, fill="#00d4ff", width=4)
		c.create_oval(172, 8, 188, 24, fill="#ff5c8a", outline="")
		# Eyes
		self.left_eye = c.create_oval(100, 120, 150, 170, fill="#0b111b", outline="#00d4ff", width=3)
		self.right_eye = c.create_oval(210, 120, 260, 170, fill="#0b111b", outline="#00d4ff", width=3)
		# Pupils
		self.left_pupil = c.create_oval(118, 138, 132, 152, fill="#00d4ff", outline="")
		self.right_pupil = c.create_oval(228, 138, 242, 152, fill="#00d4ff", outline="")
		# Mouth (rectangle, animated height while speaking)
		self.mouth = c.create_rectangle(120, 220, 240, 245, fill="#00ff88", outline="")
		# LED ring (listening pulse)
		self.pulse = c.create_oval(46, 46, 314, 314, outline="#00d4ff", width=2)

	def set_listening(self, value: bool):
		self.is_listening = value

	def start_speaking(self):
		self.is_speaking = True

	def stop_speaking(self):
		self.is_speaking = False
		# Close mouth
		self.canvas.coords(self.mouth, 120, 230, 240, 238)

	def _animate_loop(self):
		# Eyes glow when listening
		eye_color = "#00d4ff" if self.is_listening else "#35516e"
		self.canvas.itemconfig(self.left_eye, outline=eye_color)
		self.canvas.itemconfig(self.right_eye, outline=eye_color)
		self.canvas.itemconfig(self.left_pupil, fill=eye_color)
		self.canvas.itemconfig(self.right_pupil, fill=eye_color)

		# Pulse ring when listening
		if self.is_listening:
			w = time.time() % 1.0
			t = 46 + int(4 * np.sin(w * 2 * np.pi))
			# Animate the outer ring by slightly expanding/contracting
			self.canvas.coords(self.pulse, t, t, 360 - t, 360 - t)
		else:
			self.canvas.coords(self.pulse, 46, 46, 314, 314)

		# Mouth movement when speaking
		if self.is_speaking:
			# toggle height
			coords = self.canvas.coords(self.mouth)
			y1 = 220
			y2 = coords[3]
			new_h = 220 if y2 > 250 else y2 + 8
			self.canvas.coords(self.mouth, 120, y1, 240, new_h)

		self.canvas.after(70, self._animate_loop)

# --------------------- Main App ---------------------

class RobotVoiceChartApp:
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("📞 Robot Voice Chart Creator")
		self.root.geometry("1280x840")
		self.root.configure(bg="#0f1420")

		# Voice
		self.recognizer = sr.Recognizer()
		self.microphone = None
		try:
			self.microphone = sr.Microphone()
		except Exception as e:
			print("Microphone error:", e)
		self.tts = pyttsx3.init()
		self.tts.setProperty("rate", 175)
		self.tts.setProperty("volume", 1.0)

		# Data state
		self.current_df: pd.DataFrame | None = None
		self.current_name: str | None = None
		self.awaiting = "dataset"
		self.custom_config = {"type": None, "x": None, "y": None, "color": None}
		self.supported_chart_types = [
			"bar","line","scatter","pie","histogram","box","violin","heatmap","area","donut","radar","waterfall"
		]

		self.sample_datasets = {
			"sales": pd.DataFrame({
				"Month": ["Jan","Feb","Mar","Apr","May","Jun"],
				"Revenue": [2000, 2300, 2100, 2600, 2800, 3000],
				"Region": ["North","North","South","South","East","West"]
			}),
			"weather": pd.DataFrame({
				"Date": pd.date_range("2024-01-01", periods=10, freq="D"),
				"Temperature": [25,27,26,28,30,29,31,32,28,26],
				"Humidity": [60,58,62,55,53,57,50,48,52,59],
				"City": ["Mumbai","Mumbai","Delhi","Delhi","Chennai","Chennai","Delhi","Mumbai","Chennai","Delhi"]
			}),
			"students": pd.DataFrame({
				"Student": ["Alice","Bob","Charlie","Diana","Eve","Frank"],
				"Math": [85,78,92,75,88,82],
				"Science": [90,85,88,80,92,78],
				"English": [88,92,85,78,90,85],
				"Grade": ["A","B","A","C","A","B"]
			})
		}

		ensure_dir("datasets")
		self.external_csvs = list_csv_datasets("datasets")

		self._build_ui()
		self.root.after(500, self._intro_and_start)

	def _build_ui(self):
		header = tk.Frame(self.root, bg="#0f1420")
		header.pack(fill="x", padx=18, pady=(16, 8))
		# Configure ttk styles (optional)
		style = ttk.Style()
		style.configure("TButton", font=("Arial", 11))
		style.configure("TLabel", background="#0f1420", foreground="#b7c0cd")
		title = tk.Label(header, text="📞 Robot Voice Chart Creator", font=("Arial", 26, "bold"), fg="#00d4ff", bg="#0f1420")
		title.pack()
		sub = tk.Label(header, text="Hands-free. I'm already listening.", font=("Arial", 12), fg="#b7c0cd", bg="#0f1420")
		sub.pack(pady=(6, 0))

		content = tk.Frame(self.root, bg="#0f1420")
		content.pack(fill="both", expand=True, padx=18, pady=12)

		left = tk.Frame(content, bg="#121927", width=380)
		left.pack(side="left", fill="y")
		left.pack_propagate(False)

		self.avatar = RobotAvatar(left)
		lbl = tk.Label(left, text="I'm your chart assistant.", font=("Arial", 12), fg="#b7c0cd", bg="#121927")
		lbl.pack()

		self.conv = tk.Text(left, height=14, width=44, bg="#0b111b", fg="#e9eef7", font=("Consolas", 11), wrap="word", borderwidth=0)
		self.conv.pack(padx=16, pady=12, fill="both", expand=True)
		self.conv.config(state="disabled")

		right = tk.Frame(content, bg="#121927")
		right.pack(side="right", fill="both", expand=True)
		cap = tk.Label(right, text="📊 Chart", font=("Arial", 15, "bold"), fg="#00d4ff", bg="#121927")
		cap.pack(pady=(16, 8))
		self.chart_area = tk.Label(right, bg="#0b111b")
		self.chart_area.pack(padx=16, pady=12, fill="both", expand=True)

		self.status = tk.Label(self.root, text="Initializing...", font=("Arial", 11), fg="#9fb3c8", bg="#0f1420")
		self.status.pack(pady=(0, 10))

	def _set_chart_image(self, fig: plt.Figure):
		buf = io.BytesIO()
		fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
		buf.seek(0)
		img = Image.open(buf)
		imgTk = ImageTk.PhotoImage(img)
		self.chart_area.configure(image=imgTk)
		self.chart_area.image = imgTk
		plt.close(fig)

	def say(self, text: str):
		self._add_conv("Robot", text)
		def _speak():
			try:
				self.tts.stop()
			except Exception:
				pass
			self.avatar.start_speaking()
			self.tts.setProperty("volume", 1.0)
			self.tts.say(text)
			self.tts.runAndWait()
			self.avatar.stop_speaking()
		threading.Thread(target=_speak, daemon=True).start()

	def _add_conv(self, who: str, msg: str):
		self.conv.config(state="normal")
		ts = time.strftime("%H:%M:%S")
		self.conv.insert("end", f"[{ts}] {who}: {msg}\n\n")
		self.conv.config(state="disabled")
		self.conv.see("end")

	def _intro_and_start(self):
		samples = ", ".join(self.sample_datasets.keys())
		files = [os.path.splitext(f)[0] for f in self.external_csvs]
		self.say("Hello! I am your robot chart assistant.")
		if samples:
			self.say(f"You can say dataset names like: {samples}.")
		if files:
			self.say(f"I also found CSV files in your datasets folder: {', '.join(files)}.")
		self.say("Which dataset would you like to use?")
		self.status.config(text="Listening for dataset...")
		if self.microphone is not None:
			threading.Thread(target=self._listen_loop, daemon=True).start()
		else:
			self._add_conv("Robot", "Microphone not available. Please connect one and restart.")

	def _listen_loop(self):
		with self.microphone as source:
			self.recognizer.dynamic_energy_threshold = True
			self.recognizer.adjust_for_ambient_noise(source, duration=0.4)

		while True:
			try:
				with self.microphone as source:
					self.avatar.set_listening(True)
					audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
					self.avatar.set_listening(False)
				txt = self.recognizer.recognize_google(audio)
				spoken = txt.strip()
				self._add_conv("You", spoken)
				self._handle_spoken(spoken)
			except sr.WaitTimeoutError:
				self.avatar.set_listening(False)
				continue
			except sr.UnknownValueError:
				if self.awaiting in ("dataset","confirm_default","custom_decision"):
					self.say("Sorry, I didn't catch that. Please repeat.")
				continue
			except Exception:
				self.avatar.set_listening(False)
				continue

	def _handle_spoken(self, spoken: str):
		s = spoken.lower()
		if any(k in s for k in ["stop","end call","hang up","goodbye"]):
			self.say("Okay, ending our call. Thanks for using the assistant!")
			self.status.config(text="Call ended. Close the window to exit.")
			return

		if self.awaiting == "dataset":
			self._handle_dataset_choice(s)
			return

		if self.awaiting == "confirm_default":
			if any(k in s for k in ["yes","yeah","yep","ok","okay","sure"]):
				self._render_default_chart()
				self.awaiting = "custom_decision"
				self.say("Would you like a customized chart with specific chart type, X and Y columns, or colors?")
				self.status.config(text="Asking for customization...")
			elif any(k in s for k in ["no","nope","skip"]):
				self.awaiting = "custom_decision"
				self.say("Okay. Would you like a customized chart?")
			else:
				self.say("Please say yes or no. Should I show the default chart first?")
			return

		if self.awaiting == "custom_decision":
			if any(k in s for k in ["no","not","later","skip"]):
				self.say("Alright. Say 'customize chart' anytime to refine.")
			elif "custom" in s or "yes" in s:
				self.awaiting = "ask_type"
				self.say(f"I support many chart types: {', '.join(self.supported_chart_types)}. Which chart type?")
				self.status.config(text="Waiting for chart type...")
			elif "default" in s:
				self._render_default_chart()
			else:
				self.say("Say 'yes' to customize, or 'no' to keep the default.")
			return

		if self.awaiting == "ask_type":
			chart = pick_best_match(s, self.supported_chart_types)
			if not chart:
				self.say(f"Please choose one of: {', '.join(self.supported_chart_types)}.")
				return
			self.custom_config["type"] = chart
			self.awaiting = "ask_x"
			self.say("Which column for X axis?")
			self.status.config(text="Waiting for X column...")
			return

		if self.awaiting == "ask_x" and self.current_df is not None:
			col = pick_best_match(s, list(self.current_df.columns))
			if not col:
				self.say(f"I couldn't find that column. Available: {', '.join(self.current_df.columns)}. Which for X?")
				return
			self.custom_config["x"] = col
			self.awaiting = "ask_y"
			self.say("Which column for Y axis?")
			self.status.config(text="Waiting for Y column...")
			return

		if self.awaiting == "ask_y" and self.current_df is not None:
			col = pick_best_match(s, list(self.current_df.columns))
			if not col:
				self.say(f"I couldn't find that column. Available: {', '.join(self.current_df.columns)}. Which for Y?")
				return
			self.custom_config["y"] = col
			self.awaiting = "ask_color"
			self.say("Optional: Which column should control colors? You can say 'no color'.")
			self.status.config(text="Waiting for color column...")
			return

		if self.awaiting == "ask_color" and self.current_df is not None:
			col = None
			if "no" not in s:
				col = pick_best_match(s, list(self.current_df.columns))
				if not col and "no" not in s:
					self.say("I didn't match that to a column. I'll proceed without colors.")
			self.custom_config["color"] = col
			self._render_custom_chart()
			self.awaiting = "custom_decision"
			self.say("Chart ready. Would you like to customize again or change dataset?")
			self.status.config(text="Ready for next instruction.")
			return

		# Global intents
		if "customize" in s and self.current_df is not None:
			self.awaiting = "ask_type"
			self.say(f"Which chart type? Options: {', '.join(self.supported_chart_types)}")
			return

		if any(k in s for k in ["change dataset","switch dataset","new dataset"]):
			self.awaiting = "dataset"
			self.say("Sure. Which dataset would you like to use?")
			return

		if self.current_df is not None:
			self.say("You can say 'customize chart', 'change dataset', or a specific chart type like 'violin' or 'heatmap'.")

	def _handle_dataset_choice(self, s: str):
		all_names = list(self.sample_datasets.keys()) + [os.path.splitext(f)[0] for f in self.external_csvs]
		chosen = pick_best_match(s, all_names)
		if not chosen:
			self.say(f"I couldn't find that dataset. Try one of: {', '.join(all_names)}.")
			return
		if chosen in self.sample_datasets:
			self.current_df = self.sample_datasets[chosen].copy()
			self.current_name = chosen
		else:
			path = os.path.join("datasets", f"{chosen}.csv")
			try:
				self.current_df = pd.read_csv(path)
				self.current_name = chosen
			except Exception:
				self.say("I couldn't read that CSV. Please check the file.")
				return
		for col in self.current_df.columns:
			if self.current_df[col].dtype == object:
				try_num = pd.to_numeric(self.current_df[col], errors="ignore")
				self.current_df[col] = try_num
		self.say(f"Loaded {self.current_name}. Columns are: {', '.join(self.current_df.columns)}.")
		self.awaiting = "confirm_default"
		self.say("Shall I show a default chart commonly used in companies?")
		self.status.config(text="Awaiting default chart confirmation...")

	def _render_default_chart(self):
		df = self.current_df
		fig = plt.figure(figsize=(9.5, 5.8), facecolor="#0b111b")
		ax = fig.add_subplot(111, facecolor="#0b111b")
		time_col = None
		for c in df.columns:
			if is_datetime_like(df[c]):
				time_col = c
				break
		num_col = first_numeric(df)
		cat_col = first_categorical(df)
		if time_col and num_col:
			x_values = pd.to_datetime(df[time_col])
			ax.plot(x_values, df[num_col], color="#00d4ff", linewidth=3, marker="o", markerfacecolor="#00ff88")
			ax.set_title(f"{self.current_name.title()}: {num_col} over {time_col}", color="#00d4ff", fontsize=18, pad=14)
			ax.set_xlabel(time_col, color="#d7dee9"); ax.set_ylabel(num_col, color="#d7dee9")
		elif cat_col and num_col:
			grouped = df.groupby(cat_col, dropna=False)[num_col].sum().sort_values(ascending=False).head(10)
			colors = hex_colors(len(grouped))
			ax.bar(grouped.index.astype(str), grouped.values, color=colors, edgecolor="white", linewidth=1.5)
			ax.set_title(f"{self.current_name.title()}: {num_col} by {cat_col}", color="#00d4ff", fontsize=18, pad=14)
			ax.set_xlabel(cat_col, color="#d7dee9"); ax.set_ylabel(num_col, color="#d7dee9")
			ax.tick_params(axis="x", rotation=30, colors="#d7dee9")
		else:
			col = num_col if num_col else df.columns[0]
			ax.hist(df[col].dropna(), bins=10, color="#3498db", edgecolor="white")
			ax.set_title(f"{self.current_name.title()}: Distribution of {col}", color="#00d4ff", fontsize=18, pad=14)
			ax.set_xlabel(col, color="#d7dee9"); ax.set_ylabel("Count", color="#d7dee9")
		for spine in ax.spines.values():
			spine.set_color("#1f2a3a")
		ax.grid(True, alpha=0.18, linestyle="--", color="#1f2a3a")
		ax.tick_params(colors="#d7dee9")
		self._set_chart_image(fig)
		self.say("Showing the default business chart now.")

	def _render_custom_chart(self):
		df = self.current_df
		chart_type = self.custom_config["type"]
		x = self.custom_config["x"]
		y = self.custom_config["y"]
		color = self.custom_config["color"]
		fig = plt.figure(figsize=(9.5, 5.8), facecolor="#0b111b")
		ax = fig.add_subplot(111, facecolor="#0b111b")
		def style_axes(title: str, xlabel: str | None, ylabel: str | None):
			ax.set_title(title, color="#00d4ff", fontsize=18, pad=14)
			if xlabel: ax.set_xlabel(xlabel, color="#d7dee9")
			if ylabel: ax.set_ylabel(ylabel, color="#d7dee9")
			for spine in ax.spines.values():
				spine.set_color("#1f2a3a")
			ax.grid(True, alpha=0.18, linestyle="--", color="#1f2a3a")
			ax.tick_params(colors="#d7dee9")
		if chart_type in ("bar","line","scatter","area","histogram","pie","donut"):
			if chart_type == "histogram":
				ax.hist(df[x].dropna(), bins=20, color="#3498db", edgecolor="white")
				style_axes(f"Histogram of {x}", x, "Count")
			elif chart_type == "pie":
				group = df[x].value_counts(dropna=False)
				colors = hex_colors(len(group))
				ax.pie(group.values, labels=group.index.astype(str), colors=colors, autopct="%1.1f%%",
						wedgeprops={'edgecolor':'white','linewidth':1.5}, startangle=90)
				style_axes(f"Pie: {x}", None, None)
			elif chart_type == "donut":
				group = df[x].value_counts(dropna=False)
				colors = hex_colors(len(group))
				ax.pie(group.values, labels=group.index.astype(str), colors=colors, autopct="%1.1f%%",
						wedgeprops={'edgecolor':'white','linewidth':1.5}, startangle=90)
				centre = plt.Circle((0,0),0.55,fc="#0b111b")
				fig.gca().add_artist(centre)
				style_axes(f"Donut: {x}", None, None)
			else:
				if color and color in df.columns:
					groups = df.groupby(color, dropna=False)
					for idx, (name, sub) in enumerate(groups):
						c = hex_colors(100)[idx]
						if chart_type == "bar":
							agg = sub.groupby(x, dropna=False)[y].sum()
							ax.bar(agg.index.astype(str), agg.values, alpha=0.85, label=str(name), color=c, edgecolor="white")
						elif chart_type == "line":
							ax.plot(sub[x], sub[y], label=str(name), color=c, linewidth=2.5, marker="o")
						elif chart_type == "area":
							sub_sorted = sub.sort_values(by=x)
							ax.fill_between(sub_sorted[x].astype(float), sub_sorted[y], alpha=0.35, color=c, label=str(name))
							ax.plot(sub_sorted[x], sub_sorted[y], color=c, linewidth=1.6)
						elif chart_type == "scatter":
							ax.scatter(sub[x], sub[y], label=str(name), color=c, s=55, edgecolor="white", linewidth=0.6)
					ax.legend(facecolor="#0b111b", edgecolor="#1f2a3a", labelcolor="#d7dee9")
				else:
					c = "#00d4ff"
					if chart_type == "bar":
						agg = df.groupby(x, dropna=False)[y].sum()
						ax.bar(agg.index.astype(str), agg.values, color=c, edgecolor="white")
					elif chart_type == "line":
						ax.plot(df[x], df[y], color=c, linewidth=3, marker="o", markerfacecolor="#00ff88")
					elif chart_type == "area":
						sorted_df = df.sort_values(by=x)
						ax.fill_between(sorted_df[x].astype(float), sorted_df[y], alpha=0.35, color=c)
						ax.plot(sorted_df[x], sorted_df[y], color=c, linewidth=2)
					elif chart_type == "scatter":
						ax.scatter(df[x], df[y], color=c, s=60, edgecolor="white", linewidth=0.6)
				style_axes(f"{chart_type.title()} of {y} by {x}", x, y)
		elif chart_type == "box":
			cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
			if not cols:
				self.say("Box plot needs numeric columns."); plt.close(fig); return
			ax.boxplot([df[c].dropna() for c in cols], labels=cols, patch_artist=True,
						boxprops=dict(facecolor="#3498db", color="white"), medianprops=dict(color="white"))
			style_axes("Box Plot (multiple metrics)", "Metrics", "Values")
		elif chart_type == "violin":
			cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
			if not cols:
				self.say("Violin plot needs numeric columns."); plt.close(fig); return
			parts = ax.violinplot([df[c].dropna() for c in cols], showmedians=True)
			for pc in parts['bodies']:
				pc.set_facecolor("#8e44ad"); pc.set_edgecolor("white"); pc.set_alpha(0.7)
			style_axes("Violin Plot (distribution)", "Metrics (index)", "Values")
			ax.set_xticks(range(1, len(cols)+1)); ax.set_xticklabels(cols, rotation=25, color="#d7dee9")
		elif chart_type == "heatmap":
			nums = df.select_dtypes(include=[np.number])
			if nums.shape[1] < 2:
				self.say("Heatmap needs at least two numeric columns."); plt.close(fig); return
			corr = nums.corr()
			im = ax.imshow(corr, cmap="coolwarm")
			plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
			ax.set_xticks(range(len(corr.columns))); ax.set_yticks(range(len(corr.columns)))
			ax.set_xticklabels(corr.columns, rotation=30, color="#d7dee9")
			ax.set_yticklabels(corr.columns, color="#d7dee9")
			style_axes("Correlation Heatmap", None, None)
		elif chart_type == "radar":
			nums = df.select_dtypes(include=[np.number])
			if nums.shape[1] < 3:
				self.say("Radar needs at least three numeric columns."); plt.close(fig); return
			cols = nums.columns.tolist(); values = nums.mean().values
			N = len(cols)
			angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
			values = np.concatenate((values, [values[0]])); angles += angles[:1]
			ax = fig.add_subplot(111, polar=True, facecolor="#0b111b")
			ax.plot(angles, values, color="#00d4ff", linewidth=2); ax.fill(angles, values, color="#00d4ff", alpha=0.25)
			ax.set_thetagrids(np.degrees(angles[:-1]), cols); ax.tick_params(colors="#d7dee9"); ax.grid(color="#1f2a3a")
			ax.set_title("Radar (mean across metrics)", color="#00d4ff", fontsize=18, pad=14)
		elif chart_type == "waterfall":
			if x is None or y is None or not pd.api.types.is_numeric_dtype(df[y]):
				self.say("Waterfall needs an X category and numeric Y."); plt.close(fig); return
			series = df.groupby(x, dropna=False)[y].sum().sort_values(ascending=False)
			running = series.cumsum()
			colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in series.values]
			ax.bar(series.index.astype(str), series.values, color=colors, edgecolor="white")
			ax.plot(series.index.astype(str), running.values, color="#00d4ff", linewidth=2, marker="o")
			style_axes("Waterfall (cumulative)", x, y)
			plt.xticks(rotation=25, color="#d7dee9")
		else:
			self.say("That chart type is not implemented."); plt.close(fig); return
		self._set_chart_image(fig)
		self.say(f"Your {chart_type} chart is ready.")

	def run(self):
		self.root.mainloop()

# --------------------- Entrypoint ---------------------

def main():
	try:
		app = RobotVoiceChartApp()
		app.run()
	except Exception as e:
		print(f"Startup error: {e}")
		print("Install requirements: pip install matplotlib pandas numpy speechrecognition pyttsx3 pyaudio pillow")
		print("On Linux: sudo apt-get install portaudio19-dev espeak-ng")

if __name__ == "__main__":
	main()