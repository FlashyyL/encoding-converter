"""
File Encoding Detection and Conversion Core Module
"""

import os
import chardet
import codecs
import shutil
from pathlib import Path
from typing import Tuple, Optional, List


class EncodingConverter:
    """Encoding Converter Class"""
    
    # Supported target encodings
    SUPPORTED_ENCODINGS = [
        'UTF-8',
        'UTF-8-SIG',
        'GBK',
        'GB2312',
        'GB18030',
        'BIG5',
        'LATIN-1',
        'ASCII',
        'UTF-16',
        'UTF-16-LE',
        'UTF-16-BE',
        'UTF-32',
        'UTF-32-LE',
        'UTF-32-BE',
        'ISO-8859-1',
        'WINDOWS-1252',
        'SHIFT_JIS',
        'EUC-JP',
        'EUC-KR',
    ]
    
    # Text file extensions
    TEXT_EXTENSIONS = {
        '.txt', '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.js', '.ts',
        '.html', '.htm', '.css', '.xml', '.json', '.yaml', '.yml', '.ini', '.conf',
        '.cfg', '.log', '.md', '.rst', '.csv', '.sql', '.sh', '.bat', '.cmd',
        '.ps1', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r',
        '.m', '.mm', '.pl', '.pm', '.lua', '.vim', '.el', '.clj', '.hs', '.erl',
        '.ex', '.exs', '.dart', '.groovy', '.gradle', '.properties', '.env',
        '.gitignore', '.gitattributes', '.dockerignore', '.editorconfig', '.babelrc',
        '.eslintrc', '.prettierrc', 'Makefile', 'CMakeLists.txt', 'Dockerfile',
        '.vue', '.jsx', '.tsx', '.svelte', '.scss', '.sass', '.less', '.styl',
    }
    
    def __init__(self):
        self.results = []
    
    def is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in self.TEXT_EXTENSIONS:
            return True
        
        if ext == '':
            if path.name in self.TEXT_EXTENSIONS:
                return True
        
        return False
    
    def detect_encoding(self, file_path: str) -> Tuple[str, float]:
        """
        Detect file encoding with Chinese encoding priority handling
        
        Returns:
            (encoding_name, confidence)
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            if not raw_data:
                return ('EMPTY', 1.0)
            
            # Check BOM first
            if raw_data.startswith(codecs.BOM_UTF8):
                return ('UTF-8-SIG', 1.0)
            elif raw_data.startswith(codecs.BOM_UTF16_LE):
                return ('UTF-16-LE', 1.0)
            elif raw_data.startswith(codecs.BOM_UTF16_BE):
                return ('UTF-16-BE', 1.0)
            
            # Use chardet to detect encoding
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'UNKNOWN')
            confidence = result.get('confidence', 0.0)
            
            if encoding is None:
                return ('UNKNOWN', 0.0)
            
            # Normalize encoding name
            encoding = encoding.upper()
            
            # Chinese encoding priority handling
            # If chardet detects ISO-8859-1 or WINDOWS-1252 with low confidence,
            # it might be Chinese encoding misdetected
            if encoding in ['ISO-8859-1', 'WINDOWS-1252', 'LATIN-1'] or confidence < 0.8:
                # Try Chinese encodings first
                chinese_encodings = ['GB18030', 'GBK', 'GB2312', 'BIG5']
                best_encoding = encoding
                best_confidence = confidence
                
                for enc in chinese_encodings:
                    try:
                        decoded = raw_data.decode(enc, errors='strict')
                        # Verify it's valid text (no excessive replacement chars)
                        if self._is_valid_chinese_text(decoded):
                            # If original detection was low confidence or wrong encoding family
                            if confidence < 0.8 or encoding in ['ISO-8859-1', 'WINDOWS-1252', 'LATIN-1']:
                                return (enc, max(confidence, 0.9))
                            best_encoding = enc
                            best_confidence = 0.95
                            break
                    except (UnicodeDecodeError, LookupError):
                        continue
                
                return (best_encoding, best_confidence)
            
            # Handle UTF-8 without BOM
            if encoding == 'UTF-8':
                # Verify it's actually valid UTF-8
                try:
                    raw_data.decode('utf-8', errors='strict')
                except UnicodeDecodeError:
                    # Might be Chinese encoding
                    for enc in ['GB18030', 'GBK', 'GB2312']:
                        try:
                            raw_data.decode(enc, errors='strict')
                            return (enc, 0.9)
                        except:
                            continue
            
            return (encoding, confidence)
            
        except Exception as e:
            return (f'ERROR: {str(e)}', 0.0)
    
    def _is_valid_chinese_text(self, text: str) -> bool:
        """
        Check if decoded text contains valid Chinese characters
        instead of garbled text
        """
        if not text:
            return False
        
        # Count Chinese characters
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        
        # Count common garbled characters (Latin extended chars that often appear in misdecoded Chinese)
        # These are typical misdecodings of Chinese bytes
        garbled_chars = sum(1 for char in text if char in 
            '¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ')
        
        total_chars = len([c for c in text if c.isalpha()])
        
        # If we have Chinese characters, it's likely valid
        if chinese_chars > 0:
            return True
        
        # If we have many garbled characters and no Chinese, it's likely misdecoded
        if garbled_chars > 10 and chinese_chars == 0:
            return False
        
        # If mostly ASCII, it's probably fine
        ascii_chars = sum(1 for char in text if ord(char) < 128)
        if ascii_chars / len(text) > 0.9:
            return True
        
        return True
    
    def read_file(self, file_path: str, encoding: str) -> str:
        """Read file content"""
        # Handle UTF-8 with BOM
        if encoding == 'UTF-8-SIG':
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                return f.read()
        
        # Handle other encodings
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
        except:
            # If failed, read as binary then decode
            with open(file_path, 'rb') as f:
                return f.read().decode(encoding, errors='replace')
    
    def convert_file(self, file_path: str, target_encoding: str, 
                     backup: bool = True, overwrite: bool = False) -> Tuple[bool, str]:
        """
        Convert file encoding
        
        Args:
            file_path: File path
            target_encoding: Target encoding
            backup: Whether to backup original file
            overwrite: Whether to overwrite original file
        
        Returns:
            (success, message)
        """
        try:
            # Detect source encoding
            source_encoding, confidence = self.detect_encoding(file_path)
            
            if source_encoding.startswith('ERROR'):
                return (False, f"Detection failed: {source_encoding}")
            
            if source_encoding == target_encoding:
                return (True, "Same encoding, no conversion needed")
            
            # Read content
            content = self.read_file(file_path, source_encoding)
            
            # Backup original file
            if backup:
                backup_path = f"{file_path}.bak"
                shutil.copy2(file_path, backup_path)
            
            # Write with new encoding
            if overwrite:
                output_path = file_path
            else:
                base, ext = os.path.splitext(file_path)
                output_path = f"{base}_{target_encoding}{ext}"
            
            # Handle encodings with BOM
            if target_encoding == 'UTF-8-SIG':
                with open(output_path, 'w', encoding='utf-8-sig') as f:
                    f.write(content)
            elif target_encoding in ['UTF-16', 'UTF-16-LE', 'UTF-16-BE']:
                encoding_map = {
                    'UTF-16': 'utf-16-le',
                    'UTF-16-LE': 'utf-16-le',
                    'UTF-16-BE': 'utf-16-be',
                }
                with open(output_path, 'w', encoding=encoding_map[target_encoding]) as f:
                    f.write(content)
            elif target_encoding in ['UTF-32', 'UTF-32-LE', 'UTF-32-BE']:
                encoding_map = {
                    'UTF-32': 'utf-32-le',
                    'UTF-32-LE': 'utf-32-le',
                    'UTF-32-BE': 'utf-32-be',
                }
                with open(output_path, 'w', encoding=encoding_map[target_encoding]) as f:
                    f.write(content)
            else:
                with open(output_path, 'w', encoding=target_encoding.lower()) as f:
                    f.write(content)
            
            if overwrite:
                return (True, f"Converted: {source_encoding} -> {target_encoding}")
            else:
                return (True, f"Created: {output_path}")
                
        except Exception as e:
            return (False, f"Conversion failed: {str(e)}")
    
    def scan_directory(self, directory: str, recursive: bool = True,
                       include_binary: bool = False) -> List[dict]:
        """
        Scan directory for all files
        
        Args:
            directory: Directory path
            recursive: Whether to scan recursively
            include_binary: Whether to include binary files
        
        Returns:
            List of file information
        """
        results = []
        path = Path(directory)
        
        if recursive:
            files = path.rglob('*')
        else:
            files = path.iterdir()
        
        for file_path in files:
            if file_path.is_file():
                # Check if text file
                if not include_binary and not self.is_text_file(str(file_path)):
                    continue
                
                # Detect encoding
                encoding, confidence = self.detect_encoding(str(file_path))
                
                results.append({
                    'path': str(file_path),
                    'name': file_path.name,
                    'encoding': encoding,
                    'confidence': confidence,
                    'size': file_path.stat().st_size,
                })
        
        return results
    
    def get_supported_encodings(self) -> List[str]:
        """Get list of supported target encodings"""
        return self.SUPPORTED_ENCODINGS.copy()


