# codex-test

一个用于把 PDF 自动转换成 PPT 的小工具，目标是**尽可能避免内容丢失**。

## 设计思路
- 每一页 PDF 以高 DPI 渲染成 PNG。
- 每一页 PNG 放入一页 PPT（整页铺满，等比缩放）。
- 这种方式可以最大化保留原始版式、字体、图表和图片内容。

> 说明：输出的 PPT 页面是图片，不是可编辑文本/图表对象。如果你要求绝对保真，这通常是最稳妥的方法。

## 安装
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 用法
```bash
python pdf_to_ppt.py input.pdf -o output.pptx --dpi 300
```

参数：
- `pdf`：输入 PDF 路径。
- `-o, --output`：输出 PPTX 路径（默认与 PDF 同名）。
- `--dpi`：渲染清晰度，默认 `300`，可按质量和体积权衡。

## 示例
```bash
python pdf_to_ppt.py ./附件.pdf -o ./附件_转换版.pptx --dpi 300
```
