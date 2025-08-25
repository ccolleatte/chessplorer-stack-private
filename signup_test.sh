#!/bin/bash
echo "=== Test via curl ==="
curl -s -X POST https://supabase.chessplorer.com/auth/v1/signup \
  -H "apikey: $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@example.com","password":"secret123"}' \
  | jq .

echo
echo "=== Test via memo_test.py ==="
python3 memo_test.py
