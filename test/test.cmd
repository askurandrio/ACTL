set temp=%PYTHONPATH%
set PYTHONPATH=%PYTHONPATH%;..\source\library
python ..\source\main.py .\test_case\example.a

set PYTHONPATH=%temp%
