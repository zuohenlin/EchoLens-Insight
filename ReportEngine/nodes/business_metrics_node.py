"""
商业量化指标生成节点。

在报告生成流程的早期介入，综合各个引擎的输入数据，
调用LLM推演生成具体的商业价值和ROI量化指标。
这些指标将被注入到模板渲染的上下文中。
"""

import json
from typing import Dict, Any
from loguru import logger

from .base_node import BaseNode
from ..utils.json_parser import RobustJSONParser

SYSTEM_PROMPT_BUSINESS_METRICS = """
你是一个顶级的商业数据分析师和电商操盘手。你的任务是根据给定的舆情数据和分析报告，推演出具有说服力的商业量化指标。

【输入数据来源】
- 用户查询/分析目标
- 基础舆情数据摘要（声量、平台分布）
- 情感分析结果

【输出要求】
你必须返回一个严格的 JSON 对象，包含以下字段。对于无法精确计算的指标，请基于你的专业经验给出一个【合理的预估值】或【推演区间】，切忌留空。

JSON 格式要求：
{
    "estimated_exposure": "预估总曝光量，如 '120万+'",
    "conversion_intent_rate": "种草/转化意向率百分比，如 '8.5%'",
    "saved_pr_cost_wan": "潜在节省的公关成本（万元），如 '15.5'",
    "estimated_roi": "预估营销ROI，如 '1:3.5'",
    "sentiment_positive_rate": "正面情绪占比百分比，如 '65%'",
    "sentiment_negative_rate": "负面情绪占比百分比，如 '12%'"
}

【推演逻辑参考（你在内部思考时使用，不要输出）】
- 曝光量 = 抓取到的帖子阅读/播放量总和的放大预估
- 转化意向 = (正面评论 + 询问购买链接的评论) / 总评论数
- 节省公关成本 = 提前发现中高危负面帖子 * 历史处理每个帖子的平均成本
- ROI = 预估带来的新增销售额 / 营销投入成本
"""

class BusinessMetricsNode(BaseNode):
    def __init__(self, llm_client):
        super().__init__(llm_client, "BusinessMetricsNode")
        self.json_parser = RobustJSONParser(enable_json_repair=True)

    def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        执行商业指标推演。
        """
        logger.info("开始推演商业量化指标...")

        query = input_data.get('query', '')
        insight_report = input_data.get('insight_engine_report', '')

        # 构建用户提示词
        user_prompt = f"""
请基于以下信息，推演本次事件/活动的商业量化指标。

分析目标 (Query):
{query}

洞察报告摘要 (Insight Report):
{insight_report[:3000]} # 截断以防超出token

请返回符合系统提示词要求的 JSON 数据。
"""
        try:
            # 调用 LLM
            response_text = self.llm_client.generate(
                system_prompt=SYSTEM_PROMPT_BUSINESS_METRICS,
                user_prompt=user_prompt,
                temperature=0.3 # 保持较低温度以保证JSON格式和数值相对保守稳定
            )

            # 解析 JSON
            metrics = self.json_parser.parse(response_text)
            logger.info(f"商业量化指标推演成功: {metrics}")
            return metrics

        except Exception as e:
            logger.exception(f"商业量化指标推演失败: {str(e)}")
            # 失败时的兜底默认值
            return {
                "estimated_exposure": "数据不足，暂无预估",
                "conversion_intent_rate": "N/A",
                "saved_pr_cost_wan": "0",
                "estimated_roi": "N/A",
                "sentiment_positive_rate": "N/A",
                "sentiment_negative_rate": "N/A"
            }
