' Silent startup for C Helper - no console window
' Double-click to run in background

Set WshShell = WScript.CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

Dim ProjectPath
ProjectPath = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ProjectPath

If Not FSO.FileExists(".venv\Scripts\pythonw.exe") Then
    WshShell.Run "cmd /c uv venv", 0, True
    WshShell.Run "cmd /c .venv\Scripts\activate.bat && uv pip install -e .", 0, True
End If

Dim cmd
cmd = "cmd /c .venv\Scripts\pythonw.exe -m c_helper.main 2>> runtime.log"
WshShell.Run cmd, 0, False
