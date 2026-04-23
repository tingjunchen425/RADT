import requests
import urllib.parse
from typing import Dict, Any, List

class SearchAgent:
    """
    Search Agent (無狀態/弱狀態工具)
    負責檢索外部資料庫 (如 ICE API) 以協助擴充 active KG。
    符合 DOs/DON'Ts：
    - 接受查詢，檢索並回傳結構化新節點與路徑建議。
    - 不主動更新 KG。
    - 不與 Target LLM 互動。
    """
    
    ICE_BASE_URL = "https://ice.ntp.niehs.nih.gov/api/v1"

    @classmethod
    def search_chemical(cls, chemical_identifier: str) -> Dict[str, Any]:
        """
        [端點 A] 單一化學物質檢索
        支援: DTXSID, CASRN, InChIKey, Chemical name.
        """
        encoded_id = urllib.parse.quote(chemical_identifier)
        url = f"{cls.ICE_BASE_URL}/search?chemid={encoded_id}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "message": f"API Error: {response.status_code}", "data": None}
        except Exception as e:
            return {"status": "error", "message": str(e), "data": None}

    @classmethod
    def get_curve_surfer_data(cls, chemid: str = None, assay: str = None) -> Dict[str, Any]:
        """
        [端點 C] Curve Surfer 濃度-反應數據檢索
        提供 chemid (全部 assay)、assay (全部化學物)、或兩者皆給 (特定化學物於特定分析)。
        """
        params = []
        if chemid:
            params.append(f"chemid={urllib.parse.quote(chemid)}")
        if assay:
            params.append(f"assay={urllib.parse.quote(assay)}")
            
        if not params:
            return {"status": "error", "message": "Must provide either chemid or assay", "data": None}
            
        url = f"{cls.ICE_BASE_URL}/curves?{'&'.join(params)}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {"status": "success", "data": data}
            else:
                return {"status": "error", "message": f"API Error: {response.status_code}", "data": None}
        except Exception as e:
            return {"status": "error", "message": str(e), "data": None}

    @classmethod
    def analyze_results_for_kg(cls, query: str, api_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        將原始 API 返回結果轉換為給 Lead Agent 的「建議圖譜擴充資料 (Suggested Nodes/Edges)」
        """
        if api_result.get("status") != "success" or not api_result.get("data"):
            return []
            
        nodes = []
        data = api_result["data"]
        
        if isinstance(data, list):
            for idx, item in enumerate(data):
                # 簡易示範：將每一筆資料轉為一個潛在的子節點建議
                nodes.append({
                    "proposed_node_id": f"{query}_result_{idx}",
                    "node_type": "chemical_property",
                    "relation_to_parent": "has_property",
                    "properties": item
                })
                
        return nodes
