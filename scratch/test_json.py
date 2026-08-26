import json

text = "सुनीता चौधरी"
text_json = json.dumps(text)
error_json = json.dumps("")

print(f"if (window.API && window.API.handleDictationResult) {{ window.API.handleDictationResult('test', {text_json}, {error_json}); }}")
