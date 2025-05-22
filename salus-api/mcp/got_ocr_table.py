import platform
import os
import re
import argparse
from pathlib import Path
import requests
from io import BytesIO
from PIL import Image
import numpy as np

# 检查并下载必要的工具函数
def download_helper_files():
    if not Path("cmd_helper.py").exists():
        r = requests.get(url="https://raw.githubusercontent.com/openvinotoolkit/openvino_notebooks/latest/utils/cmd_helper.py")
        open("cmd_helper.py", "w").write(r.text)

    if not Path("notebook_utils.py").exists():
        r = requests.get(url="https://raw.githubusercontent.com/openvinotoolkit/openvino_notebooks/latest/utils/notebook_utils.py")
        open("notebook_utils.py", "w").write(r.text)

    if not Path("pip_helper.py").exists():
        r = requests.get(url="https://raw.githubusercontent.com/openvinotoolkit/openvino_notebooks/latest/utils/pip_helper.py")
        open("pip_helper.py", "w").write(r.text)

# 安装必要的依赖
def install_dependencies():
    from pip_helper import pip_install
    
    pip_install("torch>=2.1", "torchvision", "Pillow", "opencv-python", "--extra-index-url", "https://download.pytorch.org/whl/cpu")
    pip_install("-U", "openvino>=2025.0.0", "openvino-tokenizers>=2025.0.0", "nncf>=2.15.0")
    pip_install("transformers>=4.49", "git+https://github.com/huggingface/optimum-intel.git", "--extra-index-url", "https://download.pytorch.org/whl/cpu")
    
    if platform.system() == "Darwin":
        pip_install("numpy<2.0")

# 加载图像函数
def load_image(image_file):
    if isinstance(image_file, str) and image_file.startswith("https://"):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(image_file)
    return image.convert("RGB")

# 将OCR结果转换为Markdown表格
def convert_to_markdown_table(text):
    # 检测表格结构
    lines = text.strip().split('\n')
    
    # 过滤掉空行
    lines = [line for line in lines if line.strip()]
    
    # 检查是否有表格结构
    if len(lines) < 2:
        return text
    
    # 尝试识别表格分隔符
    has_separator = False
    for i, line in enumerate(lines):
        if i > 0 and all(c == '-' or c == '|' or c == '+' or c.isspace() for c in line):
            has_separator = True
            break
    
    # 如果没有明显的表格分隔符，尝试根据空格或制表符分割
    if not has_separator:
        # 分析每行的列数
        rows = []
        for line in lines:
            # 使用正则表达式分割，处理多个连续空格的情况
            cells = re.split(r'\s{2,}|\t', line.strip())
            rows.append(cells)
        
        # 确定最大列数
        max_cols = max(len(row) for row in rows)
        
        # 创建Markdown表格
        md_table = []
        
        # 添加表头
        md_table.append("| " + " | ".join(rows[0] + [""] * (max_cols - len(rows[0]))) + " |")
        
        # 添加分隔行
        md_table.append("| " + " | ".join(["---"] * max_cols) + " |")
        
        # 添加数据行
        for row in rows[1:]:
            md_table.append("| " + " | ".join(row + [""] * (max_cols - len(row))) + " |")
        
        return "\n".join(md_table)
    
    # 处理有分隔符的表格
    else:
        # 查找所有分隔符的位置
        separator_indices = []
        for i, line in enumerate(lines):
            if all(c == '-' or c == '|' or c == '+' or c.isspace() for c in line):
                separator_indices.append(i)
        
        # 提取表头和数据行
        headers = []
        data_rows = []
        
        if separator_indices:
            first_separator = separator_indices[0]
            headers = lines[:first_separator]
            data_rows = [line for i, line in enumerate(lines) if i > first_separator and i not in separator_indices]
        else:
            headers = [lines[0]]
            data_rows = lines[1:]
        
        # 分析列数
        max_cols = 0
        for line in headers + data_rows:
            # 计算竖线数量来确定列数
            cols = line.count('|') + 1
            max_cols = max(max_cols, cols)
        
        # 创建Markdown表格
        md_table = []
        
        # 处理表头
        header_line = headers[0].replace('+', '|')
        header_cells = [cell.strip() for cell in header_line.split('|')]
        header_cells = [cell for cell in header_cells if cell]  # 移除空单元格
        
        md_table.append("| " + " | ".join(header_cells + [""] * (max_cols - len(header_cells))) + " |")
        md_table.append("| " + " | ".join(["---"] * max_cols) + " |")
        
        # 处理数据行
        for row in data_rows:
            row = row.replace('+', '|')
            cells = [cell.strip() for cell in row.split('|')]
            cells = [cell for cell in cells if cell]  # 移除空单元格
            md_table.append("| " + " | ".join(cells + [""] * (max_cols - len(cells))) + " |")
        
        return "\n".join(md_table)

# 使用提示词引导模型输出表格格式
def process_image_with_prompt(image, processor, model, output_format="markdown"):
    # 根据输出格式选择不同的提示词
    if output_format == "markdown":
        # 使用format=True参数告诉模型输出格式化文本
        inputs = processor(image, return_tensors="pt", format=True)
    else:
        # 普通文本识别
        inputs = processor(image, return_tensors="pt")
    
    # 生成文本
    generate_ids = model.generate(
        **inputs,
        do_sample=False,
        tokenizer=processor.tokenizer,
        stop_strings="<|im_end|>",
        max_new_tokens=4096,
    )
    
    # 解码生成的文本
    result = processor.decode(
        generate_ids[0, inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )
    
    # 如果是LaTeX格式的表格，进行特殊处理
    # if "\\begin{tabular}" in result:
    #     result = convert_latex_to_markdown(result)
    
    return result

def convert_latex_to_markdown(latex_text):
    """将LaTeX表格转换为Markdown格式"""
    # 提取表格内容
    if "\\begin{tabular}" not in latex_text:
        return latex_text
    
    lines = latex_text.strip().split('\n')
    table_content = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        if "\\begin{tabular}" in line:
            in_table = True
            continue
        elif "\\end{tabular}" in line:
            in_table = False
            continue
        
        if in_table:
            # 处理嵌套的tabular
            if "\\begin{tabular}" in line:
                nested_content = line[line.find("\\begin{tabular}"):line.find("\\end{tabular}") + len("\\end{tabular}")]
                line = line.replace(nested_content, nested_content.replace("&", "，").replace("\\\\", ""))
            
            # 移除hline
            if "\\hline" in line:
                line = line.replace("\\hline", "")
            
            # 处理单元格分隔符
            if "&" in line:
                cells = line.split("&")
                cells = [cell.strip() for cell in cells]
                # 移除每个单元格末尾的 \\
                if cells[-1].endswith("\\\\"):
                    cells[-1] = cells[-1][:-2].strip()
                table_content.append(cells)
    
    # 创建Markdown表格
    if not table_content:
        return latex_text
    
    # 确定最大列数
    max_cols = max(len(row) for row in table_content)
    
    # 创建Markdown表格
    md_table = []
    
    # 添加表头
    if table_content:
        md_table.append("| " + " | ".join(table_content[0] + [""] * (max_cols - len(table_content[0]))) + " |")
        
        # 添加分隔行
        md_table.append("| " + " | ".join(["---"] * max_cols) + " |")
        
        # 添加数据行
        for row in table_content[1:]:
            md_table.append("| " + " | ".join(row + [""] * (max_cols - len(row))) + " |")
    
    return "\n".join(md_table)
       
# 主函数
def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="GOT-OCR 2.0表格识别工具")
    parser.add_argument("--image", type=str, default="1.jpg", help="要处理的图像文件路径")
    parser.add_argument("--output", type=str, default="ocr_table.md", help="输出文件路径")
    parser.add_argument("--format", type=str, default="markdown", choices=["text", "markdown"], help="输出格式")
    parser.add_argument("--device", type=str, default="AUTO", help="推理设备")
    args = parser.parse_args()
    
    print("正在初始化GOT-OCR 2.0表格识别工具...")
    
    # 下载辅助文件（如果需要）
    if not Path("notebook_utils.py").exists() or not Path("pip_helper.py").exists():
        download_helper_files()
    
    # 导入必要的库
    from transformers import AutoProcessor
    from optimum.intel.openvino import OVModelForVisualCausalLM
    
    # 设置模型路径
    model_id = "stepfun-ai/GOT-OCR-2.0-hf"
    base_model_path = Path(model_id.split("/")[-1])
    model_path = base_model_path / "INT4"  # 使用压缩模型
    
    # 检查模型是否存在，如果不存在则提示用户
    if not model_path.exists():
        print(f"错误：找不到模型文件夹 {model_path}")
        print("请先运行got-ocr2.ipynb中的模型转换步骤，或者手动下载并转换模型。")
        return
    
    print("正在加载模型和处理器...")
    
    # 加载处理器和模型
    processor = AutoProcessor.from_pretrained(model_path)
    model = OVModelForVisualCausalLM.from_pretrained(model_path, device=args.device, use_fast=False)
    
    print("模型加载完成！")
    
    # 处理图像
    image_path = args.image
    if not os.path.exists(image_path):
        print(f"错误：找不到图像文件 {image_path}")
        return
    
    print(f"正在处理图像 {image_path}...")
    image = load_image(image_path)
    
    # 使用提示词处理图像
    print("正在识别图像中的文本...")
    result = process_image_with_prompt(image, processor, model, output_format=args.format)
    
    print("\n原始OCR结果:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    # 转换为Markdown表格
    if args.format == "markdown":
        if "\\begin{tabular}" in result:
            markdown_table = result
        elif not result.strip().startswith("|"):
            markdown_table = convert_to_markdown_table(result)
        else:
            markdown_table = result
    else:
        markdown_table = result
    
    print("\nMarkdown表格格式:")
    print("-" * 50)
    print(markdown_table)
    print("-" * 50)
    
    # 保存结果到文件
    with open("ocr_result.txt", "w", encoding="utf-8") as f:
        f.write(result)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown_table)
    
    print(f"\n处理完成！结果已保存到 ocr_result.txt 和 {args.output}")

if __name__ == "__main__":
    main()