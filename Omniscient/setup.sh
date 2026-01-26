#!/bin/bash

echo "=========================================="
echo "🎯 Omniscient OKR Analytics Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✓ .env file already exists"
else
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your MySQL credentials"
    echo ""
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your MySQL credentials"
echo "  2. Test connection: python3 test_connection.py"
echo "  3. Generate report: python3 gather_okr_metrics.py"
echo ""
