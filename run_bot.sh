#!/bin/bash
echo "Останавливаем все предыдущие процессы..."
pkill -f python 2>/dev/null || true
sleep 2
echo "Запускаем бота..."
cd /workspaces/buhoy-bot
python -m src.main 2>&1
