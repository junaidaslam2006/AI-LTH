"""
Download EasyOCR models separately (run this once before starting the server)
This allows the download to complete without timeout issues.
"""
import easyocr

print("=" * 60)
print("Downloading EasyOCR Models (One-time setup)")
print("=" * 60)
print("This will download ~100MB of models for English OCR")
print("Please be patient, this may take 5-10 minutes...")
print("=" * 60)

try:
    print("\n🚀 Initializing EasyOCR Reader...")
    reader = easyocr.Reader(['en'], gpu=False, verbose=True)
    print("\n" + "=" * 60)
    print("✅ SUCCESS! EasyOCR models downloaded successfully!")
    print("=" * 60)
    print("You can now run: python app.py")
    print("Models are cached and will load instantly next time!")
    print("=" * 60)
except Exception as e:
    print(f"\n❌ Error downloading models: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Try again later if download servers are busy")
    print("3. Or use a VPN if download is blocked")
