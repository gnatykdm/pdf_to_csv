from pypdf import PdfReader
from pathlib import Path
import pandas as pd
import uuid
import os

BASE_DATA_FOLDER: Path = Path('./data/')
OUTPUT_FILE: Path = Path('./output.csv')

def _is_folder_exists() -> bool:
    if not os.path.exists(BASE_DATA_FOLDER):
        print("❌ Folder 'data' does not exist")
        return False
    return True

def _files_list() -> list[Path]:
    return list(BASE_DATA_FOLDER.glob('*.pdf'))

def _is_path_exists(path: Path) -> bool:
    return os.path.exists(path)

def read_pdf(path: Path) -> tuple[list[str], list[str]]:
    if not _is_path_exists(path):
        raise ValueError(f"PDF does not exist: {path}")
    
    reader: PdfReader = PdfReader(path)
    page = reader.pages[0]
    text = page.extract_text()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    if lines[0].startswith("Sales Report"):
        lines = lines[1:]
    
    header = lines[:6]
    data_lines = lines[6:]
    return header, data_lines


def inject_to_df(header: list[str], data_lines: list[str]) -> pd.DataFrame:
    rows = [data_lines[i:i+6] for i in range(0, len(data_lines), 6)]
    df = pd.DataFrame(rows, columns=header)
    df["Quantity"] = df["Quantity"].astype(int)
    df["Price"] = df["Price"].astype(float)
    df["Rating"] = df["Rating"].astype(float)
    df["UUID"] = [str(uuid.uuid1()) for _ in range(len(df))]
    df["Revenue"] = df["Quantity"] * df["Price"]
    return df


def load_to_csv(df: pd.DataFrame, output_path: Path = OUTPUT_FILE) -> None:
    df.to_csv(output_path, index=False)
    print(f"✓ Saved to {output_path}")


def main():
    print("\n" + "="*50)
    print("📄 PDF to CSV Converter")
    print("="*50 + "\n")
    
    if not _is_folder_exists():
        return
    
    pdf_files = _files_list()
    
    if not pdf_files:
        print("❌ No PDF files found in 'data' folder")
        return
    
    print(f"✓ Detected {len(pdf_files)} PDF file(s)")
    print("📖 Starting to read...\n")
    
    all_dataframes = []
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        try:
            print(f"   [{idx}/{len(pdf_files)}] Reading {pdf_path.name}...", end=" ")
            header, data_lines = read_pdf(pdf_path)
            df = inject_to_df(header, data_lines)
            all_dataframes.append(df)
            print(f"✓ ({len(df)} rows)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if all_dataframes:
        print(f"\n📊 Combining data from {len(all_dataframes)} file(s)...")
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"✓ Total rows: {len(combined_df)}")
        
        print(f"\n💾 Exporting to CSV...")
        load_to_csv(combined_df)
        
        print("\n" + "="*50)
        print("✅ Process completed successfully!")
        print("="*50 + "\n")
    else:
        print("\n❌ No data to export")


if __name__ == "__main__":
    main()