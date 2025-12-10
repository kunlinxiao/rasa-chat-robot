import requests

class GaodeWeatherClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })

    def get_adcode(self, city_name: str) -> str:
        """获取城市的adcode（行政编码）"""
        url = "https://restapi.amap.com/v3/config/district"
        params = {
            "keywords": city_name,
            "key": self.api_key,
            "subdistrict": 0
        }
        response = self.session.get(url, params=params)
        data = response.json()
        if data.get("status") == "1" and data.get("districts"):
            return data["districts"][0]["adcode"]
        return None

    def get_3day_forecast(self, city_name: str) -> str:
        """获取格式化的3天天气预报（返回字符串）"""
        adcode = self.get_adcode(city_name)
        if not adcode:
            return f"❌ 未找到城市【{city_name}】"

        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            "key": self.api_key,
            "city": adcode,
            "extensions": "all",
            "output": "JSON"
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") != "1" or not data.get("forecasts"):
                return "⚠️ 天气查询失败，请稍后重试"

            forecast = data["forecasts"][0]
            casts = forecast["casts"][:3]

            result = [
                f"🌤️【{city_name}】未来三天天气预报",
                f"更新时间：{forecast['reporttime']}",
                "════════════════════════"
            ]

            for day in casts:
                result.append(
                    f"📅 {day['date']} | "
                    f"白天{day['dayweather']:4} | "
                    f"夜间{day['nightweather']:4} | "
                    f"温度 {day['nighttemp']}~{day['daytemp']}°C"
                )

            return "\n".join(result)

        except Exception as e:
            print(f"Weather API Error: {str(e)}")
            return "⚠️ 天气服务暂时不可用"

# ========== 使用示例 ==========
if __name__ == "__main__":
    # 高德api
    client = GaodeWeatherClient("*****************************************f")
    print(client.get_3day_forecast("北京"))
