#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Regex地名抽出設定の改善案
現在の設定（regex_有名地名/市区町村/都道府県/郡）の分析と強化
"""

class RegexEnhancementAnalysis:
    """現在のregex設定の改善分析"""
    
    def __init__(self):
        self.current_performance = {
            "regex_有名地名": {
                "count": 637,
                "accuracy": "高い",
                "top_results": ["鎌倉(31)", "神田(31)", "江戸(31)", "本郷(24)", "上野(24)"],
                "strength": "明示的地名リストで誤抽出が少ない",
                "issue": "リストにない地名は抽出できない"
            },
            "regex_市区町村": {
                "count": 384,
                "accuracy": "中〜高",
                "pattern": r'[一-龯]{2,8}[市区町村]',
                "top_results": ["小川町(19)", "西片町(12)", "真砂町(12)", "東京市(12)"],
                "strength": "適度な長さ制限で品質確保",
                "issue": "境界条件が不十分（前後の文字チェックなし）"
            },
            "regex_都道府県": {
                "count": 61,
                "accuracy": "非常に高い",
                "strength": "明確なパターンで誤抽出ほぼなし",
                "issue": "特になし"
            },
            "regex_郡": {
                "count": 18,
                "accuracy": "中",
                "pattern": r'[一-龯]{2,6}[郡]',
                "strength": "郡レベルの地名も捕捉",
                "issue": "使用頻度が低い"
            }
        }
    
    def get_enhancement_recommendations(self):
        """改善推奨事項"""
        return {
            "immediate_improvements": [
                {
                    "target": "regex_市区町村",
                    "enhancement": "境界条件追加",
                    "new_pattern": r'(?<![一-龯])[一-龯]{2,6}[市区町村](?![一-龯])',
                    "benefit": "複合語での誤抽出防止"
                },
                {
                    "target": "regex_郡",
                    "enhancement": "長さ制限強化",
                    "new_pattern": r'(?<![一-龯])[一-龯]{2,4}[郡](?![一-龯])',
                    "benefit": "品質向上"
                }
            ],
            
            "additional_patterns": [
                {
                    "name": "regex_古典地名",
                    "pattern": r'(?:平安京|江戸|武蔵|相模|甲斐|信濃|越後|下野|上野|駿河|伊豆|伊勢|山城|大和|河内|和泉|摂津|近江|美濃|尾張|薩摩|土佐|陸奥|出羽)',
                    "benefit": "文学作品特有の古典地名を高精度で抽出"
                },
                {
                    "name": "regex_自然地形",
                    "pattern": r'(?<![一-龯])[一-龯]{2,4}[山川湖海](?![一-龯])',
                    "benefit": "自然地名の体系的抽出"
                },
                {
                    "name": "regex_寺社",
                    "pattern": r'(?<![一-龯])[一-龯]{2,4}[寺院神社宮](?![一-龯])',
                    "benefit": "宗教施設の地名抽出"
                }
            ],
            
            "anti_patterns": [
                {
                    "name": "方向語除外",
                    "pattern": r'(?<![一-龯])[東西南北](?=から|へ|に向かって)',
                    "purpose": "「東から西へ」のような方向語を除外"
                },
                {
                    "name": "植物名除外", 
                    "pattern": r'(?<![一-龯])[萩桜梅松竹](?=[がの](?:咲く|散る|茂る|延びる))',
                    "purpose": "「萩が茂る」のような植物名を除外"
                }
            ]
        }
    
    def analyze_problematic_cases(self):
        """問題ケースの分析"""
        return {
            "ginza_nlp_issues": {
                "萩": {
                    "issue": "植物名として使用されているのに地名として抽出",
                    "context": "大きな萩が人の背より高く延びて",
                    "solution": "文脈分析で植物用法を検出"
                },
                "柏": {
                    "issue": "寺院名の一部なのに地名として抽出",
                    "context": "高柏寺の五重の塔",
                    "solution": "「〜寺」パターンでの除外"
                },
                "東": {
                    "issue": "方向を示すのに地名として抽出",
                    "context": "東から西へ貫いた廊下",
                    "solution": "方向用法の文脈分析"
                },
                "都": {
                    "issue": "一般名詞なのに地名として抽出",
                    "context": "都のまん中に立って",
                    "solution": "特定の助詞パターンでの除外"
                }
            },
            "regex_performance": {
                "status": "良好",
                "reason": "上記問題ケースはregex系では抽出されていない",
                "strength": "明示的パターンにより誤抽出を回避"
            }
        }
    
    def get_best_practices(self):
        """ベストプラクティス"""
        return {
            "pattern_design": [
                "明示的地名リスト（regex_有名地名方式）が最も精度が高い",
                "境界条件（前後の文字チェック）は必須",
                "長さ制限で品質をコントロール（2-6文字推奨）",
                "カテゴリ別の信頼度設定で優先順位付け"
            ],
            
            "confidence_settings": {
                "regex_都道府県": 0.95,  # 最高精度
                "regex_古典地名": 0.92,  # 文学的重要性
                "regex_有名地名": 0.90,  # 明示的リスト
                "regex_市区町村": 0.85,  # パターンベース
                "regex_自然地形": 0.80,  # 地形名
                "regex_郡": 0.75,       # 使用頻度低
                "regex_寺社": 0.70      # 施設名
            },
            
            "hybrid_approach": [
                "regex（高精度）+ ginza_nlp（高網羅性）+ AI文脈分析（誤抽出除去）",
                "段階的フィルタリング：regex → ginza → context_analysis",
                "各手法の強みを活かした組み合わせ"
            ]
        }

# 実装例
def get_enhanced_regex_patterns():
    """強化されたregexパターンセット"""
    return {
        # 現在のパターンの改良版
        "都道府県_強化": {
            "pattern": r'(?<![一-龯])[北海青森岩手宮城秋田山形福島茨城栃木群馬埼玉千葉東京神奈川新潟富山石川福井山梨長野岐阜静岡愛知三重滋賀京都大阪兵庫奈良和歌山鳥取島根岡山広島山口徳島香川愛媛高知福岡佐賀長崎熊本大分宮崎鹿児島沖縄][都道府県](?![一-龯])',
            "confidence": 0.95
        },
        
        "市区町村_強化": {
            "pattern": r'(?<![一-龯])[一-龯]{2,6}[市区町村](?![一-龯])',
            "confidence": 0.85
        },
        
        # 新規パターン
        "古典地名": {
            "pattern": r'(?:平安京|江戸|武蔵|相模|甲斐|信濃|越後|下野|上野|駿河|伊豆|伊勢|山城|大和|河内|和泉|摂津|近江|美濃|尾張|薩摩|土佐|陸奥|出羽)',
            "confidence": 0.92
        },
        
        "自然地形": {
            "pattern": r'(?<![一-龯])[一-龯]{2,4}[山川湖海峠谷野原島岬浦崎](?![一-龯])',
            "confidence": 0.80
        }
    } 