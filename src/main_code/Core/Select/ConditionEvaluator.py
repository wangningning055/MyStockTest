"""
condition_evaluator.py - 条件评估引擎
负责评估树形条件结构，判断股票是否符合选股条件
"""

from typing import List, Dict, Any, Union, Optional
import json
import logging
import os
# 假设models已经定义
from src.main_code.Core.Select.Models import TreeNode, ConditionNode, GroupNode, FactorConfig


logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """
    条件评估器
    负责评估单个条件节点和条件树
    """
    
    def __init__(self, stock_data: Dict[str, Any], factors_metadata: Dict[str, Any]):
        """
        初始化条件评估器
        
        Args:
            stock_data: 股票数据，包含所有因子字段
                       例如: {
                           'code': '000001',
                           'name': '平安银行',
                           'open': 12.5,
                           'close': 12.8,
                           'is_up_up': 1.2,
                           ...
                       }
            factors_metadata: 因子元数据（从factors.json加载）
        """
        self.stock_data = stock_data
        self.factors_metadata = factors_metadata
        self.field_mapping = self._build_field_mapping()
        self.error_log = []
    
    def _build_field_mapping(self) -> Dict[str, str]:
        """
        构建因子名称到字段名的映射
        
        从factors.json中提取：
        name (显示名) -> name_field (数据库字段)
        
        例如：
        "3日放量增长条件" -> "is_up_up"
        """
        mapping = {}
        try:
            factors = self.factors_metadata.get('factors', {})
            for category_key, category in factors.items():
                for item in category.get('items', []):
                    # 使用显示名映射到字段名
                    mapping[item.get('name')] = item.get('name_field')
            
            logger.info(f"✅ 因子映射表已构建，共{len(mapping)}个因子")
            return mapping
        except Exception as e:
            logger.error(f"❌ 构建因子映射表失败: {e}")
            return {}
    
    def evaluate_tree(self, nodes: List[TreeNode]) -> tuple[bool, Optional[str]]:
        """
        评估整个条件树
        
        逻辑说明：
        - 树是一个节点列表，第一个节点的relation必须是'START'
        - 后续节点的relation指定与前一个结果的逻辑关系
        - 示例：
          [
            { relation: 'START', ... },     # 初始化
            { relation: 'AND', ... },       # 与前面的AND
            { relation: 'OR', ... }         # 与前面的OR
          ]
        
        Args:
            nodes: 条件树节点列表
            
        Returns:
            tuple: (是否满足条件, 错误信息)
        """
        self.error_log.clear()
        
        if not nodes:
            return True, None
        
        # 初始化结果
        current_result = None
        current_relation = None
        
        try:
            for i, node in enumerate(nodes):
                node_result, error = self._evaluate_node(node)
                
                if error:
                    self.error_log.append(error)
                
                if i == 0:
                    # 第一个节点
                    if node.relation != 'START':
                        logger.warn(f"⚠️ 第一个节点的relation应为START，实际为{node.relation}")
                    current_result = node_result
                else:
                    # 应用逻辑关系
                    if current_relation == 'AND':
                        current_result = current_result and node_result
                    elif current_relation == 'OR':
                        current_result = current_result or node_result
                    else:
                        logger.warn(f"⚠️ 未知的逻辑关系: {current_relation}")
                
                # 保存下一个节点的逻辑关系
                current_relation = node.relation
            
            return current_result, None
        
        except Exception as e:
            error_msg = f"❌ 评估条件树时出错: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _evaluate_node(self, node: TreeNode) -> tuple[bool, Optional[str]]:
        """
        评估单个节点
        
        Args:
            node: 节点对象（ConditionNode或GroupNode）
            
        Returns:
            tuple: (节点是否满足, 错误信息)
        """
        try:
            if isinstance(node, dict):
                if node.get('type') == 'condition':
                    node = ConditionNode(**node)
                elif node.get('type') == 'group':
                    node = GroupNode(**node)
            
            if isinstance(node, ConditionNode):
                return self._evaluate_condition(node)
            elif isinstance(node, GroupNode):
                return self._evaluate_group(node)
            else:
                error = f"❌ 未知的节点类型: {node.type if hasattr(node, 'type') else type(node)}"
                logger.error(error)
                return False, error
        
        except Exception as e:
            error = f"❌ 评估节点失败: {e}"
            logger.error(error)
            return False, error
    
    def _evaluate_condition(self, condition: ConditionNode) -> tuple[bool, Optional[str]]:
        """
        评估单个条件
        
        例如：
        - 因子名: "3日放量增长条件"
        - 操作符: "eq"
        - 值: "1"
        - 日期范围: dateFrom=30, dateTo=0（最近30天）
        
        Args:
            condition: 条件节点
            
        Returns:
            tuple: (是否满足, 错误信息)
        """
        try:
            # 1. 从映射表获取字段名
            field_name = self.field_mapping.get(condition.factor_name)
            if not field_name:
                error = f"❌ 因子 '{condition.factor_name}' 不存在于映射表中"
                logger.error(error)
                return False, error
            
            # 2. 获取字段值
            value = self.stock_data.get(field_name)
            
            if value is None:
                # 字段不存在，返回False（不满足条件）
                # 注意：这里可以根据需求改为警告而不是错误
                logger.debug(f"⚠️ 字段'{field_name}'在数据中不存在，因子: '{condition.factor_name}'")
                return False, None
            
            # 3. 应用操作符
            result = self._apply_operator(value, condition.operator, condition.value)
            
            # 4. 日期范围处理（可选）
            # 如果dateFrom和dateTo不为默认值，在这里进行时间序列处理
            # 现阶段假设传入的stock_data已经是目标日期的数据
            
            return result, None
        
        except Exception as e:
            error = f"❌ 评估条件 '{condition.factor_name}' 时出错: {e}"
            logger.error(error)
            return False, error
    
    def _evaluate_group(self, group: GroupNode) -> tuple[bool, Optional[str]]:
        """
        评估分组（递归）
        
        分组内的逻辑关系由:
        1. 分组内的relation字段
        2. 子节点的relation字段
        
        Args:
            group: 分组节点
            
        Returns:
            tuple: (分组是否满足, 错误信息)
        """
        try:
            if not group.children:
                return True, None
            
            # 递归评估子节点，逻辑与evaluate_tree相同
            current_result = None
            current_relation = None
            
            for i, child in enumerate(group.children):
                child_result, error = self._evaluate_node(child)
                
                if error:
                    self.error_log.append(error)
                
                if i == 0:
                    current_result = child_result
                else:
                    if current_relation == 'AND':
                        current_result = current_result and child_result
                    elif current_relation == 'OR':
                        current_result = current_result or child_result
                
                current_relation = child.relation if hasattr(child, 'relation') else None
            
            return current_result if current_result is not None else True, None
        
        except Exception as e:
            error = f"❌ 评估分组时出错: {e}"
            logger.error(error)
            return False, error
    
    def _apply_operator(self, field_value: float, operator: str, compare_value: float) -> bool:
        """
        应用操作符进行比较
        
        Args:
            field_value: 字段值
            operator: 操作符 ('gt', 'lt', 'eq', 'ge', 'le')
            compare_value: 比较值
            
        Returns:
            bool: 比较结果
        """
        try:
            field_value = float(field_value)
            compare_value = float(compare_value)
            
            if operator == 'gt':
                return field_value > compare_value
            elif operator == 'lt':
                return field_value < compare_value
            elif operator == 'eq':
                # 对于浮点数，使用近似相等
                return abs(field_value - compare_value) < 1e-6
            elif operator == 'ge':
                return field_value >= compare_value
            elif operator == 'le':
                return field_value <= compare_value
            else:
                raise ValueError(f"Unknown operator: {operator}")
        
        except Exception as e:
            logger.error(f"❌ 应用操作符失败: {e}")
            return False


class FactorEvaluator:
    """
    因子评估器
    对整个因子配置进行评估，返回综合评分
    """
    
    def __init__(self, factors_metadata: Dict[str, Any]):
        """
        初始化因子评估器
        
        Args:
            factors_metadata: 因子元数据
        """
        self.factors_metadata = factors_metadata
    
    def evaluate_stock(self, stock_data: Dict[str, Any], configs: List[FactorConfig]) -> float:
        """
        评估单只股票，返回综合评分
        
        评分逻辑：
        1. 对每个因子配置，评估其条件树
        2. 如果满足条件，加上该因子的权重
        3. 将总分标准化到0-100
        
        例如：
        - 因子1权重0.4，满足条件 -> +0.4分
        - 因子2权重0.6，满足条件 -> +0.6分
        - 总分: 1.0分 / 1.0总权重 = 100%
        
        Args:
            stock_data: 股票的所有因子数据
            configs: 因子配置列表
            
        Returns:
            float: 综合评分（0-100）
        """
        if not configs:
            return 0
        
        evaluator = ConditionEvaluator(stock_data, self.factors_metadata)
        
        # 计算总权重
        total_weight = sum(cfg.weight for cfg in configs)
        if total_weight == 0:
            logger.warn("⚠️ 总权重为0")
            return 0
        
        # 逐个评估因子配置
        score = 0
        for config in configs:
            try:
                # 评估条件树
                is_satisfied, error = evaluator.evaluate_tree(config.logic_tree)
                
                if error:
                    logger.error(f"因子 '{config.factor_group_name}': {error}")
                
                # 如果满足条件，加上权重
                if is_satisfied:
                    score += config.weight
                    logger.debug(f"✅ 因子 '{config.factor_group_name}' 满足条件，加{config.weight}分")
                else:
                    logger.debug(f"❌ 因子 '{config.factor_group_name}' 不满足条件")
            
            except Exception as e:
                logger.error(f"❌ 评估因子 '{config.factor_group_name}' 时出错: {e}")
        
        # 标准化到0-100
        final_score = (score / total_weight) * 100
        return final_score
    
    def evaluate_stocks_batch(self, stocks_data: List[Dict[str, Any]], configs: List[FactorConfig]) -> List[tuple]:
        """
        批量评估股票
        
        Args:
            stocks_data: 股票数据列表
            configs: 因子配置列表
            
        Returns:
            list: [(stock_code, stock_name, score), ...]，按分数排序
        """
        results = []
        
        for stock in stocks_data:
            try:
                score = self.evaluate_stock(stock, configs)
                results.append({
                    'code': stock.get('code'),
                    'name': stock.get('name'),
                    'score': score,
                    'industry': stock.get('industry')
                })
            except Exception as e:
                logger.error(f"❌ 评估股票 {stock.get('code')} 时出错: {e}")
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results


# ==================== 辅助函数 ====================

def load_factors_metadata(filepath: str = 'factors.json') -> Dict[str, Any]:
    """
    加载因子元数据
    
    Args:
        filepath: 因子JSON文件路径
        
    Returns:
        dict: 因子元数据
    """
    # 获取当前脚本文件的绝对路径
    script_path = os.path.abspath(__file__)
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(script_path)
    #print(f"当前脚本路径: {script_path}")
    #print(f"当前脚本目录: {script_dir}")
    # 构建因子JSON文件的绝对路径
    abs_filepath = os.path.join(script_dir, "../../" + filepath)
    #print(f"因子JSON文件绝对路径: {abs_filepath}")
    try:
        with open(abs_filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ 文件不存在: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON解析失败: {e}")
        return {}


# ==================== 测试示例 ====================

#if __name__ == '__main__':
#    # 配置日志
#    logging.basicConfig(level=logging.INFO)
    
#    # 加载因子元数据
#    factors_metadata = load_factors_metadata('factors.json')
    
#    # 模拟股票数据
#    mock_stock_data = {
#        'code': '000001',
#        'name': '平安银行',
#        'is_up_up': 1.2,  # 3日放量增长条件（假设数据库中is_up_up > 1表示是）
#        'volume_ratio': 15,  # 成交量涨跌幅
#        'avg_ratio_5': 1.08,  # 当日均价与5日均价比
#        'earn_ratio': 12.5,  # 市盈率行业排名
#        'is_pop_up': 1.1,  # 5日是否震荡上行
#        'change_Ratio_5': 7.5,  # 5日涨跌幅
#    }
    
#    # 创建因子配置
#    from models import ConditionNode, GroupNode, FactorConfig
    
#    # 条件1：3日放量增长条件 == 1
#    cond1 = ConditionNode(
#        relation='START',
#        factor_name='3日放量增长条件',
#        operator='eq',
#        value=1
#    )
    
#    # 条件2：当日成交量涨幅 > 10%
#    cond2 = ConditionNode(
#        relation='START',
#        factor_name='成交量涨跌幅',
#        operator='gt',
#        value=10
#    )
    
#    # 条件3：当日均价与5日均价比 > 1.05
#    cond3 = ConditionNode(
#        relation='AND',
#        factor_name='当日均价与5日均价比',
#        operator='gt',
#        value=1.05
#    )
    
#    # 创建分组：条件2 AND 条件3
#    group = GroupNode(
#        relation='OR',
#        children=[cond2, cond3]
#    )
    
#    # 创建完整的因子配置
#    config1 = FactorConfig(
#        factor_group_name='3日放量增长条件',
#        weight=0.4,
#        logic_tree=[cond1, group]
#    )
    
#    # 评估
#    evaluator = FactorEvaluator(factors_metadata)
#    score = evaluator.evaluate_stock(mock_stock_data, [config1])
    
#    print(f"\n股票 {mock_stock_data['name']} 的评分: {score:.2f}")