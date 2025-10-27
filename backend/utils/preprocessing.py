from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

class ImagePreprocessor:
    @staticmethod
    def enhance_for_ocr(image):
        """Optimize image for OCR"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)
        
        # Increase brightness slightly
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.2)
        
        # Resize if too small or too large
        width, height = image.size
        if width < 500 or height < 500:
            scale = 500 / min(width, height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        elif width > 2000 or height > 2000:
            scale = 2000 / max(width, height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def apply_threshold(image, threshold=128):
        """Apply binary threshold"""
        img_array = np.array(image)
        binary = (img_array > threshold) * 255
        return Image.fromarray(binary.astype(np.uint8))
