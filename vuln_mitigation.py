import subprocess
import json

def run_snyk_fix():
    """Executa análise e correção automática de vulnerabilidades"""
    try:
        # Testa vulnerabilidades e atualiza pacotes
        subprocess.run(["snyk", "test", "--severity-threshold=medium"], check=True)
        subprocess.run(["snyk", "fix"], check=True)

        # Gera relatório
        result = subprocess.run(["snyk", "test", "--json"], capture_output=True, text=True)
        data = json.loads(result.stdout)
        high_vulns = [v for v in data.get("vulnerabilities", []) if v["severity"] in ["high", "critical"]]
        return {"high_vulns": len(high_vulns)}
    except Exception as e:
        return {"error": str(e)}
