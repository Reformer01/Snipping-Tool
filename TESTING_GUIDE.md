# Clippr - Testing Guide

## 🚀 Quick Start Testing

### Step 1: Install Dependencies

Open PowerShell or Command Prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- `customtkinter` - Modern UI framework
- `Pillow` - Image processing
- `pywin32` - Windows clipboard integration
- `pygetwindow` - Window capture
- `pytesseract` - OCR text extraction

**Note:** For OCR to work, you also need to install Tesseract OCR separately:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`

### Step 2: Run the Application

```bash
python modern_snipper.py
```

## ✅ Feature Testing Checklist

### 1. Main Window UI
- [ ] **Window appears** with "Clippr" title
- [ ] **Header** shows title and subtitle
- [ ] **Settings section** is organized in a frame
- [ ] **Feature status bar** at bottom shows available features (✓ Clipboard, ✓ Window Snip, ✓ OCR)
- [ ] Window stays on top of other windows

### 2. Snip Type Selection
- [ ] **Rectangular Snip** - Select from dropdown
- [ ] **Window Snip** - Select from dropdown (shows warning if pygetwindow not installed)
- [ ] **Fullscreen Snip** - Select from dropdown

### 3. Delay Timer
- [ ] **No Delay** - Snip happens immediately
- [ ] **3 Seconds** - Countdown window appears, snips after 3 seconds
- [ ] **5 Seconds** - Countdown window appears, snips after 5 seconds
- [ ] **10 Seconds** - Countdown window appears, snips after 10 seconds

### 4. Auto-Copy Feature
- [ ] **Checkbox** is checked by default
- [ ] When enabled, snip is automatically copied to clipboard
- [ ] Can paste snip into Paint, Word, etc. immediately after capture

### 5. Rectangular Snip
- [ ] Click "NEW SNIP" button
- [ ] Main window minimizes
- [ ] Full-screen overlay appears with screenshot
- [ ] **Click and drag** to select area
- [ ] Red selection rectangle appears
- [ ] Release mouse to capture
- [ ] Editor window opens with captured image

### 6. Window Snip
- [ ] Select "Window" from Snip Type dropdown
- [ ] Click "NEW SNIP"
- [ ] Window minimizes
- [ ] Active window is captured automatically
- [ ] Editor window opens

### 7. Fullscreen Snip
- [ ] Select "Fullscreen" from Snip Type dropdown
- [ ] Click "NEW SNIP"
- [ ] Entire screen is captured instantly
- [ ] Editor window opens

### 8. Editor Window - Drawing Tools

#### Pen Tool
- [ ] Click "✏️ Pen" button (highlights in red when selected)
- [ ] Click and drag on image to draw
- [ ] Drawing appears in selected color

#### Highlighter Tool
- [ ] Click "🖍️ Highlighter" button
- [ ] Click and drag on image
- [ ] Semi-transparent highlighting appears

#### Shape Tools
- [ ] **Arrow** - Click and drag to create arrow
- [ ] **Rectangle** - Click and drag to create rectangle
- [ ] **Circle** - Click and drag to create circle
- [ ] All shapes appear in selected color

#### Crop Tool
- [ ] Click "✂️ Crop" button
- [ ] Click and drag to select crop area
- [ ] Dashed rectangle appears
- [ ] Release to crop image
- [ ] Image is cropped and resized

### 9. Color Selection
- [ ] Click any color button in color palette
- [ ] Selected color shows border indicator
- [ ] Drawing/shapes use selected color
- [ ] Try all 7 colors: Red, Orange, Yellow, Teal, Dark Blue, Black, White

### 10. Editor Actions

#### Extract Text (OCR)
- [ ] Click "🔍 Extract Text (OCR)" button
- [ ] If Tesseract installed: Processing window appears, then text extraction window
- [ ] If not installed: Error message appears with installation instructions
- [ ] Extracted text is displayed in scrollable window
- [ ] Click "Copy Text to Clipboard" to copy text

#### Copy Image
- [ ] Click "📋 Copy Image" button
- [ ] Success message appears
- [ ] Image can be pasted into other applications

#### Save to File
- [ ] Click "💾 Save to File" button
- [ ] File dialog appears
- [ ] Choose location and filename
- [ ] Image saves as PNG or JPG
- [ ] Success message appears

#### Close
- [ ] Click "✖ Close" button
- [ ] Editor closes
- [ ] Main window reappears

### 11. Keyboard Shortcuts

#### Main Window
- [ ] **Enter** - Triggers "NEW SNIP" (quick capture)

#### Editor Window
- [ ] **Ctrl+S** - Save to file
- [ ] **Ctrl+C** - Copy image to clipboard
- [ ] **Escape** - Close editor

### 12. Status Bar (Editor)
- [ ] Status bar at bottom shows:
  - Current tool (Pen, Highlighter, etc.)
  - Selected color
  - Image dimensions (width x height)
- [ ] Updates when tool or color changes

### 13. Error Handling
- [ ] **Missing pywin32** - Clipboard features show error message
- [ ] **Missing pygetwindow** - Window Snip shows warning
- [ ] **Missing pytesseract** - OCR button is disabled with message
- [ ] **Missing Tesseract OCR** - OCR shows helpful error with download link

## 🐛 Common Issues & Solutions

### Issue: "pywin32 not installed"
**Solution:** Run `pip install pywin32`

### Issue: "Window Snip unavailable"
**Solution:** Run `pip install pygetwindow`

### Issue: "OCR unavailable" or "Tesseract not found"
**Solution:** 
1. Install pytesseract: `pip install pytesseract`
2. Download and install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
3. If still not working, set path manually in code:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### Issue: Application doesn't start
**Solution:** 
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip list`
- Check for error messages in terminal

### Issue: UI looks broken or old-style
**Solution:**
- Ensure customtkinter is latest version: `pip install --upgrade customtkinter`
- Check if you're running the latest code

## 📊 Test Scenarios

### Scenario 1: Quick Screenshot
1. Open Clippr
2. Press Enter (or click "NEW SNIP")
3. Select area with mouse
4. Image appears in editor
5. Press Ctrl+C to copy
6. Paste in Paint/Word - should work!

### Scenario 2: Capture Menu with Delay
1. Open a program with a menu (e.g., Notepad)
2. In Clippr, select "Window" snip type
3. Select "3 Seconds" delay
4. Click "NEW SNIP"
5. Quickly open the menu in Notepad
6. Countdown completes, menu is captured

### Scenario 3: Annotate Screenshot
1. Take a rectangular snip
2. In editor, select "Pen" tool
3. Draw annotations
4. Select "Arrow" tool
5. Add arrows pointing to important parts
6. Select "Rectangle" tool
7. Draw boxes around areas
8. Save the annotated image

### Scenario 4: Extract Text from Image
1. Take a snip of text (e.g., from a PDF, website, or document)
2. In editor, click "Extract Text (OCR)"
3. Wait for processing
4. Review extracted text
5. Copy text to clipboard
6. Paste in Notepad - text should be there!

## 🎯 Performance Testing

- [ ] **Fast capture** - Rectangular snip should be instant
- [ ] **Smooth drawing** - Pen tool should draw smoothly without lag
- [ ] **Large images** - Test with full-screen captures (should handle well)
- [ ] **Multiple snips** - Take several snips in a row (should work reliably)

## ✅ Final Checklist

Before considering testing complete:
- [ ] All snip types work
- [ ] All drawing tools work
- [ ] All shapes work
- [ ] Color selection works
- [ ] Crop works
- [ ] Copy to clipboard works
- [ ] Save to file works
- [ ] OCR works (if Tesseract installed)
- [ ] Keyboard shortcuts work
- [ ] Error messages are helpful
- [ ] UI looks modern and professional
- [ ] Status indicators are accurate

---

**Happy Testing! 🚀**

If you find any issues, note them down with:
- What you were doing
- What happened
- What you expected to happen
- Any error messages

