#!/usr/bin/env python
"""
PDF导出脚本
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径到sys.path
sys.path.insert(0, '/Users/mayiding/Desktop/GitMy/EchoLens-Insight')

def export_pdf(ir_file_path):
    """导出PDF"""
    try:
        # 读取IR文件
        print(f"正在读取报告文件: {ir_file_path}")
        with open(ir_file_path, 'r', encoding='utf-8') as f:
            document_ir = json.load(f)

        # 导入PDF渲染器
        from ReportEngine.renderers.pdf_renderer import PDFRenderer

        # 创建PDF渲染器
        print("正在初始化PDF渲染器...")
        renderer = PDFRenderer()

        # 生成PDF
        print("正在生成PDF...")
        pdf_bytes = renderer.render_to_bytes(document_ir, optimize_layout=True)

        # 确定输出文件名
        topic = document_ir.get('metadata', {}).get('topic', 'report')
        output_dir = Path('/Users/mayiding/Desktop/GitMy/EchoLens-Insight/final_reports/pdf')
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_filename = f"report_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = output_dir / pdf_filename

        # 保存PDF文件
        print(f"正在保存PDF到: {output_path}")
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)

        print(f"✅ PDF导出成功！")
        print(f"文件位置: {output_path}")
        print(f"文件大小: {len(pdf_bytes) / 1024 / 1024:.2f} MB")

        return str(output_path)

    except Exception as e:
        print(f"❌ PDF导出失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 使用最新的报告文件
    latest_report = "/Users/mayiding/Desktop/GitMy/EchoLens-Insight/final_reports/ir/report_ir_人工智能行情发展走势_20251119_235407.json"

    if os.path.exists(latest_report):
        print("="*50)
        print("开始导出PDF")
        print("="*50)
        result = export_pdf(latest_report)
        if result:
            print(f"\n📄 PDF文件已生成: {result}")
    else:
        print(f"❌ 报告文件不存在: {latest_report}")