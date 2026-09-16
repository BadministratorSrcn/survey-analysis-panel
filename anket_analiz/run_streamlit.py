# -*- coding: utf-8 -*-
"""Streamlit başlatıcı — Windows'ta dayanıklı event loop seçimi.

Windows ProactorEventLoop, istemci bağlantısı aniden koparsa accept aşamasında
'OSError: [WinError 64]' ile sunucuyu çökertebilir. SelectorEventLoop bu sorunu
yaşamaz; yerel panel kullanımı için tercih edilir.

Kullanım:  python anket_analiz/run_streamlit.py [port]
"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from streamlit.web import cli as stcli  # noqa: E402

PORT = sys.argv[1] if len(sys.argv) > 1 else "8501"

if __name__ == "__main__":
    sys.argv = [
        "streamlit", "run", "anket_analiz/app.py",
        "--server.port", PORT,
        "--server.headless", "true",
    ]
    sys.exit(stcli.main())
