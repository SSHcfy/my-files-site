import os
import base64
import sys
from pathlib import Path

# ---------- 配置 ----------
FILES_DIR = "files"          # 存放原始文件的文件夹
OUTPUT_HTML = "index.html"   # 输出的网页名
# --------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>我的学术附件</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; background: #f9f9f9; }}
  h1 {{ color: #333; }}
  .file-block {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
  .file-name {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #0366d6; }}
  pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
  code {{ font-family: "Courier New", monospace; }}
  img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
  .error {{ color: #d32f2f; }}
</style>
</head>
<body>
<h1>📚 附件内容一览</h1>
<p>以下内容由脚本自动生成，供 DeepSeek 阅读。</p>
{content}
</body>
</html>
"""

FILE_BLOCK_TEMPLATE = """
<div class="file-block">
  <div class="file-name">{filename}</div>
  {body}
</div>
"""

def extract_pdf_text(filepath):
    """尝试用 PyPDF2 提取 PDF 文字"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text)
    except ImportError:
        return "<span class='error'>需要安装 PyPDF2 才能提取文本，请运行: pip install PyPDF2</span>"
    except Exception as e:
        return f"<span class='error'>PDF 文本提取失败: {e}</span>"

def handle_text_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    ext = Path(filepath).suffix.lstrip(".")
    lang = ext if ext in ("py", "json", "html", "css", "js", "xml", "yaml", "yml") else ""
    return f"<pre><code>{content}</code></pre>"

def handle_image_file(filepath, relative_to_output):
    # 相对路径引用，方便部署
    path = Path(filepath).as_posix()
    return f'<img src="{path}" alt="{Path(filepath).name}">'

def generate_site():
    if not os.path.isdir(FILES_DIR):
        print(f"错误：找不到文件夹 '{FILES_DIR}'，请先创建并把文件放进去。")
        sys.exit(1)

    blocks = []
    files = sorted(os.listdir(FILES_DIR))
    if not files:
        print("files 文件夹是空的，请放入文件。")
        sys.exit(1)

    for fname in files:
        filepath = os.path.join(FILES_DIR, fname)
        if os.path.isdir(filepath):
            continue  # 忽略子文件夹
        ext = Path(fname).suffix.lower()
        try:
            if ext in (".txt", ".py", ".md", ".json", ".xml", ".yaml", ".yml", ".html", ".css", ".js", ".csv"):
                body = handle_text_file(filepath)
            elif ext == ".pdf":
                text = extract_pdf_text(filepath)
                body = f"<pre><code>{text}</code></pre>" if not text.startswith("<span") else text
            elif ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"):
                body = handle_image_file(filepath, relative_to_output=True)
            else:
                # 其他文件尝试当作文本打开
                try:
                    body = handle_text_file(filepath)
                except Exception:
                    body = "<span class='error'>无法识别或显示此文件类型。</span>"
        except Exception as e:
            body = f"<span class='error'>读取文件出错: {e}</span>"

        block = FILE_BLOCK_TEMPLATE.format(filename=fname, body=body)
        blocks.append(block)

    html_content = HTML_TEMPLATE.format(content="\n".join(blocks))
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ 成功生成 {OUTPUT_HTML}，共处理 {len(blocks)} 个文件。")

if __name__ == "__main__":
    generate_site()