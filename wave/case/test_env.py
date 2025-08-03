"""Test script to verify the VSCode environment setup"""
from build123d import *
from models.switch import KailhChoc
from models.xiao import SeeedXiaoBLE

print("Virtual environment and imports are working correctly!")

# Test creating a simple part
with BuildPart() as part:
    Box(10, 10, 10)
    print("Successfully created a 3D part")

print("Environment test complete. You're ready to develop in VSCode!")
