#!/usr/bin/env python3
"""
CSV Translation Tool using ArgosTranslate
Translates CSV files based on column configuration in column_data.json
"""

import json
import csv
import os
import argparse
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any, Tuple
import time
import sys

import argostranslate.package
import argostranslate.translate
import translatehtml
from tqdm import tqdm


class InteractiveMenu:
    """Interactive menu for selecting files and languages"""
    
    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return {
            'en': 'English',
            'id': 'Indonesian',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'it': 'Italian',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish'
        }
    
    @staticmethod
    def display_menu_header():
        """Display program header"""
        print("\n" + "="*60)
        print("🌍 CSV TRANSLATION TOOL")
        print("   Powered by ArgosTranslate")
        print("="*60)
    
    @staticmethod
    def select_language(prompt: str, default: str = None) -> str:
        """Interactive language selection"""
        languages = InteractiveMenu.get_supported_languages()
        
        print(f"\n{prompt}")
        print("-" * 40)
        
        # Display languages in columns
        lang_items = list(languages.items())
        for i in range(0, len(lang_items), 2):
            left = f"{i+1:2d}. {lang_items[i][0]} - {lang_items[i][1]}"
            if i+1 < len(lang_items):
                right = f"{i+2:2d}. {lang_items[i+1][0]} - {lang_items[i+1][1]}"
                print(f"{left:<30} {right}")
            else:
                print(left)
        
        if default:
            print(f"\n0. Use default ({default} - {languages.get(default, 'Unknown')})")
        
        while True:
            try:
                choice = input(f"\nPilih nomor (1-{len(languages)}" + 
                             (f" atau 0 untuk default" if default else "") + "): ").strip()
                
                if choice == "0" and default:
                    return default
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(languages):
                    selected_code = lang_items[choice_num - 1][0]
                    selected_name = lang_items[choice_num - 1][1]
                    print(f"✅ Dipilih: {selected_name} ({selected_code})")
                    return selected_code
                else:
                    print("❌ Pilihan tidak valid!")
            except ValueError:
                print("❌ Masukkan nomor yang valid!")
            except KeyboardInterrupt:
                print("\n⚠️  Program dibatalkan")
                sys.exit(0)
    
    @staticmethod
    def select_files(available_files: List[str]) -> List[str]:
        """Interactive file selection"""
        if not available_files:
            print("❌ Tidak ada file CSV yang tersedia")
            return []
        
        print("\n📁 PILIH FILE CSV UNTUK DITERJEMAHKAN")
        print("-" * 40)
        
        for i, filename in enumerate(available_files, 1):
            print(f"{i:2d}. {filename}")
        
        print(f"\n{len(available_files)+1:2d}. Proses SEMUA file")
        print("0. Keluar")
        
        while True:
            try:
                choice = input(f"\nPilih nomor (0-{len(available_files)+1}): ").strip()
                choice_num = int(choice)
                
                if choice_num == 0:
                    print("👋 Program dibatalkan")
                    sys.exit(0)
                elif choice_num == len(available_files) + 1:
                    print("✅ Dipilih: SEMUA file akan diproses")
                    return available_files
                elif 1 <= choice_num <= len(available_files):
                    selected_file = available_files[choice_num - 1]
                    print(f"✅ Dipilih: {selected_file}")
                    return [selected_file]
                else:
                    print("❌ Pilihan tidak valid!")
            except ValueError:
                print("❌ Masukkan nomor yang valid!")
            except KeyboardInterrupt:
                print("\n⚠️  Program dibatalkan")
                sys.exit(0)
    
    @staticmethod
    def confirm_translation(source_lang: str, target_lang: str, files: List[str]) -> bool:
        """Confirm translation settings"""
        languages = InteractiveMenu.get_supported_languages()
        
        print("\n" + "="*50)
        print("📋 KONFIRMASI PENGATURAN")
        print("="*50)
        print(f"🔤 Bahasa asal    : {languages.get(source_lang, source_lang)} ({source_lang})")
        print(f"🎯 Bahasa tujuan  : {languages.get(target_lang, target_lang)} ({target_lang})")
        print(f"📁 File yang akan diproses:")
        for i, filename in enumerate(files, 1):
            print(f"   {i}. {filename}")
        print(f"📊 Total file     : {len(files)}")
        print("="*50)
        
        while True:
            try:
                confirm = input("Lanjutkan? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', 'ya']:
                    return True
                elif confirm in ['n', 'no', 'tidak']:
                    print("❌ Proses dibatalkan")
                    return False
                else:
                    print("❌ Masukkan 'y' untuk ya atau 'n' untuk tidak")
            except KeyboardInterrupt:
                print("\n⚠️  Program dibatalkan")
                sys.exit(0)


class CSVTranslator:
    """Main class for CSV translation operations"""
    
    def __init__(self, source_lang: str = "en", target_lang: str = "id"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.input_dir = Path("input")
        self.output_dir = Path("output") / target_lang
        self.column_config = self._load_column_config()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Install translation packages if needed
        self._install_translation_packages()
        
        # Initialize translation object for HTML translation
        self.translation_obj = None
        self._setup_html_translation()
    
    def _load_column_config(self) -> Dict:
        """Load column configuration from JSON file"""
        config_path = self.input_dir / "column_data.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _install_translation_packages(self):
        """Install required translation packages"""
        print(f"Checking translation packages for {self.source_lang} -> {self.target_lang}")
        
        # Update package index
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Find and install required package
        package_to_install = None
        for package in available_packages:
            if package.from_code == self.source_lang and package.to_code == self.target_lang:
                package_to_install = package
                break
        
        if package_to_install:
            # Check if already installed
            installed_packages = argostranslate.package.get_installed_packages()
            already_installed = any(
                pkg.from_code == self.source_lang and pkg.to_code == self.target_lang
                for pkg in installed_packages
            )
            
            if not already_installed:
                print(f"Installing translation package: {self.source_lang} -> {self.target_lang}")
                argostranslate.package.install_from_path(package_to_install.download())
            else:
                print(f"Translation package already installed: {self.source_lang} -> {self.target_lang}")
        else:
            raise ValueError(f"Translation package not available: {self.source_lang} -> {self.target_lang}")
    
    def _setup_html_translation(self):
        """Setup translation object for HTML translation"""
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == self.source_lang), None)
            to_lang = next((lang for lang in installed_languages if lang.code == self.target_lang), None)
            
            if from_lang and to_lang:
                self.translation_obj = from_lang.get_translation(to_lang)
                print(f"HTML translation object initialized: {self.source_lang} -> {self.target_lang}")
            else:
                print(f"Warning: Could not initialize HTML translation object")
                self.translation_obj = None
        except Exception as e:
            print(f"Warning: HTML translation setup failed: {e}")
            self.translation_obj = None
    
    def get_available_csv_files(self) -> List[str]:
        """Get list of available CSV files in input directory"""
        csv_files = []
        for file_path in self.input_dir.glob("*.csv"):
            if file_path.name in self.column_config:
                csv_files.append(file_path.name)
        return sorted(csv_files)
    
    def csv_to_json(self, csv_filename: str) -> Dict[str, Any]:
        """Convert CSV file to JSON format"""
        csv_path = self.input_dir / csv_filename
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        print(f"Converting {csv_filename} to JSON...")
        
        data = {"rows": []}
        
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Get total rows for progress bar
                rows_list = list(reader)
                
                with tqdm(total=len(rows_list), desc="📄 Converting CSV", unit="rows") as pbar:
                    for row_idx, row in enumerate(rows_list):
                        # Clean the row data (remove quotes and strip whitespace)
                        cleaned_row = {}
                        for key, value in row.items():
                            if key is not None:  # Skip None keys
                                cleaned_key = key.strip(' "')
                                cleaned_value = value.strip(' "') if value else ""
                                cleaned_row[cleaned_key] = cleaned_value
                        
                        data["rows"].append(cleaned_row)
                        pbar.update(1)
        
        except UnicodeDecodeError:
            # Try with different encoding
            with open(csv_path, 'r', encoding='latin-1', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Get total rows for progress bar
                rows_list = list(reader)
                
                with tqdm(total=len(rows_list), desc="📄 Converting CSV", unit="rows") as pbar:
                    for row_idx, row in enumerate(rows_list):
                        cleaned_row = {}
                        for key, value in row.items():
                            if key is not None:
                                cleaned_key = key.strip(' "')
                                cleaned_value = value.strip(' "') if value else ""
                                cleaned_row[cleaned_key] = cleaned_value
                        
                        data["rows"].append(cleaned_row)
                        pbar.update(1)
        
        print(f"  Converted {len(data['rows'])} rows to JSON")
        return data
    
    def translate_text(self, text: str, is_html: bool = False) -> str:
        """Translate a single text string"""
        if not text or text.strip() == "":
            return text
        
        try:
            if is_html and ('<' in text and '>' in text):
                # Use translatehtml for HTML content
                if self.translation_obj:
                    return str(translatehtml.translate_html(self.translation_obj, text))
                else:
                    # Fallback to regular translation if HTML translation is not available
                    print(f"Warning: HTML translation not available, using regular translation")
                    return argostranslate.translate.translate(text, self.source_lang, self.target_lang)
            else:
                # Use regular argostranslate for plain text
                return argostranslate.translate.translate(text, self.source_lang, self.target_lang)
        except Exception as e:
            print(f"Translation error for text: {text[:50]}... Error: {e}")
            return text  # Return original text if translation fails
    
    def translate_row_batch(self, args: Tuple[List[Dict], List[str], str]) -> List[Dict]:
        """Translate a batch of rows (for multiprocessing)"""
        rows, translate_columns, csv_filename = args
        
        # Re-initialize translation in subprocess
        argostranslate.package.update_package_index()
        
        # Setup HTML translation object for subprocess
        try:
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == self.source_lang), None)
            to_lang = next((lang for lang in installed_languages if lang.code == self.target_lang), None)
            
            translation_obj = None
            if from_lang and to_lang:
                translation_obj = from_lang.get_translation(to_lang)
        except Exception:
            translation_obj = None
        
        translated_rows = []
        
        with tqdm(total=len(rows), desc="🔄 Translating batch", unit="rows", leave=False) as pbar:
            for i, row in enumerate(rows):
                translated_row = row.copy()
                
                for column in translate_columns:
                    if column in row and row[column]:
                        text = str(row[column])
                        # Check if content contains HTML
                        is_html = '<' in text and '>' in text
                        
                        try:
                            if is_html and translation_obj:
                                # Use translatehtml for HTML content
                                translated_row[column] = str(translatehtml.translate_html(translation_obj, text))
                            else:
                                # Use regular argostranslate for plain text
                                translated_row[column] = argostranslate.translate.translate(text, self.source_lang, self.target_lang)
                        except Exception as e:
                            print(f"Translation error in subprocess: {e}")
                            translated_row[column] = text  # Keep original if translation fails
                
                translated_rows.append(translated_row)
                pbar.update(1)
        
        return translated_rows
    
    def translate_json_data(self, data: Dict[str, Any], csv_filename: str) -> Dict[str, Any]:
        """Translate JSON data using multiprocessing"""
        if csv_filename not in self.column_config:
            raise ValueError(f"No configuration found for {csv_filename}")
        
        config = self.column_config[csv_filename]
        translate_columns = config.get("translate", [])
        
        if not translate_columns:
            print(f"No columns to translate for {csv_filename}")
            return data
        
        print(f"Translating {csv_filename} ({len(data['rows'])} rows)...")
        print(f"Columns to translate: {', '.join(translate_columns)}")
        
        rows = data["rows"]
        translated_data = {"rows": []}
        
        # Determine optimal batch size and number of processes
        num_processes = min(mp.cpu_count(), 8)  # Limit to 8 processes max
        batch_size = max(10, len(rows) // (num_processes * 4))  # Adaptive batch size
        
        print(f"Using {num_processes} processes with batch size {batch_size}")
        
        # Create batches
        batches = []
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            batches.append((batch, translate_columns, csv_filename))
        
        # Process batches in parallel
        start_time = time.time()
        total_batches = len(batches)
        
        print(f"🚀 Starting translation with {total_batches} batches...")
        
        # Main progress bar for overall progress
        with tqdm(total=len(rows), desc="🌍 Translating", unit="rows", colour="green") as main_pbar:
            with ProcessPoolExecutor(max_workers=num_processes) as executor:
                future_to_batch = {
                    executor.submit(self.translate_row_batch, batch_args): i 
                    for i, batch_args in enumerate(batches)
                }
                
                for future in as_completed(future_to_batch):
                    batch_idx = future_to_batch[future]
                    try:
                        translated_batch = future.result()
                        translated_data["rows"].extend(translated_batch)
                        
                        # Update main progress bar
                        batch_size_actual = len(translated_batch)
                        main_pbar.update(batch_size_actual)
                        
                        # Update progress bar description with current stats
                        completed_rows = len(translated_data["rows"])
                        elapsed = time.time() - start_time
                        rate = completed_rows / elapsed if elapsed > 0 else 0
                        main_pbar.set_postfix({
                            'Rate': f'{rate:.1f} rows/s',
                            'Elapsed': f'{elapsed:.1f}s'
                        })
                        
                    except Exception as e:
                        tqdm.write(f"❌ Error processing batch {batch_idx}: {e}")
                        # Add original batch without translation as fallback
                        original_batch = batches[batch_idx][0]
                        translated_data["rows"].extend(original_batch)
                        main_pbar.update(len(original_batch))
        
        # Sort rows to maintain original order
        translated_data["rows"] = sorted(
            translated_data["rows"], 
            key=lambda x: next(
                i for i, orig_row in enumerate(rows) 
                if orig_row.get('id', str(i)) == x.get('id', str(i))
            )
        )
        
        total_time = time.time() - start_time
        print(f"\n✅ Translation completed in {total_time:.1f}s")
        print(f"   📊 Processed {len(translated_data['rows'])} rows")
        print(f"   ⚡ Average speed: {len(translated_data['rows'])/total_time:.1f} rows/sec")
        
        return translated_data
    
    def save_json_output(self, data: Dict[str, Any], csv_filename: str):
        """Save translated data to JSON file"""
        output_filename = csv_filename.replace('.csv', '.json')
        output_path = self.output_dir / output_filename
        
        print(f"Saving translated data to {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  Saved {len(data['rows'])} translated rows")
    
    def process_csv_file(self, csv_filename: str):
        """Complete pipeline: CSV -> JSON -> Translate -> Save"""
        print(f"\n{'='*60}")
        print(f"Processing: {csv_filename}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Convert CSV to JSON
            json_data = self.csv_to_json(csv_filename)
            
            # Step 2: Translate JSON data
            translated_data = self.translate_json_data(json_data, csv_filename)
            
            # Step 3: Save output
            self.save_json_output(translated_data, csv_filename)
            
            print(f"✅ Successfully processed {csv_filename}")
            
        except Exception as e:
            print(f"❌ Error processing {csv_filename}: {e}")
            raise
    
    def process_all_files(self):
        """Process all available CSV files"""
        available_files = self.get_available_csv_files()
        
        if not available_files:
            print("No CSV files found or configured for translation")
            return
        
        print(f"Found {len(available_files)} CSV files to process:")
        for i, filename in enumerate(available_files, 1):
            print(f"  {i}. {filename}")
        
        total_start_time = time.time()
        
        with tqdm(total=len(available_files), desc="📁 Processing files", unit="file", colour="blue") as file_pbar:
            for filename in available_files:
                file_pbar.set_description(f"📁 Processing {filename}")
                self.process_csv_file(filename)
                file_pbar.update(1)
        
        total_time = time.time() - total_start_time
        print(f"\n🎉 All files processed successfully in {total_time:.1f}s!")
        print(f"Output directory: {self.output_dir.absolute()}")


def main():
    """Main function with command line interface and interactive mode"""
    parser = argparse.ArgumentParser(description="Translate CSV files using ArgosTranslate")
    parser.add_argument("--source", "-s", help="Source language code")
    parser.add_argument("--target", "-t", help="Target language code")
    parser.add_argument("--file", "-f", help="Specific CSV file to translate")
    parser.add_argument("--list", "-l", action="store_true", help="List available CSV files")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto mode (en->id, all files)")
    
    args = parser.parse_args()
    
    try:
        # Check if running in interactive mode (default if no args provided)
        if not any(vars(args).values()) or args.interactive:
            # Interactive mode
            InteractiveMenu.display_menu_header()
            
            # Initialize translator with defaults to get available files
            temp_translator = CSVTranslator("en", "id")
            available_files = temp_translator.get_available_csv_files()
            
            if not available_files:
                print("❌ Tidak ada file CSV yang tersedia atau dikonfigurasi")
                return 1
            
            # Select source language
            source_lang = InteractiveMenu.select_language("🔤 PILIH BAHASA ASAL:", "en")
            
            # Select target language
            target_lang = InteractiveMenu.select_language("🎯 PILIH BAHASA TUJUAN:", "id")
            
            if source_lang == target_lang:
                print("⚠️  Bahasa asal dan tujuan sama, tidak perlu diterjemahkan!")
                return 1
            
            # Select files
            selected_files = InteractiveMenu.select_files(available_files)
            
            if not selected_files:
                return 1
            
            # Confirm settings
            if not InteractiveMenu.confirm_translation(source_lang, target_lang, selected_files):
                return 1
            
            # Initialize translator with selected languages
            translator = CSVTranslator(source_lang, target_lang)
            
        else:
            # Command line mode
            if args.auto:
                source_lang, target_lang = "en", "id"
                print("🚀 Auto mode: English -> Indonesian, semua file")
            else:
                source_lang = args.source or "en"
                target_lang = args.target or "id"
            
            translator = CSVTranslator(source_lang, target_lang)
            
            if args.list:
                files = translator.get_available_csv_files()
                print("Available CSV files:")
                for i, filename in enumerate(files, 1):
                    print(f"  {i}. {filename}")
                return 0
            
            if args.file:
                available_files = translator.get_available_csv_files()
                if args.file in available_files:
                    selected_files = [args.file]
                else:
                    print(f"File not found or not configured: {args.file}")
                    print("Available files:")
                    for filename in available_files:
                        print(f"  - {filename}")
                    return 1
            else:
                selected_files = translator.get_available_csv_files()
        
        # Process selected files
        if 'selected_files' in locals():
            if len(selected_files) == 1:
                translator.process_csv_file(selected_files[0])
            else:
                # Show processing summary
                print(f"\n🚀 Memulai proses translasi {len(selected_files)} file...")
                total_start_time = time.time()
                
                with tqdm(total=len(selected_files), desc="📁 Processing files", unit="file", colour="blue") as file_pbar:
                    for i, filename in enumerate(selected_files, 1):
                        file_pbar.set_description(f"📁 File {i}/{len(selected_files)}: {filename}")
                        translator.process_csv_file(filename)
                        file_pbar.update(1)
                
                total_time = time.time() - total_start_time
                print(f"\n🎉 SELESAI! Semua file berhasil diproses dalam {total_time:.1f}s")
                print(f"📂 Output tersimpan di: {translator.output_dir.absolute()}")
        else:
            translator.process_all_files()
    
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
