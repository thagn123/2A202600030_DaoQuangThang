import os
import sys

def check(name: str, passed: bool, detail: str = "") -> dict:
    icon = "[OK]" if passed else "[FAIL]"
    print(f"  {icon} {name}" + (f" — {detail}" if detail else ""))
    return {"name": name, "passed": passed}

def run_checks():
    results = []
    base = os.path.dirname(__file__)

    print("\n" + "=" * 55)
    print("  Production Readiness Check - Day 12 Lab")
    print("=" * 55)

    print("\nFiles:")
    results.append(check("Dockerfile exists", os.path.exists(os.path.join(base, "Dockerfile"))))
    results.append(check("docker-compose.yml exists", os.path.exists(os.path.join(base, "docker-compose.yml"))))
    results.append(check(".dockerignore exists", os.path.exists(os.path.join(base, ".dockerignore"))))
    results.append(check(".env.example exists", os.path.exists(os.path.join(base, ".env.example"))))
    results.append(check("requirements.txt exists", os.path.exists(os.path.join(base, "requirements.txt"))))
    results.append(check("railway.toml exists", os.path.exists(os.path.join(base, "railway.toml"))))

    print("\nSecurity Check:")
    main_py = os.path.join(base, "app", "main.py")
    if os.path.exists(main_py):
        content = open(main_py).read()
        results.append(check("/health endpoint", "/health" in content))
        results.append(check("/ready endpoint", "/ready" in content))
        results.append(check("Auth implemented", "verify_api_key" in content))
        results.append(check("Rate limit implemented", "check_rate_limit" in content))
        results.append(check("SIGTERM handler", "SIGTERM" in content))
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\nResult: {passed}/{total} checks passed")
    return passed == total

if __name__ == "__main__":
    ready = run_checks()
    sys.exit(0 if ready else 1)
