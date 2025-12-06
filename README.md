# PySnip Pro - Portfolio-Ready Snipping Tool

A modern, professional snipping tool built with Python that demonstrates clean architecture, modern UI design, and deep OS integration.

## 🎯 Portfolio Highlights

This project showcases three critical software engineering principles:

### 1. Clean Architecture (OOP)
- **Object-Oriented Design**: The `SnippingTool` class inherits from `CTk` (CustomTkinter), encapsulating all state management (coordinates, image data) within the class instance
- **Separation of Concerns**: Each method has a single responsibility (snip capture, preview, clipboard operations, file saving)
- **Maintainability**: Well-structured code that's easy to extend and modify

### 2. Modern UI/UX
- **Dark Mode**: Native dark-mode aesthetic using CustomTkinter that feels like a built-in Windows 11 app
- **Professional Appearance**: Replaces outdated Tkinter look with modern, rounded, high-DPI aware components
- **User Experience**: Intuitive interface with visual feedback and status updates

### 3. OS Integration
- **Clipboard Integration**: Most challenging aspect - handles binary image data conversion using `BytesIO` and direct Windows API calls via `win32clipboard`
- **System-Level Operations**: Captures full-screen content and provides seamless copy-to-clipboard functionality
- **File Management**: Integrated save functionality with intelligent filename generation

## 🛠️ Tech Stack

- **GUI**: `customtkinter` - Modern, dark-mode UI framework
- **Image Processing**: `Pillow` (PIL) - Screen capture and image manipulation
- **System Integration**: `pywin32` - Windows clipboard and system APIs

## 📦 Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or manually:
   ```bash
   pip install customtkinter Pillow pywin32
   ```

## 🚀 Usage

Run the application:
```bash
python modern_snipper.py
```

### Features:
1. **Create Snip**: Click "NEW SNIP" button
2. **Select Area**: Click and drag to select the area you want to capture
3. **Preview**: View your snip in a preview window
4. **Copy to Clipboard**: One-click copy for immediate paste into other applications
5. **Save to File**: Save as PNG or JPG with auto-generated timestamp filename

## 📝 Key Technical Challenges Solved

### Clipboard Integration
Python doesn't handle binary image data on the clipboard natively. The solution involves:
1. Converting PIL Image to BMP format using `BytesIO`
2. Removing the BMP header (14 bytes) to get the DIB (Device-Independent Bitmap) data
3. Using `win32clipboard` to interface directly with Windows API
4. Properly managing clipboard state (open, empty, set, close)

### Screen Capture & Overlay
- Full-screen screenshot capture using `ImageGrab.grab()`
- Transparent overlay window for selection
- Real-time rectangle drawing with mouse drag events
- Coordinate normalization to handle any drag direction

### Image Display in Modern UI
- Converting PIL Images to CustomTkinter-compatible format
- Responsive preview window sizing
- Scrollable frame for large images
- Memory management to prevent garbage collection issues

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

## 📊 Architecture Discussion Points

When presenting this in interviews or portfolios, emphasize:

1. **Design Patterns**: Class-based architecture with clear method responsibilities
2. **Error Handling**: Coordinate validation to prevent accidental tiny captures
3. **User Experience**: Status updates, visual feedback, and intuitive workflow
4. **Platform-Specific Code**: Windows API integration while maintaining cross-platform core structure

## 🐛 Known Limitations

- Windows-only (due to `pywin32` dependency for clipboard)
- Single monitor support (can be extended for multi-monitor setups)
- No annotation tools (potential future enhancement)

## 📄 License

This project is for portfolio and personal use.

---

**Built with attention to detail for portfolio presentation** 🚀


