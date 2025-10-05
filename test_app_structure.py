#!/usr/bin/env python3
"""
Test script to validate the voice chart app structure
"""

import ast
import sys

def test_app_structure():
    """Test if the voice chart app has the correct structure"""
    try:
        with open('voice_chart_app.py', 'r') as f:
            source = f.read()
        
        # Parse the Python code
        tree = ast.parse(source)
        
        # Check if VoiceEnabledChartApp class exists
        class_found = False
        methods_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'VoiceEnabledChartApp':
                class_found = True
                print("✅ VoiceEnabledChartApp class found")
                
                # Check for key methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods_found.append(item.name)
                
                break
        
        if not class_found:
            print("❌ VoiceEnabledChartApp class not found")
            return False
        
        # Check for essential methods
        essential_methods = [
            '__init__', 'setup_ui', 'start_session', 'end_session',
            'process_request', 'render_chart', 'speak', 'listen_loop'
        ]
        
        missing_methods = []
        for method in essential_methods:
            if method not in methods_found:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing essential methods: {missing_methods}")
            return False
        else:
            print("✅ All essential methods found")
        
        # Check for helper functions
        helper_functions = ['parse_color', 'get_vibrant_colors', 'generate_random_data']
        functions_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in helper_functions:
                functions_found.append(node.name)
        
        if len(functions_found) == len(helper_functions):
            print("✅ All helper functions found")
        else:
            missing_helpers = set(helper_functions) - set(functions_found)
            print(f"⚠️  Missing helper functions: {missing_helpers}")
        
        # Check for main execution block
        has_main = False
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                if (isinstance(node.test.left, ast.Name) and 
                    node.test.left.id == '__name__' and
                    isinstance(node.test.comparators[0], ast.Constant) and
                    node.test.comparators[0].value == '__main__'):
                    has_main = True
                    break
        
        if has_main:
            print("✅ Main execution block found")
        else:
            print("❌ Main execution block not found")
            return False
        
        print("\n🎉 Application structure validation passed!")
        print(f"📊 Total methods in VoiceEnabledChartApp: {len(methods_found)}")
        print(f"🔧 Helper functions: {len(functions_found)}")
        
        return True
        
    except FileNotFoundError:
        print("❌ voice_chart_app.py not found")
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error in voice_chart_app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing app structure: {e}")
        return False

def test_requirements():
    """Test if requirements.txt exists and has necessary packages"""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        required_packages = [
            'matplotlib', 'numpy', 'pandas', 'scikit-learn',
            'SpeechRecognition', 'pyttsx3', 'tkinter'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️  Missing packages in requirements.txt: {missing_packages}")
        else:
            print("✅ All required packages in requirements.txt")
        
        return len(missing_packages) == 0
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def test_readme():
    """Test if README.md exists and has essential sections"""
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        
        essential_sections = [
            'Voice Enabled Chart Creation',
            'Features', 'Installation', 'How to Use',
            'Example Voice Commands', 'Chart Types Available'
        ]
        
        missing_sections = []
        for section in essential_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  Missing sections in README.md: {missing_sections}")
        else:
            print("✅ All essential sections in README.md")
        
        return len(missing_sections) == 0
        
    except FileNotFoundError:
        print("❌ README.md not found")
        return False

if __name__ == "__main__":
    print("🧪 Testing Voice Chart App Structure\n")
    
    tests = [
        ("App Structure", test_app_structure),
        ("Requirements", test_requirements),
        ("README", test_readme)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\n📝 To run the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the app: python voice_chart_app.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")