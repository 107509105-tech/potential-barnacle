"""
邊界框坐標解析模組
從 LLM 生成的答案中提取邊界框坐標信息
"""
import re
from typing import List, Dict, Tuple


def parse_bboxes(answer: str) -> Tuple[str, List[Dict]]:
    """
    從答案文本中解析邊界框坐標

    Args:
        answer: LLM 生成的答案文本

    Returns:
        (clean_answer, bboxes)
        - clean_answer: 移除坐標標記後的答案文本
        - bboxes: 邊界框坐標列表，每個元素包含：
            {
                'image_index': int,
                'x1': float,  # 百分比 0-100
                'y1': float,
                'x2': float,
                'y2': float
            }
    """
    # 正則表達式匹配 [BBOX:image_index,x1,y1,x2,y2]
    pattern = r'\[BBOX:(\d+),(\d+(?:\.\d+)?),(\d+(?:\.\d+)?),(\d+(?:\.\d+)?),(\d+(?:\.\d+)?)\]'

    bboxes = []
    matches = re.findall(pattern, answer)

    for match in matches:
        image_index, x1, y1, x2, y2 = match
        bboxes.append({
            'image_index': int(image_index),
            'x1': float(x1),
            'y1': float(y1),
            'x2': float(x2),
            'y2': float(y2)
        })

    # 移除坐標標記，返回乾淨的答案
    clean_answer = re.sub(pattern, '', answer).strip()

    return clean_answer, bboxes


def validate_bbox(bbox: Dict) -> bool:
    """
    驗證邊界框坐標的有效性

    Args:
        bbox: 邊界框字典

    Returns:
        是否有效
    """
    try:
        # 檢查坐標範圍
        if not (0 <= bbox['x1'] <= 100 and 0 <= bbox['y1'] <= 100):
            return False
        if not (0 <= bbox['x2'] <= 100 and 0 <= bbox['y2'] <= 100):
            return False

        # 檢查坐標順序
        if bbox['x1'] >= bbox['x2'] or bbox['y1'] >= bbox['y2']:
            return False

        # 檢查索引
        if bbox['image_index'] < 0:
            return False

        return True
    except (KeyError, TypeError):
        return False


if __name__ == "__main__":
    # 測試代碼
    test_answer = """這是一個測試答案。根據文件內容，答案位於第一頁的中間部分。

[BBOX:0,10,20,90,60]"""

    clean_answer, bboxes = parse_bboxes(test_answer)

    print("原始答案:")
    print(test_answer)
    print("\n清理後的答案:")
    print(clean_answer)
    print("\n解析的邊界框:")
    for bbox in bboxes:
        print(f"  圖像 {bbox['image_index']}: ({bbox['x1']}, {bbox['y1']}) -> ({bbox['x2']}, {bbox['y2']})")
        print(f"    有效性: {validate_bbox(bbox)}")
