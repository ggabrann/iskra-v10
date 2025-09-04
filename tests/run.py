from iskra.engine import run_step
def main():
    r = run_step("iskra_core", "тест")
    assert r["ok"]
    print("All tests passed.")
if __name__ == "__main__":
    main()
