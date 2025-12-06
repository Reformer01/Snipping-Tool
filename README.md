# Clippr - Professional Snipping Tool

A modern, feature-rich snipping tool built with Python that demonstrates clean architecture, modern UI design, deep OS integration, and AI-powered text extraction.

## 🎯 Portfolio Highlights

This project showcases critical software engineering principles:

### 1. Clean Architecture (OOP)
- **Object-Oriented Design**: The `SnippingTool` class inherits from `CTk` (CustomTkinter), encapsulating all state management (coordinates, image data) within the class instance
- **Separation of Concerns**: Each method has a single responsibility (snip capture, preview, clipboard operations, file saving, OCR)
- **Maintainability**: Well-structured code that's easy to extend and modify

### 2. Modern UI/UX
- **Dark Mode**: Native dark-mode aesthetic using CustomTkinter that feels like a built-in Windows 11 app
- **Professional Appearance**: Replaces outdated Tkinter look with modern, rounded, high-DPI aware components
- **User Experience**: Intuitive interface with visual feedback, status updates, and comprehensive editing tools

### 3. OS Integration & Advanced Features
- **Clipboard Integration**: Handles binary image data conversion using `BytesIO` and direct Windows API calls via `win32clipboard`
- **System-Level Operations**: Captures full-screen content, active windows, and custom regions
- **OCR Text Extraction**: AI-powered optical character recognition using Tesseract OCR
- **Comprehensive Editor**: Drawing tools, shapes, crop, and annotation capabilities

## 🛠️ Tech Stack

- **GUI**: `customtkinter` - Modern, dark-mode UI framework
- **Image Processing**: `Pillow` (PIL) - Screen capture and image manipulation
- **System Integration**: `pywin32` - Windows clipboard and system APIs
- **Window Capture**: `pygetwindow` - Active window detection and capture
- **OCR**: `pytesseract` - Text extraction from images using Google Tesseract

## 📦 Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install customtkinter Pillow pywin32 pygetwindow pytesseract
```

### 2. Install Tesseract OCR (Required for Text Extraction)

**Windows:**
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default location: `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to your system PATH, or manually set it in code:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Note:** The application will work without Tesseract, but OCR functionality will be disabled.

## 🚀 Usage

Run the application:
```bash
python modern_snipper.py
```

### Core Features:

1. **Snip Types:**
   - **Rectangular**: Click and drag to select any area
   - **Window**: Automatically captures the active window
   - **Fullscreen**: Instantly captures entire screen

2. **Delay Timer:**
   - No Delay, 3s, 5s, or 10s countdown
   - Perfect for capturing pop-up menus and tooltips

3. **Auto-Copy:**
   - Automatically copies snips to clipboard (enabled by default)

### Editor Features:

1. **Drawing Tools:**
   - **Pen**: Draw with customizable colors and line width
   - **Highlighter**: Semi-transparent highlighting

2. **Shapes:**
   - Arrows for pointing out details
   - Rectangles and circles for emphasis
   - All shapes support custom colors

3. **Image Tools:**
   - **Crop**: Resize/crop after capture
   - **Extract Text (OCR)**: Extract text from images using AI
   - **Copy**: Copy edited image to clipboard
   - **Save**: Save as PNG or JPG with timestamp

## 📝 Key Technical Challenges Solved

### Clipboard Integration
Python doesn't handle binary image data on the clipboard natively. The solution involves:
1. Converting PIL Image to BMP format using `BytesIO`
2. Removing the BMP header (14 bytes) to get the DIB (Device-Independent Bitmap) data
3. Using `win32clipboard` to interface directly with Windows API
4. Properly managing clipboard state (open, empty, set, close)

### Screen Capture & Overlay
- Full-screen screenshot capture using `ImageGrab.grab()`
- Active window detection using `pygetwindow`
- Transparent overlay window for selection
- Real-time rectangle drawing with mouse drag events
- Coordinate normalization to handle any drag direction

### OCR Text Extraction
- Integration with Google Tesseract OCR engine via `pytesseract`
- Image preprocessing for optimal OCR accuracy
- User-friendly text display with copy functionality
- Graceful error handling when Tesseract is not installed

### Image Display & Editing
- Converting PIL Images to CustomTkinter-compatible format
- Responsive preview window sizing
- Real-time drawing on canvas with coordinate scaling
- Memory management to prevent garbage collection issues
- Multi-layer drawing system (shapes, annotations, crop)

## 🎨 Customization

### Adding an Icon
To add a custom icon, place a `scissors.ico` file in the project directory and add this line in `__init__`:
```python
self.iconbitmap("scissors.ico")
```

### Building an Executable
For portfolio distribution, create a standalone `.exe`:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=scissors.ico modern_snipper.py
```

This creates a portable application that runs without a terminal window.

**Note:** For OCR functionality in the executable, you may need to bundle Tesseract OCR or provide installation instructions.

## 📊 Architecture Discussion Points

When presenting this in interviews or portfolios, emphasize:

1. **Design Patterns**: Class-based architecture with clear method responsibilities
2. **Error Handling**: Comprehensive try-except blocks with user-friendly error messages
3. **User Experience**: Status updates, visual feedback, and intuitive workflow
4. **Platform-Specific Code**: Windows API integration while maintaining clean separation
5. **AI Integration**: OCR text extraction demonstrates integration with external AI engines
6. **Modular Design**: Optional dependencies (pygetwindow, pytesseract) with graceful degradation

## ✨ Feature Highlights

### Essential Features
- ✅ Rectangular Snip
- ✅ Window Snip
- ✅ Fullscreen Snip
- ✅ Clipboard Auto-Copy
- ✅ File Save (PNG/JPG)

### Editor Features (Pro Layer)
- ✅ Pen & Highlighter Tools
- ✅ Shapes (Arrows, Rectangles, Circles)
- ✅ Crop Tool
- ✅ Delay Timer (3s, 5s, 10s)

### Portfolio Star Features (AI & Advanced)
- ✅ **OCR Text Extraction** - Extract and copy text from any image
- 🔄 Redaction (future enhancement)
- 🔄 Screen Recording (future enhancement)

## 🐛 Known Limitations

- Windows-only (due to `pywin32` dependency for clipboard)
- OCR requires separate Tesseract installation
- Single monitor support (can be extended for multi-monitor setups)

## 📄 License

This project is for portfolio and personal use.

---

**Built with attention to detail for portfolio presentation** 🚀

**Clippr** - Your modern snipping companion
