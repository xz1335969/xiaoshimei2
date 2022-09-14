import json
with open(__file__.strip("custom_command.py") + "custom_command\\customization.json", "r") as f:
    json_code = f.read()
    json_code = json.loads(json_code)
    questions = json_code["questions"]
    question = '测试消息'
    print("测试问题：\n\n")
    print(questions)
    print(question)
    print(question in questions)
    print("测试完成\n\n")