#!/bin/bash

# AI Crypto Trading Agent - Quick Setup Script
# Based on DeepSeek's Alpha Arena winning strategy

echo "🚀 AI Crypto Trading Agent - Setup"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ Pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created (please edit with your API keys)"
else
    echo "✓ .env file already exists"
fi
echo ""

# ASCII Art
echo "   _____ _______       _____ _______ _____ _   _  _____ "
echo "  / ____|__   __|/\   |  __ \__   __|_   _| \ | |/ ____|"
echo " | (___    | |  /  \  | |__) | | |    | | |  \| | |  __ "
echo "  \___ \   | | / /\ \ |  _  /  | |    | | | . \` | | |_ |"
echo "  ____) |  | |/ ____ \| | \ \  | |   _| |_| |\  | |__| |"
echo " |_____/   |_/_/    \_\_|  \_\ |_|  |_____|_| \_|\_____|"
echo ""
echo "===================================="
echo "🎉 Setup Complete!"
echo "===================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Get your DeepSeek API key:"
echo "   → Visit: https://platform.deepseek.com"
echo "   → Sign up and create an API key"
echo ""
echo "2. Edit the .env file:"
echo "   → Open .env in a text editor"
echo "   → Add your DEEPSEEK_API_KEY"
echo ""
echo "3. Run the application:"
echo "   → streamlit run app.py"
echo ""
echo "4. Access the dashboard:"
echo "   → Open http://localhost:8501 in your browser"
echo ""
echo "===================================="
echo "💡 Pro Tips:"
echo ""
echo "• Start with paper trading (virtual money)"
echo "• Read STRATEGY_GUIDE.md for winning strategies"
echo "• Begin with 2-3x leverage, not maximum"
echo "• Set stop losses on EVERY trade"
echo "• Only trade BTC/ETH until you're confident"
echo ""
echo "===================================="
echo "🏆 DeepSeek's Alpha Arena Results:"
echo ""
echo "• Started: \$10,000"
echo "• Ended: \$13,830 (38.3% profit)"
echo "• Time: 72 hours"
echo "• Peak: 125% profit mid-competition"
echo ""
echo "Your goal: Beat DeepSeek! 🚀"
echo "===================================="
echo ""
echo "⚠️  IMPORTANT DISCLAIMER:"
echo ""
echo "This is PAPER TRADING only (virtual money)."
echo "Real crypto trading involves significant risk."
echo "Only trade with real money if you:"
echo "  • Fully understand the risks"
echo "  • Can afford to lose 100% of capital"
echo "  • Have practiced successfully in paper trading"
echo "  • Consulted with financial advisors"
echo ""
echo "This is NOT financial advice!"
echo "===================================="
echo ""
echo "Ready to start? Run: streamlit run app.py"
echo ""