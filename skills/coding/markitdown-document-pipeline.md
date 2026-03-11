# Skill: MarkItDown文档预处理流水线

## 元信息
- **类型**: coding
- **来源**: Microsoft MarkItDown (GitHub 86k+ stars)
- **链接**: https://github.com/microsoft/markitdown
- **创建日期**: 2026-03-11
- **版本**: 1.0

---

## 触发条件

使用此技能当：
- 需要将PDF/Word/Excel/PPT等非结构化文档转换为结构化Markdown
- 构建RAG系统的文档预处理流程
- 处理批量文档进行知识库构建
- 需要提取图片中的文字内容(OCR)

---

## 安装

```bash
# 基础安装
pip install markitdown

# 带OCR功能（支持图片文字提取）
pip install markitdown[ocr]

# 完整安装（所有插件）
pip install markitdown[all]
```

---

## Python API使用

### 基础用法

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

### 带OCR的图片处理

```python
from markitdown import MarkItDown

# 使用OCR提取图片文字
md = MarkItDown(enable_plugins=["ocr"])
result = md.convert("image_with_text.png")
print(result.text_content)
```

### 批量处理函数

```python
from markitdown import MarkItDown
from pathlib import Path
import json

def batch_convert_documents(input_dir: str, output_dir: str):
    """
    批量转换文档为Markdown

    Args:
        input_dir: 输入文档目录
        output_dir: 输出Markdown目录
    """
    md = MarkItDown()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    for file in input_path.iterdir():
        if file.suffix.lower() in ['.pdf', '.docx', '.pptx', '.xlsx', '.html', '.png', '.jpg']:
            try:
                result = md.convert(str(file))
                output_file = output_path / f"{file.stem}.md"
                output_file.write_text(result.text_content, encoding='utf-8')

                results.append({
                    'source': file.name,
                    'output': output_file.name,
                    'status': 'success',
                    'chars': len(result.text_content)
                })
            except Exception as e:
                results.append({
                    'source': file.name,
                    'status': 'failed',
                    'error': str(e)
                })

    # 保存处理日志
    log_file = output_path / 'conversion_log.json'
    log_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')

    return results

# 使用示例
results = batch_convert_documents("./raw_docs", "./markdown_output")
print(f"成功: {sum(1 for r in results if r['status'] == 'success')}")
print(f"失败: {sum(1 for r in results if r['status'] == 'failed')}")
```

---

## CLI使用

```bash
# 单个文件转换
markitdown document.pdf > document.md

# 指定输出文件
markitdown document.docx -o output.md

# 使用OCR
markitdown image.png --enable-ocr > output.md

# 处理网页
markitdown https://example.com > page.md
```

---

## RAG流程集成

```python
from markitdown import MarkItDown
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib

def rag_document_pipeline(file_path: str) -> dict:
    """
    RAG文档预处理流水线

    Returns:
        {
            'doc_id': str,          # 文档唯一ID
            'content': str,         # Markdown内容
            'chunks': List[str],    # 分块后的文本
            'metadata': dict        # 文档元数据
        }
    """
    # 1. 转换为Markdown
    md = MarkItDown()
    result = md.convert(file_path)

    # 2. 生成文档ID
    doc_id = hashlib.md5(result.text_content.encode()).hexdigest()[:12]

    # 3. 文本分块
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", " "]
    )
    chunks = splitter.split_text(result.text_content)

    return {
        'doc_id': doc_id,
        'content': result.text_content,
        'chunks': chunks,
        'metadata': {
            'source': file_path,
            'chars': len(result.text_content),
            'chunks': len(chunks)
        }
    }

# 使用示例
doc_data = rag_document_pipeline("report.pdf")
print(f"文档ID: {doc_data['doc_id']}")
print(f"分块数: {doc_data['metadata']['chunks']}")
```

---

## 支持格式对照表

| 格式 | 扩展名 | OCR支持 | 保留结构 |
|------|--------|---------|----------|
| PDF | .pdf | 可选 | 标题、段落 |
| Word | .docx | - | 标题、列表、表格 |
| Excel | .xlsx | - | 表格 |
| PowerPoint | .pptx | - | 标题、列表 |
| HTML | .html | - | 完整结构 |
| 图片 | .png/.jpg | 是 | - |
| 音频 | .mp3/.wav | 转录 | - |

---

## 最佳实践

1. **PDF处理**: 优先选择文本型PDF，扫描版PDF需启用OCR
2. **表格保留**: Excel转换后的Markdown表格可能需要手动调整
3. **图片提取**: 如需保留图片，建议单独处理图片文件
4. **批量处理**: 大量文档时建议使用异步/多线程
5. **错误处理**: 始终包装try-except处理损坏文件

---

## 常见问题

**Q: 转换后的Markdown格式混乱？**
A: 原文件格式越规范，转换效果越好。扫描版PDF必须使用OCR。

**Q: 如何处理表格？**
A: Excel和Word表格会转为Markdown表格格式，复杂表格可能需要手动修复。

**Q: 中文支持如何？**
A: 完全支持中文，OCR对中文识别效果良好。
