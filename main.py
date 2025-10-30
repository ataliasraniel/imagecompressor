#!/usr/bin/env python3
"""
Image Compressor for ENEM Data
Comprime imagens dos dados do ENEM de 2009 a 2023
"""

import os
import json
from pathlib import Path
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class CompressionConfig:
    """Configurações de compressão personalizáveis"""
    quality: int = 85  
    format: str = "JPEG"  
    max_width: Optional[int] = None 
    max_height: Optional[int] = None 
    optimize: bool = True
    progressive: bool = True
    backup_original: bool = False
    output_suffix: str = "_compressed"
    delete_original_on_format_change: bool = True

class ImageCompressor:
    """Classe principal para compressão de imagens"""
    
    def __init__(self, config: CompressionConfig):
        self.config = config
        self.stats = {
            "processed": 0,
            "errors": 0,
            "total_original_size": 0,
            "total_compressed_size": 0
        }
        self._setup_logging()
    
    def _setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('compression.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Redimensionar imagem se necessário"""
        if not self.config.max_width and not self.config.max_height:
            return image
        
        width, height = image.size
        
        if self.config.max_width and width > self.config.max_width:
            ratio = self.config.max_width / width
            height = int(height * ratio)
            width = self.config.max_width
        
        if self.config.max_height and height > self.config.max_height:
            ratio = self.config.max_height / height
            width = int(width * ratio)
            height = self.config.max_height
        
        if width != image.size[0] or height != image.size[1]:
            return image.resize((width, height), Image.Resampling.LANCZOS)
        
        return image
    
    def _get_save_kwargs(self) -> Dict[str, Any]:
        """Obter argumentos para salvar a imagem"""
        kwargs: Dict[str, Any] = {
            "optimize": self.config.optimize
        }
        
        if self.config.format.upper() == "JPEG":
            kwargs["quality"] = self.config.quality
            kwargs["progressive"] = self.config.progressive
        elif self.config.format.upper() == "PNG":
            kwargs["optimize"] = True
        elif self.config.format.upper() == "WEBP":
            kwargs["quality"] = self.config.quality
            kwargs["method"] = 6 
        
        return kwargs
    
    def compress_image(self, input_path: Path, output_path: Optional[Path] = None) -> bool:
        """Comprimir uma única imagem"""
        try:
            if not input_path.exists():
                self.logger.warning(f"Arquivo não encontrado: {input_path}")
                return False
            
            original_size = input_path.stat().st_size
            self.stats["total_original_size"] += original_size
            
            original_format = input_path.suffix.lower()
            target_format = f".{self.config.format.lower()}"
            format_changed = original_format != target_format
            
            with Image.open(input_path) as image:
                if self.config.format.upper() == "JPEG" and image.mode in ("RGBA", "P"):
                    rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                    image = rgb_image
                
               
                image = self._resize_image(image)
                if output_path is None:
                    if format_changed:
                        output_path = input_path.with_suffix(target_format)
                    elif self.config.backup_original:
                        stem = input_path.stem + self.config.output_suffix
                        suffix = f".{self.config.format.lower()}"
                        output_path = input_path.parent / f"{stem}{suffix}"
                    else:
                        output_path = input_path.with_suffix(f".{self.config.format.lower()}")
                
                if self.config.backup_original and not self.config.output_suffix and not format_changed:
                    backup_path = input_path.with_suffix(f"{input_path.suffix}.bak")
                    input_path.rename(backup_path)
                
                save_kwargs = self._get_save_kwargs()
                image.save(output_path, format=self.config.format.upper(), **save_kwargs)
            
            if (format_changed and 
                self.config.delete_original_on_format_change and 
                input_path != output_path and 
                input_path.exists()):
                input_path.unlink()  
                self.logger.info(f"Arquivo original excluído: {input_path.name} (convertido para {target_format})")
            
            compressed_size = output_path.stat().st_size
            self.stats["total_compressed_size"] += compressed_size
            self.stats["processed"] += 1
            
            compression_ratio = (1 - compressed_size / original_size) * 100
            format_info = f" [{original_format} -> {target_format}]" if format_changed else ""
            self.logger.info(
                f"Comprimido: {input_path.name} -> {output_path.name}{format_info} "
                f"({original_size:,} -> {compressed_size:,} bytes, "
                f"{compression_ratio:.1f}% reducao)"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao comprimir {input_path}: {str(e)}")
            self.stats["errors"] += 1
            return False
    
    def scan_and_compress_directory(self, directory: Path) -> List[Path]:
        """Escanear diretório e comprimir todas as imagens"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        compressed_files = []
        
        if not directory.exists():
            self.logger.warning(f"Diretório não encontrado: {directory}")
            return compressed_files
        
        image_files = []
        for ext in image_extensions:
            image_files.extend(directory.glob(f"*{ext}"))
            image_files.extend(directory.glob(f"*{ext.upper()}"))
        
        self.logger.info(f"Encontradas {len(image_files)} imagens em {directory}")
        
        for image_file in image_files:
            if self.compress_image(image_file):
                compressed_files.append(image_file)
        
        return compressed_files
    
    def process_enem_data(self, base_path: str = "assets/enem_data", 
                         start_year: int = 2009, end_year: int = 2023) -> Dict:
        """Processar todos os dados do ENEM"""
        base_path_obj = Path(base_path)
        
        if not base_path_obj.exists():
            self.logger.error(f"Caminho base não encontrado: {base_path_obj}")
            return self.stats
        
        total_directories = 0
        processed_directories = 0
        
        for year in range(start_year, end_year + 1):
            year_dir = base_path_obj / f"enem-{year}"
            
            if not year_dir.exists():
                self.logger.warning(f"Diretório do ano {year} não encontrado: {year_dir}")
                continue
            
            self.logger.info(f"Processando ano {year}...")
            
            image_dirs = list(year_dir.glob("*-images"))
            total_directories += len(image_dirs)
            
            for image_dir in image_dirs:
                self.logger.info(f"Processando diretório: {image_dir.name}")
                self.scan_and_compress_directory(image_dir)
                processed_directories += 1
        
        self.stats.update({
            "total_directories": total_directories,
            "processed_directories": processed_directories
        })
        
        return self.stats
    
    def print_statistics(self):
        """Imprimir estatísticas da compressão"""
        stats = self.stats
        
        print("\n" + "="*50)
        print("ESTATÍSTICAS DE COMPRESSÃO")
        print("="*50)
        print(f"Imagens processadas: {stats['processed']:,}")
        print(f"Erros: {stats['errors']:,}")
        print(f"Diretórios processados: {stats.get('processed_directories', 0):,}")
        print(f"Total de diretórios: {stats.get('total_directories', 0):,}")
        
        if stats['total_original_size'] > 0:
            original_mb = stats['total_original_size'] / (1024 * 1024)
            compressed_mb = stats['total_compressed_size'] / (1024 * 1024)
            reduction = (1 - stats['total_compressed_size'] / stats['total_original_size']) * 100
            
            print(f"Tamanho original total: {original_mb:.2f} MB")
            print(f"Tamanho comprimido total: {compressed_mb:.2f} MB")
            print(f"Redução total: {reduction:.1f}%")
            print(f"Espaço economizado: {original_mb - compressed_mb:.2f} MB")
        
        print("="*50)

def load_config(config_file: str = "compression_config.json") -> CompressionConfig:
    """Carregar configuração de arquivo JSON"""
    config_path = Path(config_file)
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return CompressionConfig(**config_data)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            print("Usando configuração padrão...")
    
    return CompressionConfig()

def save_default_config(config_file: str = "compression_config.json"):
    """Salvar configuração padrão em arquivo JSON"""
    config = CompressionConfig()
    config_data = {
        "quality": config.quality,
        "format": config.format,
        "max_width": config.max_width,
        "max_height": config.max_height,
        "optimize": config.optimize,
        "progressive": config.progressive,
        "backup_original": config.backup_original,
        "output_suffix": config.output_suffix,
        "delete_original_on_format_change": config.delete_original_on_format_change
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"Configuração padrão salva em: {config_file}")

def main():
    """Função principal"""
    print("Image Compressor para dados do ENEM")
    print("Criando arquivo de configuração padrão...")
    
    if not Path("compression_config.json").exists():
        save_default_config()
    
    config = load_config()
    
    print(f"\nConfigurações carregadas:")
    print(f"- Qualidade: {config.quality}")
    print(f"- Formato: {config.format}")
    print(f"- Redimensionar: {config.max_width}x{config.max_height}" if config.max_width or config.max_height else "- Redimensionar: Não")
    print(f"- Backup original: {config.backup_original}")
    print(f"- Sufixo de saída: {config.output_suffix}")
    
    compressor = ImageCompressor(config)
    
    print("\nIniciando processamento...")
    compressor.process_enem_data()
    
    compressor.print_statistics()

if __name__ == "__main__":
    main()