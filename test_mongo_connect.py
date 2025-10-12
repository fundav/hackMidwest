import os
import sys
import ssl
import platform
import certifi
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')

print('--- Environment info ---')
print('Python:', sys.version.replace('\n',' '))
print('Platform:', platform.platform())
print('OpenSSL version:', ssl.OPENSSL_VERSION)
try:
    import pymongo
    print('pymongo version:', pymongo.version)
except Exception as e:
    print('pymongo not installed or import failed:', e)

print('\n--- certifi CA bundle path ---')
print(certifi.where())

if not MONGODB_URI:
    print('\nMONGODB_URI not set in .env. Aborting connectivity test.')
    sys.exit(1)

print('\n--- Attempting MongoDB connection (ping) ---')
try:
    from pymongo import MongoClient
    # Use TLS/SSL CA via certifi
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
    # Issue a ping to force server selection / TLS handshake
    res = client.admin.command('ping')
    print('Ping response:', res)
    print('Server info:', client.server_info())
    client.close()
except Exception as e:
    print('Connection failed. Detailed exception:')
    try:
        import traceback
        traceback.print_exc()
    except Exception:
        print(str(e))
    # Helpful hints
    print('\n--- Hints ---')
    print('1) If you are using MongoDB Atlas, ensure your current public IP is in the Atlas IP Access List.')
    print("2) Ensure the username/password in MONGODB_URI are correct. If password has special characters like '#', URL-encode them.")
    print('3) Ensure you have an up-to-date OpenSSL and pymongo package. Consider: pip install --upgrade pymongo certifi')
    print('4) If TLS issues persist, try specifying the CA bundle (we already used certifi).')
    print('5) If behind a corporate VPN/proxy, that can interfere with TLS handshakes.')
    sys.exit(2)

print('\nConnectivity test completed successfully.')
