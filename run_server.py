#!/usr/bin/env python3
"""
Simple server runner with error handling
"""
import sys
import traceback

try:
    print("=" * 60)
    print("🚀 SATO AI Fashion Chatbot - Starting Server")
    print("=" * 60)
    
    from api_server import app
    import os
    
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("\n✅ Modules loaded successfully")
    print("✅ Folders created")
    print("\n" + "=" * 60)
    print("🌐 Server starting on:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")
    print("=" * 60)
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    
    # Start the server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
    
except KeyboardInterrupt:
    print("\n\n⚠️  Server stopped by user")
    sys.exit(0)
    
except Exception as e:
    print("\n\n" + "=" * 60)
    print("❌ ERROR STARTING SERVER")
    print("=" * 60)
    print(f"\nError: {e}\n")
    print("Full traceback:")
    traceback.print_exc()
    print("\n" + "=" * 60)
    sys.exit(1)
