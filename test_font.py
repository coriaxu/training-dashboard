from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

def test_font():
    try:
        # 尝试使用内置的中文字体
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        
        c = canvas.Canvas("test.pdf")
        c.setFont("STSong-Light", 12)
        c.drawString(100, 750, "测试中文字符")
        c.save()
        print("成功创建测试PDF文件，使用STSong-Light字体")
        
    except Exception as e:
        print(f"PDF生成错误: {e}")

if __name__ == '__main__':
    test_font()
