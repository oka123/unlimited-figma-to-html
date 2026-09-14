import json
from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    path = flow.request.path

    # Filter khusus endpoint Anima App yang relevan
    is_anima_target = "api.animaapp.com/v2/" in url
    is_stigg_target = "edge.api.stigg.io" in url and "entitlements-state.json" in url

    if not (is_anima_target or is_stigg_target):
        return

    try:
        content = flow.response.content
        if not content:
            return
        data = json.loads(content)

        # Fungsi rekursif umum untuk override limit / grant / status flag
        def walk_and_max(obj):
            if isinstance(obj, dict):
                # Ubah plan jadi Business atau naikkan limit related keys
                if "plan" in obj:
                    obj["plan"] = "Business"
                if "team_plan" in obj:
                    obj["team_plan"] = "Business"
                if "is_in_paying_team" in obj:
                    obj["is_in_paying_team"] = True
                if "is_admin" in obj:
                    obj["is_admin"] = True
                
                # Batasan screen / component / projects
                if "storybook_components_limit" in obj:
                    obj["storybook_components_limit"] = 99999
                if "team_screens_limit" in obj:
                    obj["team_screens_limit"] = 99999
                if "active_projects_count" in obj and obj["active_projects_count"] is not None:
                    obj["active_projects_count"] = 99999

                # Anima style fields
                if "is_granted" in obj or "/entitlements" in path:
                    obj["is_granted"] = True
                if "limit" in obj or "/entitlements" in path:
                    obj["limit"] = 99999.0
                if "usage" in obj:
                    obj["usage"] = 0.0

                # Stigg style fields
                if "usageLimit" in obj:
                    obj["usageLimit"] = 99999
                if "hasUnlimitedUsage" in obj:
                    obj["hasUnlimitedUsage"] = True
                if "hasSoftLimit" in obj:
                    obj["hasSoftLimit"] = False
                if "isGranted" in obj:
                    obj["isGranted"] = True
                if "accessDeniedReason" in obj:
                    obj["accessDeniedReason"] = None

                # Aktifkan seluruh boolean flag di dalam experiments atau object umum jika bernilai False/limitasi
                for k, v in obj.items():
                    if isinstance(v, bool) and not v and k not in ["is_archived", "is_pre_process_error", "is_pre_process_running"]:
                        # Biarkan beberapa flag aman, atau paksa aktifkan fitur berbayar
                        pass
                    walk_and_max(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk_and_max(item)

        # Penanganan spesifik per endpoint jika struktur root butuh pemastian eksplisit
        if "/users/me" in path and not "/team_" in path and isinstance(data, dict):
            data["plan"] = "Business"
            data["is_in_paying_team"] = True
            data["is_admin"] = True
            # Paksa semua eksperimen jadi true jika berupa boolean
            if "experiments" in data and isinstance(data["experiments"], dict):
                for exp_k in data["experiments"]:
                    data["experiments"][exp_k] = True

        if "/team_memberships" in path and isinstance(data, dict):
            results = data.get("results", [])
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict):
                        item["team_plan"] = "Business"
                        item["access_level"] = "owner"
                        item["storybook_components_limit"] = 99999
                        item["team_screens_limit"] = 99999
                        item["allow_data_training"] = True

        if "/projects/" in path and isinstance(data, dict):
            results = data.get("results", [])
            if isinstance(results, list):
                for item in results:
                    if isinstance(item, dict):
                        item["is_locked"] = False
                        item["is_archived"] = False

        # Jalankan general walker untuk menyapu semua bagian tersembunyi
        walk_and_max(data)

        # Encode ulang response
        flow.response.content = json.dumps(data).encode("utf-8")
        flow.response.headers["content-type"] = "application/json"

    except Exception as e:
        print(f"Error modifying Anima/Stigg response for {url}: {e}")