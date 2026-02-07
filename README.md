## 🏎️ F1 Telemetry Dashboard — Interactive Race Engineer Tool

An interactive **Formula 1 telemetry analysis dashboard** built with **FastF1** and **Dash** that lets you visualize, compare, and replay real F1 driver data like a race engineer.

This project turns raw telemetry into an immersive visual tool where you can **see how drivers take corners, compare racing lines, and watch throttle/brake behavior live on the track**.

---

### 🚀 What this project does

* 📍 Draws the **exact racing line** of any driver on any circuit
* 🟢 Animates a **moving car pointer** along the lap
* 🎮 Play / Pause controls + adjustable replay speed
* ⚡ Shows **live speed** next to the moving car
* 🟩 Live **Throttle** bar and 🟥 **Brake** bar synced with the pointer
* 🆚 Compare **two drivers** on the same session
* 📈 Speed trace comparison across the lap distance
* 📊 Automatic **Qualifying / Race results** table
* 🖼️ Driver photo displayed above each telemetry map
* 🌍 Supports most tracks from the F1 calendar
* 👥 Full driver grid support

---

### 🧠 Why this is cool

This isn’t just charts.

This replicates how real motorsport engineers analyze laps:

> Where did the driver brake?
> How much throttle was used exiting the corner?
> Who carried more speed through the apex?
> Which racing line is more efficient?

You **watch** the lap happen.

---

### 🛠️ Tech Stack

* Python
* Dash (interactive web UI)
* Plotly (animated telemetry visualization)
* FastF1 (official F1 telemetry data)

---

### 🎯 Key Features

| Feature                 | Description                             |
| ----------------------- | --------------------------------------- |
| Animated Track Map      | Car moves along the real racing line    |
| Live Telemetry Bars     | Throttle & Brake update in real time    |
| Dual Driver Comparison  | Side-by-side racing line analysis       |
| Speed Trace             | Compare speed across lap distance       |
| Results Table           | Session-aware quali/race classification |
| Adjustable Replay Speed | Slow motion to fast playback            |
| Driver Cards            | Photos + telemetry visualization        |
| Multi-Track Support     | Most F1 circuits supported              |

---

### 📸 What it looks like

A dashboard that feels like a mix of F1 TV analysis + engineering software.

---

### 🧩 Use Cases

* Motorsport data analysis
* Understanding racing lines and corner technique
* Comparing driver styles
* Learning how telemetry works
* Portfolio project for motorsport / data / CV roles

---

### ▶️ How to run

```bash
pip install fastf1 dash plotly pandas
python app.py
```

Open in browser → start analyzing laps.

---

### 💡 Future Improvements

* Sector timing overlays
* Corner detection & labeling
* Onboard video sync
* Tire & stint analysis
* Deploy as live web app

---

### 🙌 Inspiration

Built as a passion project to explore how **data science meets motorsport** and how raw telemetry can be turned into meaningful visual insights.

---

If you like motorsport, data, or visualization — this project is for you.
