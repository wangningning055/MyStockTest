import traceback
import uvicorn

from src.main_code.FastCore import app


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    try:
        main()

    except Exception:

        print("\n===== 程序崩溃 =====\n")

        traceback.print_exc()

        input("\n按回车退出...")