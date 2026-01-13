#!/bin/bash
# Run both main application and admin panel

echo "Starting both applications..."

# Start main app in background
python main.py &
MAIN_PID=$!

# Wait a bit
sleep 2

# Start admin panel
python admin_app.py &
ADMIN_PID=$!

echo "Main Application PID: $MAIN_PID"
echo "Admin Panel PID: $ADMIN_PID"
echo ""
echo "Main Application: http://localhost:8000"
echo "Admin Panel: http://localhost:8001"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both applications"

# Wait for interrupt
wait
