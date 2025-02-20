# TS To MP4 Video Converter (by Sahil Singh) - EXE Version

This project is a **multi-threaded video converter** built with Python, designed to convert `.ts` video files into mp4  formats using **FFmpeg**. The application supports logging of conversions in a **CSV file** and is designed to be packaged into a Windows executable (.exe) for ease of use.

## Features

✅ **Batch Processing** - Convert multiple `.ts` files in a single run.
✅ **Multi-threading** - Faster processing by running conversions in parallel.
✅ **Conversion Log** - Logs all conversions in a CSV file in the Input Folder for tracking.
✅ **Drag & Drop Support** - Easily add files to the queue.
✅ **Standalone EXE** - Runs on Windows without requiring Python installation.

---

## Requirements

- Windows OS (for running the `.exe` version)
- The `.exe` version handles dependencies internally

---

## Installation

If you are using the **EXE version**, simply download and run the executable. No additional setup is required.

If running from source, install the dependencies:

```sh
pip install pandas ffmpeg-python tkinter threading
```


---

## Usage

### **Running the EXE**

1. Double-click the `.exe` file.
2. Select the `.ts` files for conversion.
3. The converted files will be saved in the same directory as the originals.
4. Check the log file (`conversion_log.csv`) for details.

### **Log File Handling**

- **Log Format**: CSV file (`conversion_log.csv`)
- **Columns**:
  - `Original TS File`
  - `Converted File`
  - `Status`
- The log file is updated automatically after each conversion.

---

## Building the EXE (For Developers)

If you want to create the executable yourself, use **PyInstaller**:

```sh
pip install pyinstaller
pyinstaller --onefile --windowed TS2MP4Converter.py
```

This will generate a `dist/TS2MP4Converter.exe` file that you can distribute.

---

## Troubleshooting

### **FFmpeg Not Found**
- Ensure FFmpeg is installed and added to the directory.

### **Unnamed Columns in Log File**
- Ensure logs are saved with `index=False` in pandas.
- Delete any old log files that may contain an incorrect format.

### **Slow Conversion?**
- The tool uses multi-threading, but performance depends on system resources.

---

## License

This project is open-source. Feel free to modify and distribute it as needed.

---

### **Author**: Sahil Singh (@sahil_sinnh)

For questions or suggestions, feel free to reach out!

