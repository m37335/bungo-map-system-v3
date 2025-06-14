#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗾 青空文庫5作品→完全地名フロー最終版

地名抽出エラーを修正し、正確な処理を実行
"""

import sys
import os
import sqlite3
import requests
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# v3パスを追加
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/bungo_map')

# v3システムをインポート
from bungo_map.extractors.simple_place_extractor import SimplePlaceExtractor
from bungo_map.ai.context_aware_geocoding import ContextAwareGeocodingService

class FinalWorkflowExecutor:
    """最終版完全フロー実行システム"""
    
    def __init__(self, db_path: str = '/app/bungo-map-v4/data/databases/bungo_v4.db'):
        self.db_path = db_path
        
        print("🔧 最終版完全フロー実行システム初期化中...")
        
        # v3システム初期化
        self.simple_extractor = SimplePlaceExtractor()
        self.ai_geocoding = ContextAwareGeocodingService()
        print("✅ v3統合システム初期化完了")
    
    def execute_place_extraction_and_geocoding(self):
        """地名抽出とGeocodingの実行"""
        print("🚀 最終版地名抽出+Geocoding実行開始")
        print("=" * 80)
        
        # フェーズ1: 既存データの確認
        print("\n📊 フェーズ1: 既存データ確認")
        print("-" * 50)
        
        stats = self._get_current_statistics()
        print(f"👥 作家数: {stats['authors']:,}")
        print(f"📚 作品数: {stats['works']:,}")
        print(f"📝 センテンス数: {stats['sentences']:,}")
        print(f"🗺️ 既存地名数: {stats['places']:,}")
        print(f"🔗 既存文-地名関係数: {stats['sentence_places']:,}")
        
        # フェーズ2: 地名抽出実行
        print("\n🗺️ フェーズ2: 全センテンス地名抽出実行")
        print("-" * 50)
        
        total_extracted = self._extract_all_places()
        print(f"\n✅ フェーズ2完了: {total_extracted}件の新規地名抽出")
        
        # フェーズ3: AI Geocoding実行
        print("\n🌍 フェーズ3: AI Geocoding実行")
        print("-" * 50)
        
        geocoded_count = self._execute_comprehensive_geocoding()
        print(f"\n✅ フェーズ3完了: {geocoded_count}件の座標取得")
        
        # 最終統計
        print("\n📊 フェーズ4: 最終統計表示")
        print("-" * 50)
        self._show_comprehensive_statistics()
        
        print(f"\n🎉 最終版完全フロー実行完了！")
    
    def _get_current_statistics(self) -> Dict[str, int]:
        """現在の統計情報取得"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            cursor = conn.execute("SELECT COUNT(*) FROM authors")
            stats['authors'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM works")
            stats['works'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM sentences")
            stats['sentences'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM places_master")
            stats['places'] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM sentence_places")
            stats['sentence_places'] = cursor.fetchone()[0]
            
            return stats
    
    def _extract_all_places(self) -> int:
        """全センテンスの地名抽出"""
        total_extracted = 0
        
        try:
            # 全センテンス取得
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT sentence_id, sentence_text, before_text, after_text, work_id
                    FROM sentences 
                    WHERE length(sentence_text) > 5
                    ORDER BY work_id, position_in_work
                """)
                all_sentences = cursor.fetchall()
                
                print(f"📝 処理対象センテンス: {len(all_sentences):,}件")
            
            # 地名抽出処理
            for i, (sentence_id, sentence_text, before_text, after_text, work_id) in enumerate(all_sentences):
                if i > 0 and i % 1000 == 0:
                    print(f"  📍 進捗: {i:,}/{len(all_sentences):,} ({i/len(all_sentences)*100:.1f}%)")
                
                try:
                    # 地名抽出
                    places = self.simple_extractor.extract_places_from_text(work_id, sentence_text)
                    
                    if places:
                        # データベースに追加
                        extracted = self._add_places_to_database(
                            sentence_id, places, before_text, after_text
                        )
                        total_extracted += extracted
                        
                        if extracted > 0:
                            place_names = [p.place_name for p in places]
                            print(f"    🗺️ 抽出: {', '.join(place_names)}")
                
                except Exception as e:
                    print(f"    ⚠️ センテンス処理エラー: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ 地名抽出エラー: {e}")
        
        return total_extracted
    
    def _add_places_to_database(self, sentence_id: int, places: List, 
                               before_text: str, after_text: str) -> int:
        """地名をデータベースに追加"""
        added_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for place in places:
                    try:
                        # places_masterに追加（重複チェック）
                        cursor = conn.execute(
                            "SELECT place_id FROM places_master WHERE place_name = ?",
                            (place.place_name,)
                        )
                        result = cursor.fetchone()
                        
                        if result:
                            place_id = result[0]
                        else:
                            # 新規地名追加
                            cursor = conn.execute("""
                                INSERT INTO places_master (place_name, canonical_name, place_type, confidence)
                                VALUES (?, ?, ?, ?)
                            """, (
                                place.place_name, 
                                place.place_name, 
                                '地名',
                                getattr(place, 'confidence', 0.8)
                            ))
                            place_id = cursor.lastrowid
                        
                        # sentence_placesに追加（重複チェック）
                        cursor = conn.execute("""
                            SELECT 1 FROM sentence_places 
                            WHERE sentence_id = ? AND place_id = ?
                        """, (sentence_id, place_id))
                        
                        if not cursor.fetchone():
                            conn.execute("""
                                INSERT INTO sentence_places (
                                    sentence_id, place_id, extraction_method, confidence,
                                    context_before, context_after, matched_text, created_at
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                sentence_id, place_id,
                                getattr(place, 'extraction_method', 'simple'),
                                getattr(place, 'confidence', 0.8),
                                before_text[:200], after_text[:200], place.place_name,
                                datetime.now().isoformat()
                            ))
                            added_count += 1
                    
                    except Exception as e:
                        print(f"      ⚠️ 地名追加エラー ({place.place_name}): {e}")
                        continue
                
                conn.commit()
        
        except Exception as e:
            print(f"    ❌ データベース追加エラー: {e}")
        
        return added_count
    
    def _execute_comprehensive_geocoding(self) -> int:
        """包括的AI Geocoding実行"""
        geocoded_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 未処理地名取得
                cursor = conn.execute("""
                    SELECT pm.place_id, pm.place_name
                    FROM places_master pm
                    WHERE pm.latitude IS NULL OR pm.longitude IS NULL
                    ORDER BY pm.place_name
                """)
                places_to_geocode = cursor.fetchall()
                
                print(f"  🎯 Geocoding対象: {len(places_to_geocode):,}件")
                
                for i, (place_id, place_name) in enumerate(places_to_geocode):
                    if i > 0 and i % 50 == 0:
                        print(f"    🌍 Geocoding進捗: {i}/{len(places_to_geocode)} ({i/len(places_to_geocode)*100:.1f}%)")
                    
                    try:
                        # センテンス文脈情報取得
                        cursor = conn.execute("""
                            SELECT s.sentence_text, sp.context_before, sp.context_after
                            FROM sentence_places sp
                            JOIN sentences s ON sp.sentence_id = s.sentence_id
                            WHERE sp.place_id = ?
                            ORDER BY sp.confidence DESC
                            LIMIT 1
                        """, (place_id,))
                        
                        context = cursor.fetchone()
                        if context:
                            sentence_text, context_before, context_after = context
                        else:
                            sentence_text = context_before = context_after = ""
                        
                        # AI Geocoding実行
                        result = self.ai_geocoding.geocode_place_sync(
                            place_name, sentence_text, context_before, context_after
                        )
                        
                        if result and result.latitude is not None:
                            # 座標更新
                            conn.execute("""
                                UPDATE places_master 
                                SET latitude = ?, longitude = ?, 
                                    verification_status = 'verified',
                                    geocoded_at = ?
                                WHERE place_id = ?
                            """, (
                                result.latitude, result.longitude, 
                                datetime.now().isoformat(), place_id
                            ))
                            
                            geocoded_count += 1
                            print(f"    🌍 {place_name}: ({result.latitude:.4f}, {result.longitude:.4f})")
                        else:
                            print(f"    ❌ {place_name}: Geocoding失敗")
                        
                        time.sleep(0.1)  # API制限
                        
                    except Exception as e:
                        print(f"    ⚠️ Geocodingエラー ({place_name}): {e}")
                        continue
                
                conn.commit()
        
        except Exception as e:
            print(f"  ❌ 包括的Geocodingエラー: {e}")
        
        return geocoded_count
    
    def _show_comprehensive_statistics(self):
        """包括的統計表示"""
        with sqlite3.connect(self.db_path) as conn:
            # 基本統計
            final_stats = self._get_current_statistics()
            
            # 作品別統計
            cursor = conn.execute("""
                SELECT 
                    a.name, w.title, w.sentence_count,
                    COUNT(DISTINCT pm.place_id) as unique_places,
                    COUNT(sp.sentence_place_id) as total_mentions
                FROM authors a
                JOIN works w ON a.author_id = w.author_id
                LEFT JOIN sentences s ON w.work_id = s.work_id
                LEFT JOIN sentence_places sp ON s.sentence_id = sp.sentence_id
                LEFT JOIN places_master pm ON sp.place_id = pm.place_id
                GROUP BY a.author_id, w.work_id
                ORDER BY w.created_at DESC
            """)
            work_stats = cursor.fetchall()
            
            # 頻出地名TOP10
            cursor = conn.execute("""
                SELECT 
                    pm.place_name, 
                    COUNT(sp.sentence_id) as mention_count,
                    pm.latitude, pm.longitude
                FROM places_master pm
                LEFT JOIN sentence_places sp ON pm.place_id = sp.place_id
                GROUP BY pm.place_id
                HAVING mention_count > 0
                ORDER BY mention_count DESC
                LIMIT 10
            """)
            top_places = cursor.fetchall()
            
            # Geocoding成功率
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_places,
                    COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded_places
                FROM places_master
            """)
            geocoding_stats = cursor.fetchone()
        
        print("📊 最終統計レポート")
        print("=" * 60)
        print(f"👥 作家数: {final_stats['authors']:,}")
        print(f"📚 作品数: {final_stats['works']:,}")
        print(f"📝 センテンス数: {final_stats['sentences']:,}")
        print(f"🗺️ 総地名数: {final_stats['places']:,}")
        print(f"🔗 文-地名関係数: {final_stats['sentence_places']:,}")
        
        if geocoding_stats:
            total_places, geocoded_places = geocoding_stats
            if total_places > 0:
                success_rate = (geocoded_places / total_places) * 100
                print(f"🌍 Geocoding成功率: {success_rate:.1f}% ({geocoded_places:,}/{total_places:,})")
        
        print(f"\n📖 作品別地名統計:")
        for author, title, sentences, unique_places, total_mentions in work_stats:
            if unique_places > 0:
                print(f"  • {author} - {title}: {unique_places}地名, {total_mentions}回言及")
        
        if top_places:
            print(f"\n🗺️ 頻出地名TOP10:")
            for place_name, count, lat, lng in top_places:
                coord_info = f"({lat:.3f}, {lng:.3f})" if lat and lng else "座標なし"
                print(f"  • {place_name}: {count}回 {coord_info}")


def main():
    """メイン実行関数"""
    print("🗾 最終版青空文庫地名抽出+Geocoding実行")
    print("=" * 80)
    
    executor = FinalWorkflowExecutor()
    executor.execute_place_extraction_and_geocoding()


if __name__ == "__main__":
    main() 